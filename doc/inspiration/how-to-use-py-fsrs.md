```python
def snippet_watch(request, snippet_id):
    
    snippet = get_object_or_404(Snippet,id=snippet_id)

    if request.method == 'POST':
        try:
            answer = int(request.POST.get('answer'))
        except (ValueError, TypeError):
            return render(request, 'videos/snippet_watch.html', {
                'snippet': snippet,
                'video': snippet.video,
                'error': "Invalid answer submitted.",
            })

        scheduler = Scheduler()
        
        # Get or create a practice record
        practice, created = SnippetPractice.objects.get_or_create(
            user_profile=request.user_profile,
            snippet=snippet,
            defaults={'state': "Learning", 'due': timezone.now()}
        )

        if created:
            card = Card()  # New FSRS card
        else:
            # Recreate the FSRS card from stored practice state
            from fsrs import State
            card = Card(
                card_id=practice.card_id,
                state=State[practice.state] if practice.state else State.Learning,
                step=practice.step,
                stability=practice.stability,
                difficulty=practice.difficulty,
                due=practice.due,
                last_review=practice.last_review,
            )

        # Map the user's rating to an FSRS rating
        rating_map = {1: Rating.Again, 2: Rating.Hard, 3: Rating.Good, 4: Rating.Easy}
        rating = rating_map.get(answer)
        if not rating:
            return render(request, 'videos/snippet_watch.html', {
                'snippet': snippet,
                'video': snippet.video,
                'error': "Invalid rating value.",
            })

        # Update FSRS card
        card, review_log = scheduler.review_card(card, rating)

        # Save updated practice data
        practice.card_id = card.card_id
        practice.state = card.state.name if card.state else "Learning"
        practice.step = card.step
        practice.stability = card.stability
        practice.difficulty = card.difficulty
        practice.due = card.due
        practice.last_review = card.last_review
        practice.save()
        return redirect(reverse('show_snippet_endscreen', args=[snippet.id]))
    
    return render(request, 'videos/snippet_watch.html', {
        'snippet': snippet,
        'video': snippet.video,
    })

# practice all the words the user encountered so far
def words_practice(request):
    
        # Retrieve all words associated with this snippet.
    practice_objs_of_words_user_has_practiced_before = VocabPractice.objects.filter(user_profile=request.user_profile)
    now = timezone.now()
    due_words = []

    request.session["active_snippet_id"] = None
    
    # For each word, if no practice record exists, or if it exists and is due, consider it due.
    for practice in practice_objs_of_words_user_has_practiced_before:
        if practice.due is not None and practice.due <= now and not practice.is_blacklisted:
            if "last_word_id" in request.session:
                last_word_id = int(request.session["last_word_id"]) 
                last_word = Word.objects.get(id=last_word_id)

                if last_word.id != practice.word.id:
                    due_words.append(practice.word)
            else:
                    due_words.append(practice.word)
    if len(due_words) == 0:
        messages.success(request, "All due words practiced :)")
        return redirect('dashboard')

    selected_word:Word = random.choice(due_words)
    return redirect(reverse('word_practice', args=[selected_word.id]))



def word_practice(request, word_id):
    
    word = get_object_or_404(Word, id=word_id)
    practice = word.vocab_practices.filter(user_profile=request.user_profile).first()

    request.session["last_word_id"] = word_id

    if request.method == 'POST':
        try:
            answer = int(request.POST.get('answer'))
        except (ValueError, TypeError):
            error_msg = "Invalid answer submitted."
            return render(request, 'videos/word_practice.html', {
                'word': word,
                'error': error_msg,
            })
        
     
        
        # Initialize the scheduler.
        scheduler = Scheduler()
        if practice is None:
            card = Card()
            practice = VocabPractice.objects.create(
                user_profile=request.user_profile,
                word=word,
                card_id = card.card_id,
                state = card.state.name if card.state else "Learning",
                step = card.step,
                stability = card.stability,
                difficulty = card.difficulty,
                due = card.due,
                last_review = card.last_review,
            )
               # blacklist
            if answer == 99:
                rating = Rating.Again
                practice.is_blacklisted = True
                practice.save() 
        else:
            # Recreate the Card from stored practice state.
            # Assume that the state was stored as a string (e.g., "Learning") and convert it using fsrs.State.
            card = Card(
                card_id = practice.card_id,
                state = State[practice.state] if practice.state else State.Learning,
                step = practice.step,
                stability = practice.stability,
                difficulty = practice.difficulty,
                due = practice.due,
                last_review = practice.last_review,
            )
        
            # Map the submitted answer to an fsrs Rating.
            if answer == 99:
                rating = Rating.Again
                practice.is_blacklisted = True
                practice.save() 
            elif answer == 1:
                rating = Rating.Again
            elif answer == 2:
                rating = Rating.Hard
            elif answer == 3:
                rating = Rating.Good
            elif answer == 4:
                rating = Rating.Easy
            
            # Update the card using the fsrs API.
            card, _ = scheduler.review_card(card, rating)
        
            practice.card_id = card.card_id
            practice.state = card.state.name if card.state else "Learning"
            practice.step = card.step
            practice.stability = card.stability
            practice.difficulty = card.difficulty
            
            practice.due = card.due
            # I want to immediately re-practice 'Wrong' words
            if rating == Rating.Again:
                practice.due = timezone.now()

            practice.last_review = card.last_review
            practice.save()

        # if we're currently practicing a snippet, let 
        # snippet_practice handle which word we're picking
        if "active_snippet_id" in request.session:
            if request.session["active_snippet_id"] != None:
                snippet_id = int(request.session["active_snippet_id"])
                return redirect(reverse('snippet_practice', args=[snippet_id]))
        
        # else, we let words_practice pick the next word
        return redirect(reverse('words_practice'))
    
    is_favorite = False
    if practice is not None:
        if practice.is_favorite:
            is_favorite = True

    return render(request, 'videos/word_practice.html', {
        'word': word,
        'was_practiced_before': practice is not None,
        'is_favorite': is_favorite
    })

```