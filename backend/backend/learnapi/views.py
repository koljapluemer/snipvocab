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
                    'start_time': snippet.start_time,
                    'end_time': snippet.end_time,
                    'video_id': video.youtube_id,
                    'index': snippet.index
                }
                for snippet in snippets
            ]
            
            return Response(transformed_snippets)
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")

