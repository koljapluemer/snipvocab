from django.db import models
import math


class TagType(models.TextChoices):
    FROM_YOUTUBE = 'from_youtube', 'From YouTube'
    FROM_SEARCH = 'from_search', 'From Search'
    MANUAL = 'manual', 'Manual'
    UNKNOWN = 'unknown', 'Unknown'


class Tag(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TagType.choices, default=TagType.UNKNOWN)

    unique_together = ('name', 'type')

    def __str__(self):
        return self.name

class Frontend(models.TextChoices):
    GERMAN = 'de', '🇩🇪'
    ARABIC = 'ar', '🇪🇬'

class VideoStatus(models.TextChoices):
    NEEDS_REVIEW = 'needs_review', 'Needs Review'
    SHORTLISTED = 'shortlisted', 'Shortlisted'
    LONGLISTED = 'longlisted', 'Longlisted'
    NOT_RELEVANT = 'not_relevant', 'Not Relevant'
    SNIPPETS_GENERATED = 'snippets_generated', 'Snippets Generated'
    SNIPPETS_AND_TRANSLATIONS_GENERATED = 'snippets_and_translations_generated', 'Snippets and Translations Generated'
    LIVE = 'live', 'Live'
    BLACKLISTED = 'blacklisted', 'Blacklisted'


class Video(models.Model):
    frontend = models.CharField(max_length=10, choices=Frontend.choices, default=Frontend.ARABIC)
    title = models.CharField(max_length=500, blank=True, null=True)
    available_subtitle_languages = models.JSONField(default=list, blank=True, null=True)
    checked_for_relevant_subtitles = models.BooleanField(default=False)
    youtube_id = models.CharField(max_length=20, unique=True)
    tags = models.ManyToManyField(Tag, related_name="videos", blank=True)
    priority = models.IntegerField(default=0)
    
    status = models.CharField(max_length=100, choices=VideoStatus.choices, default=VideoStatus.NEEDS_REVIEW)
    comment = models.TextField(blank=True)
    youtube_title = models.CharField(max_length=500, blank=True, null=True)
    channel_name = models.CharField(max_length=500, blank=True, null=True)
    video_views = models.IntegerField(default=0)
    video_likes = models.IntegerField(default=0)

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.youtube_id}"
    

class Snippet(models.Model):
    content = models.TextField()
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
    occurs_in_snippets = models.ManyToManyField(Snippet, related_name="words", blank=True)

    def __str__(self):
        return self.original_word


class MeaningStatus(models.TextChoices):
    NEEDS_REVIEW = 'needs_review', 'Needs Review'
    LIVE = 'live', 'Live'
    BLACKLISTED = 'blacklisted', 'Blacklisted'
    

class Meaning(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="meanings")
    en = models.TextField()
    snippet_context = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name="meanings", null=True, blank=True)
    creation_method = models.CharField(max_length=50)
    status = models.CharField(max_length=100, choices=MeaningStatus.choices, default=MeaningStatus.LIVE)

    def __str__(self):
        return f"{self.word.original_word} - {self.meaning}"