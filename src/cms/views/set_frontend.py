from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from shared.models import Frontend

@staff_member_required
@require_http_methods(["POST"])
def set_frontend(request):
    """Set the frontend in the session"""
    frontend = request.POST.get('frontend')
    if frontend in [f[0] for f in Frontend.choices]:
        request.session['frontend'] = frontend
    return redirect(request.POST.get('next', 'cms:cms_home'))
