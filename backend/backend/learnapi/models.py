from django.conf import settings
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
import math

class Language(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " (" + self.code + ")"


class PremiumCode(models.Model):
    hrid = models.CharField(max_length=256)

    def __str__(self):
        return self.hrid

class UserProfile(models.Model):
    user_identification_code = models.CharField(max_length=512, unique=True)

    learning_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    premium_code = models.ForeignKey(PremiumCode, on_delete=models.SET_NULL, null=True, blank=True)

    daily_vocab_goal = models.PositiveIntegerField(default=25)
    daily_snippet_goal = models.PositiveIntegerField(default=10)

class Video(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="videos")
    youtube_id = models.CharField(max_length=20, unique=True)
    only_premium = models.BooleanField(default=False)  
    is_blacklisted = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.youtube_id} ({self.language.code})"
    

class Snippet(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="snippets")
    index = models.PositiveIntegerField()  # position of the snippet in the video
    start = models.FloatField()
    duration = models.FloatField()

    class Meta:
        ordering = ['index']

    def __str__(self):
        return f"Snippet {self.index} for {self.video.youtube_id}"
    
    @property
    def end_time(self):
        return math.floor(self.start + self.duration + 1)
    
    @property
    def start_time(self):
        return math.floor(self.start - 1)

class Word(models.Model):
    original_word = models.CharField(max_length=100, unique=True)
    videos = models.ManyToManyField(Video, related_name="words", blank=True)
    meanings = models.JSONField(default=list)
    occurs_in_snippets = models.ManyToManyField(Snippet, related_name="words", blank=True)

    def __str__(self):
        return self.original_word


class VideoProgress(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="video_progress")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="progresses")
    # Update last_watched whenever the video is viewed.
    last_watched = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = ('user_profile', 'video')

    def __str__(self):
        return f"{self.user_profile} - {self.video} last watched on {self.last_watched}"

class VocabPractice(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="vocab_practices")
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name="vocab_practices")
    
    # Store fsrs Card attributes exactly as defined.
    card_id = models.BigIntegerField(null=True, blank=True)
    state = models.CharField(max_length=20, default="Learning")  # We'll store the name of the state.
    step = models.IntegerField(null=True, blank=True)
    stability = models.FloatField(null=True, blank=True)
    difficulty = models.FloatField(null=True, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    last_review = models.DateTimeField(null=True, blank=True)

    is_blacklisted = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user_profile', 'word')
    
    def __str__(self):
        return f"{self.user_profile} - {self.word} practice"


class SnippetPractice(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="snippet_practices")
    snippet = models.ForeignKey('Snippet', on_delete=models.CASCADE, related_name="snippet_practices")
    
    # FSRS attributes
    card_id = models.BigIntegerField(null=True, blank=True)
    state = models.CharField(max_length=20, default="Learning")  # Store state name
    step = models.IntegerField(null=True, blank=True)
    stability = models.FloatField(null=True, blank=True)
    difficulty = models.FloatField(null=True, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    last_review = models.DateTimeField(null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_profile', 'snippet')

    def __str__(self):
        return f"{self.user_profile} - Snippet {self.snippet.index} ({self.snippet.video.youtube_id})"

