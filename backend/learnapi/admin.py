from django.contrib import admin
from .models import VideoProgress, VocabPractice, SnippetPractice

@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'last_practiced')
    list_filter = ('last_practiced',)
    search_fields = ('user__username', 'video__youtube_id')
    ordering = ('-last_practiced',)

@admin.register(VocabPractice)
class VocabPracticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'state', 'due', 'is_favorite', 'is_blacklisted')
    list_filter = ('state', 'due', 'is_favorite', 'is_blacklisted')
    search_fields = ('user__username', 'word__original_word')
    ordering = ('-updated',)

@admin.register(SnippetPractice)
class SnippetPracticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'snippet', 'perceived_difficulty', 'updated')
    list_filter = ('perceived_difficulty',)
    search_fields = ('user__username', 'snippet__video__youtube_id')
    ordering = ('-updated',)
