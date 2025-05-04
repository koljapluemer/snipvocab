from django.db.models import Q
from shared.models import Video
from frontend.models import SearchQuery
from django.utils import timezone
from django.conf import settings

def get_videos_for_search(search_term=None):
    """
    Search videos by title, channel, tags, or comments.
    Returns a tuple of (videos_queryset, total_count)
    """
    # Get the current frontend language
    language_code = getattr(settings, 'LANGUAGE_TO_LEARN', 'de')
    frontend_value = language_code  # 'de' or 'ar'

    if not search_term:
        videos = Video.objects.filter(
            status='live',
            frontend=frontend_value
        ).order_by('-added_at')
        return videos, videos.count()

    # Create search query record
    search_query, created = SearchQuery.objects.get_or_create(term=search_term)
    search_query.count += 1
    search_query.save()

    # Build search query
    search_query_obj = Q()
    for term in search_term.split():
        search_query_obj |= (
            Q(youtube_title__icontains=term) |
            Q(channel_name__icontains=term) |
            Q(comment__icontains=term) |
            Q(tags__name__icontains=term)
        )

    videos = Video.objects.filter(
        search_query_obj,
        status='live',
        frontend=frontend_value
    ).distinct().order_by('-added_at')

    total_count = videos.count()
    return videos, total_count
