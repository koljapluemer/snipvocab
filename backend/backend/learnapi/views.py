from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from shared.models import Video, Language, Snippet, Word
from .serializers import VideoSerializer, SnippetSerializer, WordSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class VideoListView(generics.ListAPIView):
    serializer_class = VideoSerializer
    renderer_classes = [JSONRenderer]
    
    def get_queryset(self):
        language_code = self.kwargs.get('language_code')
        logger.info(f"Fetching videos for language code: {language_code}")
        try:
            language = Language.objects.get(code=language_code)
            logger.info(f"Found language: {language}")
            videos = Video.objects.filter(language=language, is_blacklisted=False)
            logger.info(f"Found {videos.count()} videos")
            return videos
        except Language.DoesNotExist:
            logger.warning(f"Language with code {language_code} not found")
            return Video.objects.none()

class VideoSnippetsView(generics.ListAPIView):
    serializer_class = SnippetSerializer
    renderer_classes = [JSONRenderer]
    
    def get_queryset(self):
        youtube_id = self.kwargs.get('youtube_id')
        try:
            video = Video.objects.get(youtube_id=youtube_id)
            return Snippet.objects.filter(video=video).order_by('index')
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found")

class SnippetWordsView(generics.ListAPIView):
    serializer_class = WordSerializer
    renderer_classes = [JSONRenderer]
    
    def get_queryset(self):
        youtube_id = self.kwargs.get('youtube_id')
        snippet_index = self.kwargs.get('snippet_index')
        try:
            video = Video.objects.get(youtube_id=youtube_id)
            snippet = Snippet.objects.get(video=video, index=snippet_index)
            return Word.objects.filter(occurs_in_snippets=snippet)
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found")
        except Snippet.DoesNotExist:
            raise NotFound(f"Snippet with index {snippet_index} not found in video {youtube_id}")
