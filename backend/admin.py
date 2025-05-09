from django.contrib import admin

from shared.models import Snippet, Video, Tag
from frontend.models import VideoProgress, VocabPractice, SnippetPractice, ContentWish


admin.site.register(VideoProgress)
admin.site.register(VocabPractice)
admin.site.register(SnippetPractice)


admin.site.register(Video)
admin.site.register(Snippet)
admin.site.register(Tag)

admin.site.register(ContentWish)