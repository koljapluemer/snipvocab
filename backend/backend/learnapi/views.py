from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .models import Video, Language
from .serializers import VideoSerializer
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
