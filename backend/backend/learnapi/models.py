from django.conf import settings
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from shared.models import Video, Snippet, Word


class UserProfile(models.Model):
    daily_vocab_goal = models.PositiveIntegerField(default=25)
    daily_snippet_goal = models.PositiveIntegerField(default=10)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vocab_practices")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="vocab_practices")
    
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
        unique_together = ('user', 'word')
    
    def __str__(self):
        return f"{self.user_profile} - {self.word} practice"


class SnippetPractice(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="snippet_practices")
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name="snippet_practices")
    
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

