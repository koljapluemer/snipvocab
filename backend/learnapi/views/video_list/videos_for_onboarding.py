from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.models import Video, Tag
import random
import logging

logger = logging.getLogger(__name__)

class VideosForOnboardingView(APIView):
    def get(self, request):
        try:
            # Get the 'feature-in-onboarding' tag
            onboarding_tag = Tag.objects.get(name='feature-in-onboarding')
            
            # Get all videos with this tag and only the fields we need
            videos = Video.objects.filter(tags=onboarding_tag).values('youtube_id', 'youtube_title')
            logger.info(f"Found videos for onboarding: {list(videos)}")  # Debug log
            
            # If we have less than 3 videos, return all of them
            if len(videos) <= 3:
                selected_videos = list(videos)
            else:
                # Randomly select 3 videos
                selected_videos = random.sample(list(videos), 3)
            
            logger.info(f"Returning selected videos: {selected_videos}")  # Debug log
            return Response(selected_videos, status=status.HTTP_200_OK)
            
        except Tag.DoesNotExist:
            return Response(
                {'error': 'Onboarding tag not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
