from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from learnapi.models import VideoProgress
from shared.models import Video, VideoStatus
import logging
from rest_framework.permissions import IsAuthenticated

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