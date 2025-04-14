from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from learnapi.models import SnippetPractice
from shared.models import Video, Snippet, VideoStatus
import logging
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


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