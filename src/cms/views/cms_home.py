
@staff_member_required
@never_cache
def cms_home(request):
    """Home view for the CMS"""
    frontend = get_current_frontend(request)
    # Get video statistics
    total_videos = Video.objects.filter(frontend=frontend).count()
    needs_review = Video.objects.filter(frontend=frontend, status=VideoStatus.NEEDS_REVIEW).count()
    shortlisted = Video.objects.filter(frontend=frontend, status=VideoStatus.SHORTLISTED).count()
    longlisted = Video.objects.filter(frontend=frontend, status=VideoStatus.LONGLISTED).count()
    not_relevant = Video.objects.filter(frontend=frontend, status=VideoStatus.NOT_RELEVANT).count()
    snippets_generated = Video.objects.filter(frontend=frontend, status=VideoStatus.SNIPPETS_GENERATED).count()
    snippets_and_translations_generated = Video.objects.filter(frontend=frontend, status=VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED).count()
    live = Video.objects.filter(frontend=frontend, status=VideoStatus.LIVE).count()
    blacklisted = Video.objects.filter(frontend=frontend, status=VideoStatus.BLACKLISTED).count()
    
    context = {
        'total_videos': total_videos,
        'needs_review': needs_review,
        'shortlisted': shortlisted,
        'longlisted': longlisted,
        'not_relevant': not_relevant,
        'snippets_generated': snippets_generated,
        'snippets_and_translations_generated': snippets_and_translations_generated,
        'live': live,
        'blacklisted': blacklisted,
        'frontend': frontend
    }
    
    return render(request, 'cms_home.html', context)
