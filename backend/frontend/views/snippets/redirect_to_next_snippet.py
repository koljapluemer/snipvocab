from django.shortcuts import redirect
from shared.models import Snippet
from frontend.interactors.get_next_snippet_url import get_next_snippet_url

def redirect_to_next_snippet(request, pk:int):
    snippet = Snippet.objects.get(pk=pk)
    next_snippet_url = get_next_snippet_url(snippet)
    if next_snippet_url:
        return redirect(next_snippet_url)
    return redirect('snippet_list') 
