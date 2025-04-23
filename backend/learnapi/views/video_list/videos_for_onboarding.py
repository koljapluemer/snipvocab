from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shared.models import Video, Tag
import random

class VideosForOnboardingView(APIView):
    def get(self, request):
        try:
            # Get the 'feature-in-onboarding' tag
            onboarding_tag = Tag.objects.get(name='feature-in-onboarding')
            
            # Get all videos with this tag
            videos = Video.objects.filter(tags=onboarding_tag)
            
            # If we have less than 3 videos, return all of them
            if videos.count() <= 3:
                selected_videos = list(videos)
            else:
                # Randomly select 3 videos
                selected_videos = random.sample(list(videos), 3)
            
            # Serialize the videos
            video_data = [{
                'youtube_id': video.youtube_id,
                'title': video.youtube_title,
                'channel_name': video.channel_name,
                'video_views': video.video_views,
                'video_likes': video.video_likes
            } for video in selected_videos]
            
            return Response(video_data, status=status.HTTP_200_OK)
            
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
