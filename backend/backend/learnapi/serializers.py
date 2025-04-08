from rest_framework import serializers
from .models import Video, Snippet

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'youtube_id', 'only_premium', 'is_blacklisted']

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ['id', 'index', 'start', 'duration', 'start_time', 'end_time'] 