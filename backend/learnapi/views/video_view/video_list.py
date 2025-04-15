from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.models import Video, VideoStatus

import logging
logger = logging.getLogger(__name__)    

class VideoListView(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        logger.info("Fetching all live videos")
        videos = Video.objects.filter(status=VideoStatus.LIVE).values('youtube_id', 'youtube_title')
        logger.info(f"Found {videos.count()} live videos")
        return Response(list(videos))

