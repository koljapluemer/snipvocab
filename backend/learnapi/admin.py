from django.contrib import admin
from .models import VideoProgress, VocabPractice, SnippetPractice

@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'video', 'last_watched')
    list_filter = ('user_profile', 'video')
    search_fields = ('user_profile__username', 'video__youtube_id')
    ordering = ('-last_watched',)

@admin.register(VocabPractice)
class VocabPracticeAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'state', 'due', 'last_review', 'is_favorite', 'is_blacklisted')
    list_filter = ('state', 'is_favorite', 'is_blacklisted', 'user')
    search_fields = ('user__username', 'word__original_word')
    ordering = ('-due',)
    readonly_fields = ('card_id', 'state', 'step', 'stability', 'difficulty', 'due', 'last_review')

@admin.register(SnippetPractice)
class SnippetPracticeAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'snippet', 'state', 'due', 'last_review')
    list_filter = ('state', 'user_profile')
    search_fields = ('user_profile__username', 'snippet__video__youtube_id')
    ordering = ('-due',)
    readonly_fields = ('card_id', 'state', 'step', 'stability', 'difficulty', 'due', 'last_review')
