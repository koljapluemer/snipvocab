

from frontend.models import Video
from frontend.models import SnippetPractice
from django.contrib.auth.models import User

# function that takes a video and returns its snippets
# however, current user is analyzed, and if they have practiced a given snippet,
# the perceived_difficulty is appended to the snippet
def enrich_video_snippets_with_user_progress(video:Video, user:User):
    snippets = video.snippets.all()
    snippet_practices = SnippetPractice.objects.filter(user=user, snippet__in=snippets)
    for snippet in snippets:
        # practice may not exist, so we need to handle that
        if snippet_practices.filter(snippet=snippet).exists():
            snippet.perceived_difficulty = snippet_practices.get(snippet=snippet).perceived_difficulty
        else:
            snippet.perceived_difficulty = None
    return snippets

