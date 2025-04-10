from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from shared.models import Video, Language, Snippet, Word, VideoStatus
import logging

logger = logging.getLogger(__name__)

class VideoListView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        logger.info("Fetching all live videos")
        videos = Video.objects.filter(status=VideoStatus.LIVE).values_list('youtube_id', flat=True)
        logger.info(f"Found {videos.count()} live videos")
        return Response(list(videos))

