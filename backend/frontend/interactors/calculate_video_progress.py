from shared.models import Video
from learnapi.models import SnippetPractice
from django.contrib.auth.models import User

def calculate_video_progress(video:Video, user:User):
    # in %, rounded to 2 decimal places
    # 0 if no snippets practiced
    # 100 if all snippets practiced
    # otherwise, the percentage of snippets practiced
    snippets = video.snippets.all()
    snippet_practices = SnippetPractice.objects.filter(user=user, snippet__in=snippets)
    return round(snippet_practices.count() / snippets.count() * 100, 2)   