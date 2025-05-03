from django.conf import settings

def language_to_learn(request):
    return {
        'LANGUAGE_TO_LEARN': getattr(settings, 'LANGUAGE_TO_LEARN', 'de')
    } 