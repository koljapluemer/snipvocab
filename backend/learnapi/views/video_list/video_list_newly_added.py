from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from shared.models import Video, VideoStatus

import logging
logger = logging.getLogger(__name__)    

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 4

class VideoListNewlyAddedView(APIView):
    renderer_classes = [JSONRenderer]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request, *args, **kwargs):
        logger.info("Fetching all live videos sorted by added_at")
        videos = Video.objects.filter(
            status=VideoStatus.LIVE
        ).order_by('-added_at')[:50].values('youtube_id', 'youtube_title')
        
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(videos, request)
        
        logger.info(f"Found {videos.count()} live videos")
        return paginator.get_paginated_response(list(result_page))
