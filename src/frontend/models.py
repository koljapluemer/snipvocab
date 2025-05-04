from django.conf import settings
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from shared.models import Video, Snippet, Word

class VideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="video_progress")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="progresses")
    # Update last_practiced whenever the video is viewed.
    last_practiced = models.DateTimeField(default=timezone.now)
    perceived_difficulty = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user} - {self.video} last practiced on {self.last_practiced}"

class VocabPractice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vocab_practices")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="vocab_practices")
    
    state = models.CharField(max_length=20, default="Learning")  # We'll store the name of the state.
    step = models.IntegerField(null=True, blank=True)
    stability = models.FloatField(null=True, blank=True)
    difficulty = models.FloatField(null=True, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    last_review = models.DateTimeField(null=True, blank=True)

    # is_blacklisted = models.BooleanField(default=False)
    # is_favorite = models.BooleanField(default=False)
    
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'word')
    
    def __str__(self):
        return f"{self.user} - {self.word} practice"
    
    @property
    def is_due(self):
        return self.due and self.due <= timezone.now()


class SnippetPractice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="snippet_practices")
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name="snippet_practices")
    
    perceived_difficulty = models.IntegerField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    is_blacklisted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'snippet')

    def __str__(self):
        return f"{self.user} - Snippet {self.snippet.index} ({self.snippet.video.youtube_id})"


class Feedback(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback" )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.content[:30]}"