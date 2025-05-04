from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from frontend.models import VocabPractice
from shared.models import Word, Snippet
import json
from fsrs import Scheduler, Card, State, Rating
from datetime import datetime, timezone

class SavePracticedWordsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ratings_json = request.POST.get('ratings_json')
        action = request.POST.get('action')
        snippet_id = request.POST.get('snippet_id')
        if not ratings_json or not action or not snippet_id:
            return HttpResponseRedirect('/')
        ratings = json.loads(ratings_json)
        snippet = Snippet.objects.get(id=snippet_id)
        scheduler = Scheduler()
        for entry in ratings:
            word_id = entry.get('word_id')
            rating = entry.get('rating')
            if not word_id or not rating:
                continue
            try:
                practice = VocabPractice.objects.get(user=request.user, word_id=word_id)
                # Recreate Card from DB
                card = Card(
                    state=State[practice.state] if practice.state else State.Learning,
                    step=getattr(practice, 'step', None),
                    stability=practice.stability,
                    difficulty=practice.difficulty,
                    due=practice.due,
                    last_review=practice.last_review,
                )
            except VocabPractice.DoesNotExist:
                card = Card()
                practice = VocabPractice(user=request.user, word_id=word_id)
            # Map int rating to Rating enum
            if int(rating) == 1:
                fsrs_rating = Rating.Again
            elif int(rating) == 2:
                fsrs_rating = Rating.Hard
            elif int(rating) == 3:
                fsrs_rating = Rating.Good
            elif int(rating) == 4:
                fsrs_rating = Rating.Easy
            else:
                continue
            # Review the card
            card, _ = scheduler.review_card(card, fsrs_rating)
            # Save all fields back
            practice.state = card.state.name if card.state else "Learning"
            practice.step = card.step
            practice.stability = card.stability
            practice.difficulty = card.difficulty
            practice.due = card.due
            practice.last_review = card.last_review
            practice.save()
        if action == 'practice_again':
            return HttpResponseRedirect(reverse('frontend:snippet_practice', kwargs={'pk': snippet.id}))
        elif action == 'watch_snippet':
            return HttpResponseRedirect(reverse('frontend:snippet_watch', kwargs={'pk': snippet.id}))
        else:
            return HttpResponseRedirect('/')
