from django.shortcuts import render
from guest_user.decorators import allow_guest_user
from frontend.interactors.get_onboarding_videos import get_onboarding_videos

@allow_guest_user
def onboarding(request):
    videos = get_onboarding_videos()
    context = {
        'videos': videos,
    }
    return render(request, 'frontend/onboarding/onboarding.html', context)
