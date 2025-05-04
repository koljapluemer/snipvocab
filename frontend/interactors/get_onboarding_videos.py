from django.conf import settings
from shared.models import Video, VideoStatus

def get_onboarding_videos():
    # Use the feature flag to select the frontend language
    language_code = getattr(settings, 'LANGUAGE_TO_LEARN', 'de')
    frontend_value = language_code  # 'de' or 'ar'

    # Get first 3 live videos with the feature-in-onboarding tag
    videos = Video.objects.filter(
        status=VideoStatus.LIVE,
        frontend=frontend_value,
        tags__name='feature-in-onboarding'
    ).order_by('added_at')[:3]
    
    return videos
