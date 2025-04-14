from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from learnapi.models import VideoProgress
from shared.models import Video, VideoStatus
import logging
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

logger = logging.getLogger(__name__)

class VideoProgressView(generics.GenericAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        
        try:
            # Get the video
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            
            # Try to get the video progress
            try:
                progress = VideoProgress.objects.get(user=request.user, video=video)
                return Response({
                    'lastWatched': progress.last_watched.isoformat(),
                    'perceivedDifficulty': progress.perceived_difficulty,
                    'snippetPercentageWatched': progress.snippet_percentage_watched
                })
            except VideoProgress.DoesNotExist:
                # Return null values if no progress exists
                return Response({
                    'lastWatched': None,
                    'perceivedDifficulty': None,
                    'snippetPercentageWatched': None
                })
            
        except Video.DoesNotExist:
            logger.warning(f"Video {youtube_id} not found or not live")
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")

    def post(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        
        try:
            # Get the video
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            
            # Get the data from the request
            perceived_difficulty = request.data.get('perceivedDifficulty')
            snippet_percentage_watched = request.data.get('snippetPercentageWatched')
            
            # Validate the data
            if perceived_difficulty is not None and not isinstance(perceived_difficulty, int):
                return Response({'error': 'perceivedDifficulty must be an integer'}, status=400)
            
            if snippet_percentage_watched is not None and not isinstance(snippet_percentage_watched, (int, float)):
                return Response({'error': 'snippetPercentageWatched must be a number'}, status=400)
            
            # Get or create the video progress
            progress, created = VideoProgress.objects.get_or_create(
                user=request.user,
                video=video,
                defaults={
                    'perceived_difficulty': perceived_difficulty,
                    'snippet_percentage_watched': snippet_percentage_watched,
                    'last_watched': timezone.now()
                }
            )
            
            # Update if it already exists
            if not created:
                if perceived_difficulty is not None:
                    progress.perceived_difficulty = perceived_difficulty
                if snippet_percentage_watched is not None:
                    progress.snippet_percentage_watched = snippet_percentage_watched
                progress.last_watched = timezone.now()
                progress.save()
            
            return Response({
                'lastWatched': progress.last_watched.isoformat(),
                'perceivedDifficulty': progress.perceived_difficulty,
                'snippetPercentageWatched': progress.snippet_percentage_watched
            })
            
        except Video.DoesNotExist:
            logger.warning(f"Video {youtube_id} not found or not live")
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live") 