from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from shared.models import Video, VideoStatus
import logging
import re
from difflib import SequenceMatcher

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

