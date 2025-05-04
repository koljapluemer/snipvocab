from shared.models import Frontend

def get_current_frontend(request):
    """Get the current frontend from session or default to Arabic"""
    return request.session.get('frontend', Frontend.ARABIC)
