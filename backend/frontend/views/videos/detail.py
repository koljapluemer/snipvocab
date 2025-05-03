from django.shortcuts import render, get_object_or_404
from shared.models import Video
from guest_user.decorators import allow_guest_user
from learnapi.models import VideoProgress
from django.utils import timezone

@allow_guest_user
def video_detail(request, youtube_id):
    video = get_object_or_404(Video, youtube_id=youtube_id)
    snippets = video.snippets.all().order_by('index')
    total = snippets.count()
    # Upsert VideoProgress for this user and video
    if request.user.is_authenticated:
        VideoProgress.objects.update_or_create(
            user=request.user,
            video=video,
            defaults={"last_practiced": timezone.now()}
        )
    # Placeholder: no perceivedDifficulty, so progress is always 0
    progress = 0
    first_snippet = snippets.first() if snippets else None
    context = {
        'video': video,
        'snippets': snippets,
        'progress': progress,
        'total_snippets': total,
        'first_snippet': first_snippet,
    }
    return render(request, 'frontend/videos/detail.html', context) 