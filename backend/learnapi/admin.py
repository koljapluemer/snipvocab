from django.contrib import admin
from .models import VideoProgress, VocabPractice, SnippetPractice

@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'last_watched')
    list_filter = ('last_watched',)
    search_fields = ('user__username', 'video__youtube_id')
    ordering = ('-last_watched',)

@admin.register(VocabPractice)
class VocabPracticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'state', 'is_blacklisted', 'is_favorite', 'last_review', 'due')
    list_filter = ('state', 'is_blacklisted', 'is_favorite')
    search_fields = ('user__username', 'word__original_word')
    ordering = ('-updated',)

@admin.register(SnippetPractice)
class SnippetPracticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'snippet', 'perceived_difficulty', 'updated')
    list_filter = ('perceived_difficulty',)
    search_fields = ('user__username', 'snippet__video__youtube_id')
    ordering = ('-updated',)
