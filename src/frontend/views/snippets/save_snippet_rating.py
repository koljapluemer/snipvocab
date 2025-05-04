from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.models import Snippet
from frontend.models import SnippetPractice
from datetime import datetime, timezone

class SaveSnippetRatingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        snippet_id = request.POST.get('snippet_id')
        rating = request.POST.get('rating')
        if not snippet_id or rating is None:
            return HttpResponseRedirect('/')
        snippet = Snippet.objects.get(id=snippet_id)
        # Save or update the SnippetPractice
        practice, _ = SnippetPractice.objects.get_or_create(
            user=request.user,
            snippet=snippet
        )
        practice.perceived_difficulty = int(rating)
        practice.updated = datetime.now(timezone.utc)
        practice.save()
        # Prepare context for re-render
        next_snippet = snippet.video.snippets.filter(index__gt=snippet.index).first()
        next_snippet_url = reverse('snippet_watch', kwargs={'pk': next_snippet.id}) if next_snippet else None
        return render(request, 'frontend/snippets/watch.html', {
            'snippet': snippet,
            'rating_saved': True,
            'next_snippet_url': next_snippet_url,
        }) 