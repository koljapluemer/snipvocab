from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from youtube_transcript_api import YouTubeTranscriptApi

from shared.models import Video, VideoStatus
from .get_current_frontend import get_current_frontend


@staff_member_required
def video_details(request, youtube_id):
    """View to show details of a specific video"""
    frontend = get_current_frontend(request)
    try:
        video = Video.objects.select_related().prefetch_related(
            'tags',
            'snippets',
            'words',
            'words__meanings',
            'words__occurs_in_snippets'
        ).get(youtube_id=youtube_id, frontend=frontend)
        
        # Get available languages if not already set
        if not video.available_subtitle_languages:
            try:
                available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                video.available_subtitle_languages = [lang.language_code for lang in available_languages]
                video.save()
            except Exception:
                video.available_subtitle_languages = []
                video.save()
        
        # Get snippet count
        snippet_count = video.snippets.count()
        
        # Get all words for this video with their meanings
        words = video.words.all()
        
        context = {
            'video': video,
            'snippet_count': snippet_count,
            'words': words,
            'frontend': frontend,
            'video_status_choices': VideoStatus.choices
        }
        
        return render(request, 'video_details.html', context)
    except Video.DoesNotExist:
        return render(request, '404.html', {'message': 'Video not found'}, status=404)
