from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from shared.models import Video, Snippet, Word, VideoStatus
from .models import VocabPractice, SnippetPractice
from django.contrib.auth.models import User
from fsrs import Scheduler, Card, Rating, State
from datetime import datetime, timezone
import logging
import re
from difflib import SequenceMatcher
from rest_framework.permissions import IsAuthenticated
import traceback

logger = logging.getLogger(__name__)

def normalize_meaning(meaning: str) -> str:
    """Normalize a meaning by removing parentheses and converting to lowercase."""
    # Remove everything in parentheses
    meaning = re.sub(r'\([^)]*\)', '', meaning)
    # Remove extra whitespace and convert to lowercase
    return meaning.strip().lower()

def are_meanings_similar(meaning1: str, meaning2: str) -> bool:
    """Check if two meanings are similar based on the given criteria."""
    # Get normalized versions
    norm1 = normalize_meaning(meaning1)
    norm2 = normalize_meaning(meaning2)
    
    # If they're exactly the same after normalization, they're duplicates
    if norm1 == norm2:
        return True
        
    # If they differ by only one character (Levenshtein distance of 1)
    if len(norm1) == len(norm2):
        differences = sum(1 for a, b in zip(norm1, norm2) if a != b)
        if differences <= 1:
            return True
            
    # If they're very similar (90% or more)
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    if similarity >= 0.9:
        return True
        
    return False

def deduplicate_meanings(meanings: list) -> list:
    """Remove duplicate meanings based on similarity criteria."""
    unique_meanings = []
    for meaning in meanings:
        # Check if this meaning is similar to any we've already added
        if not any(are_meanings_similar(meaning, existing) for existing in unique_meanings):
            unique_meanings.append(meaning)
    return unique_meanings

class VideoListView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        logger.info("Fetching all live videos")
        videos = Video.objects.filter(status=VideoStatus.LIVE).values_list('youtube_id', flat=True)
        logger.info(f"Found {videos.count()} live videos")
        return Response(list(videos))

class VideoSnippetsView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        try:
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippets = Snippet.objects.filter(video=video).order_by('index')
            
            # Transform Django snippets to match frontend interface
            transformed_snippets = [
                {
                    'startTime': snippet.start_time,
                    'endTime': snippet.end_time,
                    'videoId': video.youtube_id,
                    'index': snippet.index
                }
                for snippet in snippets
            ]
            
            return Response(transformed_snippets)
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")

class SnippetDetailsView(generics.RetrieveAPIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        index = self.kwargs.get('index')
        
        try:
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippet = Snippet.objects.get(video=video, index=index)
            
            # Get all words associated with this snippet
            words = Word.objects.filter(occurs_in_snippets=snippet)
            
            # Transform words to match frontend interface
            transformed_words = []
            for word in words:
                # Get all meanings for this word
                meanings = [meaning.en for meaning in word.meanings.all()]
                # Deduplicate meanings
                unique_meanings = deduplicate_meanings(meanings)
                # Create word object with deduplicated meanings
                transformed_words.append({
                    'originalWord': word.original_word,
                    'meanings': [{'en': meaning} for meaning in unique_meanings]
                })
            
            # Transform snippet to match frontend interface
            response_data = {
                'startTime': snippet.start_time,
                'endTime': snippet.end_time,
                'videoId': video.youtube_id,
                'index': snippet.index,
                'words': transformed_words
            }
            
            return Response(response_data)
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")
        except Snippet.DoesNotExist:
            raise NotFound(f"Snippet with index {index} not found for video {youtube_id}")

class SnippetDueWordsView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        index = self.kwargs.get('index')
        
        logger.info(f"Fetching due words for video {youtube_id}, snippet {index}, user {request.user.id}")
        
        try:
            # Get the video and snippet
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippet = Snippet.objects.get(video=video, index=index)
            
            # Get all words associated with this snippet
            words = Word.objects.filter(occurs_in_snippets=snippet)
            logger.debug(f"Found {words.count()} words in snippet")
            
            # Transform words to match frontend interface
            transformed_words = []
            for word in words:
                try:
                    # Get all meanings for this word and deduplicate them
                    meanings = [meaning.en for meaning in word.meanings.all()]
                    unique_meanings = deduplicate_meanings(meanings)
                    
                    # Try to get existing practice
                    try:
                        vocab_practice = VocabPractice.objects.get(user=request.user, word=word)
                        # If practice exists and is due, add to response
                        if vocab_practice.is_due:
                            transformed_words.append({
                                'originalWord': word.original_word,
                                'meanings': [{'en': meaning} for meaning in unique_meanings],
                                'isDue': True,
                                'isNew': False,
                                'isFavorite': vocab_practice.is_favorite,
                                'isBlacklisted': vocab_practice.is_blacklisted
                            })
                    except VocabPractice.DoesNotExist:
                        # No practice exists for this word - it's new and due
                        transformed_words.append({
                            'originalWord': word.original_word,
                            'meanings': [{'en': meaning} for meaning in unique_meanings],
                            'isDue': True,
                            'isNew': True,
                            'isFavorite': False,
                            'isBlacklisted': False
                        })
                except Exception as e:
                    logger.error(f"Error processing word {word.original_word}: {str(e)}")
                    continue
            
            logger.info(f"Returning {len(transformed_words)} due words")
            return Response(transformed_words)
            
        except Video.DoesNotExist:
            logger.warning(f"Video {youtube_id} not found or not live")
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")
        except Snippet.DoesNotExist:
            logger.warning(f"Snippet {index} not found for video {youtube_id}")
            raise NotFound(f"Snippet with index {index} not found for video {youtube_id}")
        except Exception as e:
            logger.error(f"Unexpected error in SnippetDueWordsView: {str(e)}")
            raise

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

class SnippetPracticeView(generics.GenericAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        index = self.kwargs.get('index')
        
        try:
            # Get the video and snippet
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippet = Snippet.objects.get(video=video, index=index)
            
            # Get or create the practice
            practice, created = SnippetPractice.objects.get_or_create(
                user=request.user,
                snippet=snippet,
                defaults={'perceived_difficulty': None}
            )
            
            return Response({
                'perceived_difficulty': practice.perceived_difficulty,
                'updated': practice.updated
            })
            
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")
        except Snippet.DoesNotExist:
            raise NotFound(f"Snippet with index {index} not found for video {youtube_id}")
    
    def post(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        index = self.kwargs.get('index')
        perceived_difficulty = request.data.get('perceived_difficulty')
        
        try:
            # Get the video and snippet
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippet = Snippet.objects.get(video=video, index=index)
            
            # Get or create the practice
            practice, created = SnippetPractice.objects.get_or_create(
                user=request.user,
                snippet=snippet,
                defaults={'perceived_difficulty': perceived_difficulty}
            )
            
            # Update if it already exists
            if not created and perceived_difficulty is not None:
                practice.perceived_difficulty = perceived_difficulty
                practice.save()
            
            return Response({
                'perceived_difficulty': practice.perceived_difficulty,
                'updated': practice.updated
            })
            
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")
        except Snippet.DoesNotExist:
            raise NotFound(f"Snippet with index {index} not found for video {youtube_id}")

class VideoEnrichedSnippetsView(generics.GenericAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        
        try:
            # Get the video
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            
            # Get all snippets for this video
            snippets = Snippet.objects.filter(video=video).order_by('index')
            
            # Transform snippets to match frontend interface
            enriched_snippets = []
            for snippet in snippets:
                # Get all words associated with this snippet
                words = Word.objects.filter(occurs_in_snippets=snippet)
                
                # Transform words to match frontend interface
                transformed_words = []
                for word in words:
                    # Get all meanings for this word
                    meanings = [meaning.en for meaning in word.meanings.all()]
                    # Deduplicate meanings
                    unique_meanings = deduplicate_meanings(meanings)
                    # Create word object with deduplicated meanings
                    transformed_words.append({
                        'originalWord': word.original_word,
                        'meanings': [{'en': meaning} for meaning in unique_meanings]
                    })
                
                # Get practice data if it exists
                try:
                    practice = SnippetPractice.objects.get(user=request.user, snippet=snippet)
                    perceived_difficulty = practice.perceived_difficulty
                    last_updated = practice.updated
                except SnippetPractice.DoesNotExist:
                    perceived_difficulty = None
                    last_updated = None
                
                # Create enriched snippet details
                enriched_snippet = {
                    'startTime': snippet.start_time,
                    'endTime': snippet.end_time,
                    'videoId': video.youtube_id,
                    'index': snippet.index,
                    'words': transformed_words,
                    'perceivedDifficulty': perceived_difficulty,
                    'lastUpdated': last_updated.isoformat() if last_updated else None
                }
                
                enriched_snippets.append(enriched_snippet)
            
            return Response(enriched_snippets)
            
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")

