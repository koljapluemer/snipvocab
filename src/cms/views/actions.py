
@staff_member_required
def actions(request):
    """View for the actions page"""
    frontend = get_current_frontend(request)
    unchecked_count = Video.objects.filter(
        frontend=frontend,
        checked_for_relevant_subtitles=False
    ).exclude(
        status=VideoStatus.NOT_RELEVANT
    ).count()
    context = {
        'unchecked_count': unchecked_count,
        'frontend': frontend
    }
    return render(request, 'actions.html', context)
