
@staff_member_required
@require_http_methods(["POST"])
def set_frontend(request):
    """Set the frontend in the session"""
    frontend = request.POST.get('frontend')
    if frontend in [f[0] for f in Frontend.choices]:
        request.session['frontend'] = frontend
    return redirect(request.POST.get('next', 'cms_home'))
