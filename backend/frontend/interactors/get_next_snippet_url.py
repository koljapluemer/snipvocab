from shared.models import Snippet

# a function that takes a snippet and returns the next snippet url
# goes to parent video and gets snippet with next higher index, if it exists
# returns the url of the next snippet
def get_next_snippet_url(snippet:Snippet) -> str | None:
    video = snippet.video
    next_snippet = video.snippets.filter(index__gt=snippet.index).first()
    if next_snippet:
        return next_snippet.get_absolute_url()
    return None