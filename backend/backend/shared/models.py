from django.db import models
import math

class Language(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " (" + self.code + ")"

class VideoStatus(models.TextChoices):
    NEEDS_REVIEW = 'needs_review', 'Needs Review'
    SHORTLISTED = 'shortlisted', 'Shortlisted'
    LONGLISTED = 'longlisted', 'Longlisted'
    NOT_RELEVANT = 'not_relevant', 'Not Relevant'
    ASSETS_GENERATED = 'assets_generated', 'Assets Generated'
    BLACKLISTED = 'blacklisted', 'Blacklisted'

class Video(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="videos", null=True, blank=True) # largely obsolete
    available_subtitle_languages = models.JSONField(default=list)
    youtube_id = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=VideoStatus.choices, default=VideoStatus.NEEDS_REVIEW)
    comment = models.TextField(blank=True)

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
