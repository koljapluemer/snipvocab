from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from shared.models import Video, Snippet, Word, VideoStatus
from .models import VocabPractice
from django.contrib.auth.models import User
from fsrs import Scheduler, Card, Rating
from datetime import datetime, timezone
import logging
import re
from difflib import SequenceMatcher
from rest_framework.permissions import IsAuthenticated

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
                        if vocab_practice.due and vocab_practice.due <= datetime.now(timezone.utc):
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

