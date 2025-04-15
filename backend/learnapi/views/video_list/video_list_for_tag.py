from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from shared.models import Video, VideoStatus, Tag

import logging
logger = logging.getLogger(__name__)    

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 4

class VideoListForTagView(APIView):
    renderer_classes = [JSONRenderer]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request, tag_name, *args, **kwargs):
        logger.info(f"Fetching videos for tag: {tag_name}")
        
        # Get the tag object
        try:
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist:
            logger.warning(f"Tag not found: {tag_name}")
            return Response({"error": "Tag not found"}, status=404)
        
        # Filter videos by tag and status
        videos = Video.objects.filter(
            tags=tag,
            status=VideoStatus.LIVE
        ).values('youtube_id', 'youtube_title')
        
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(videos, request)
        
        logger.info(f"Found {videos.count()} live videos for tag: {tag_name}")
        return paginator.get_paginated_response(list(result_page))
