# take a given snippet's words, but compare them again relevant WordProgress of a user
# if a word is not due, remove it from the return
# if a word has no practice object, note it as "not practiced"

# important model classes: Word, VocabPractice

from frontend.models import VocabPractice
from frontend.models import Snippet
from django.contrib.auth.models import User


def enrich_snippet_vocab_with_user_progress(snippet:Snippet, user:User):
    words = snippet.words.all()
    # 'ManyRelatedManager' object is not iterable, so the following line is not valid
    # word_progress = VocabPractice.objects.filter(word__in=words, user=user)
    words_to_return = []
    for word in words:
        has_progress = VocabPractice.objects.filter(word=word, user=user).exists()
        if has_progress:
            progress = VocabPractice.objects.get(word=word, user=user)
            if progress.is_due:
                word.is_new = False
                words_to_return.append(word)
        else:
            word.is_new = True
            words_to_return.append(word)
    return words_to_return

