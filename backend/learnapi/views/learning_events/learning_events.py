from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from fsrs import Scheduler, Card, Rating, State
from datetime import datetime, timezone
import logging
from rest_framework.permissions import IsAuthenticated
import traceback

from learnapi.models import VocabPractice
from shared.models import Word

logger = logging.getLogger(__name__)


class LearningEventsView(generics.CreateAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        learning_events = request.data
        logger.info(f"Received {len(learning_events)} learning events for user {request.user.id}")
        
        if not isinstance(learning_events, list):
            logger.error("Invalid request: learning_events must be a list")
            return Response({"error": "learning_events must be a list"}, status=400)
            
        scheduler = Scheduler()
        results = []
        
        for event in learning_events:
            try:
                # Convert frontend LearningEventType to FSRS Rating
                # Rating.Again (==1) forgot the card
                # Rating.Hard (==2) remembered the card with serious difficulty
                # Rating.Good (==3) remembered the card after a hesitation
                # Rating.Easy (==4) remembered the card easily
                event_type = event.get('eventType')
                rating_map = {
                    'AGAIN': Rating.Again,
                    'HARD': Rating.Hard,
                    'GOOD': Rating.Good,
                    'EASY': Rating.Easy
                }
                
                if event_type not in rating_map:
                    logger.error(f"Invalid event type: {event_type}")
                    continue
                    
                rating = rating_map[event_type]
                
                original_word = event.get('originalWord')
                if not original_word:
                    logger.error("Missing originalWord in learning event")
                    continue
                    
                # Get or create the word
                try:
                    word = Word.objects.get(original_word=original_word)
                except Word.DoesNotExist:
                    logger.error(f"Word not found: {original_word}")
                    continue
                    
                # Get or create the vocab practice
                vocab_practice, created = VocabPractice.objects.get_or_create(
                    user=request.user,
                    word=word,
                    defaults={
                        'state': 'Learning',
                        'last_review': datetime.fromtimestamp(event.get('timestamp', 0) / 1000, timezone.utc)
                    }
                )
                
                # Create FSRS card from existing practice or new card
                if created:
                    card = Card()
                    vocab_practice.state = card.state.name if card.state else "Learning"
                    vocab_practice.step = card.step
                    vocab_practice.stability = card.stability
                    vocab_practice.difficulty = card.difficulty
                    vocab_practice.due = card.due
                    vocab_practice.last_review = card.last_review
                    vocab_practice.save()
                    logger.info(f"Created new card for word {original_word}")
                else:
                    # Create card from existing practice data
                    state_map = {
                        'Learning': State.Learning,
                        'Review': State.Review,
                        'Relearning': State.Relearning
                    }
                    card = Card(
                        state=state_map.get(vocab_practice.state, State.Learning),
                        step=vocab_practice.step,
                        stability=vocab_practice.stability,
                        difficulty=vocab_practice.difficulty,
                        due=vocab_practice.due,
                        last_review=vocab_practice.last_review
                    )
                    logger.info(f"Loaded existing card for word {original_word} with state {card.state}, step {card.step}, stability {card.stability}, difficulty {card.difficulty}")
                
                # Review the card with FSRS
                try:
                    logger.debug(f"Reviewing card for word {original_word} with state {card.state}, step {card.step}, stability {card.stability}, difficulty {card.difficulty}")
                    card, review_log = scheduler.review_card(card, rating)
                    logger.debug(f"Card review successful. New state: {card.state}, new due date: {card.due}")
                except Exception as e:
                    logger.error(f"Error reviewing card for word {original_word}: {str(e)}")
                    # If the review fails, we'll still save the card with its current state
                    review_log = None
                
                # Update the vocab practice with new FSRS values
                vocab_practice.state = card.state.name if card.state else "Learning"
                vocab_practice.step = card.step
                vocab_practice.stability = card.stability
                vocab_practice.difficulty = card.difficulty
                vocab_practice.due = card.due
                # Immediately re-practice wrong answers
                if rating == Rating.Again:
                    vocab_practice.due = datetime.now(timezone.utc)
                if review_log:
                    vocab_practice.last_review = review_log.review_datetime
                vocab_practice.save()
                
                results.append({
                    'originalWord': original_word,
                    'success': True,
                    'newDueDate': card.due.isoformat() if card.due else None
                })
                
                logger.info(f"Processed learning event for word {original_word} with rating {rating}")
                
            except Exception as e:
                logger.error(f"Error processing learning event for word '{event.get('originalWord')}':")
                logger.error(traceback.format_exc())
                results.append({
                    'originalWord': event.get('originalWord'),
                    'success': False,
                    'error': f"Error processing learning event: {str(e)}"
                })
        
        return Response(results)
