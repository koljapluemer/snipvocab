from django.db.models import Q
from shared.models import Video
from frontend.models import SearchQuery
from django.utils import timezone

def get_videos_for_search(search_term=None):
    """
    Search videos by title, channel, tags, or comments.
    Returns a tuple of (videos_queryset, total_count)
    """
    if not search_term:
        videos = Video.objects.filter(status='live').order_by('-added_at')
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
        status='live'
    ).distinct().order_by('-added_at')

    total_count = videos.count()
    return videos, total_count
