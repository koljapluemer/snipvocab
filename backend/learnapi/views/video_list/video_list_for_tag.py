from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from shared.models import Video, VideoStatus, Tag, Frontend

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
        # Get language from query params, default to Arabic if not specified
        language = request.query_params.get('lang', 'ar').lower()
        
        # Map language codes to Frontend values
        language_map = {
            'de': Frontend.GERMAN,
            'ar': Frontend.ARABIC
        }
        
        if language not in language_map:
            logger.warning(f"Invalid language requested: {language}")
            return Response(
                {"error": f"Invalid language. Must be one of: {', '.join(language_map.keys())}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        frontend = language_map[language]
        
        logger.info(f"Fetching videos for tag: {tag_name} and language: {language}")
        
        # Get the tag object
        try:
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist:
            logger.warning(f"Tag not found: {tag_name}")
            return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Filter videos by tag, status, and language
        videos = Video.objects.filter(
            tags=tag,
            status=VideoStatus.LIVE,
            frontend=frontend
        ).values('youtube_id', 'youtube_title')
        
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(videos, request)
        
        logger.info(f"Found {videos.count()} live videos for tag: {tag_name} and language: {language}")
        return paginator.get_paginated_response(list(result_page))
