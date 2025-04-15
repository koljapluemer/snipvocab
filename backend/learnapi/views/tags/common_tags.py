from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.models import Tag, Video, VideoStatus
import random
import logging
from django.db import models

logger = logging.getLogger(__name__)

class RandomCommonTagView(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        logger.info("Fetching random tag from top 20 most used tags")
        
        # Get top 20 tags by number of associated live videos
        top_tags = Tag.objects.annotate(
            video_count=models.Count(
                'videos',
                filter=models.Q(videos__status=VideoStatus.LIVE)
            )
        ).order_by('-video_count')[:20]
        
        if not top_tags:
            logger.warning("No tags found")
            return Response("", status=404)
        
        # Select a random tag from the top 20
        random_tag = random.choice(top_tags)
        
        logger.info(f"Selected random tag: {random_tag.name}")
        return Response(random_tag.name)
