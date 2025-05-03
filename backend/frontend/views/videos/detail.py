from django.shortcuts import render, get_object_or_404
from shared.models import Video

def video_detail(request, youtube_id):
    video = get_object_or_404(Video, youtube_id=youtube_id)
    snippets = video.snippets.all().order_by('index')
    total = snippets.count()
    # Placeholder: no perceivedDifficulty, so progress is always 0
    progress = 0
    context = {
        'video': video,
        'snippets': snippets,
        'progress': progress,
        'total_snippets': total,
    }
    return render(request, 'frontend/videos/detail.html', context) 