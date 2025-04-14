from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from learnapi.views.utils.meanings import deduplicate_meanings
from shared.models import Video, Snippet, Word, VideoStatus
import logging

logger = logging.getLogger(__name__)

class SnippetDetailsView(generics.RetrieveAPIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        index = self.kwargs.get('index')
        
        try:
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippet = Snippet.objects.get(video=video, index=index)
            
            # Get all words associated with this snippet
            words = Word.objects.filter(occurs_in_snippets=snippet)
            
            # Transform words to match frontend interface
            transformed_words = []
            for word in words:
                # Get all meanings for this word
                meanings = [meaning.en for meaning in word.meanings.all()]
                # Deduplicate meanings
                unique_meanings = deduplicate_meanings(meanings)
                # Create word object with deduplicated meanings
                transformed_words.append({
                    'originalWord': word.original_word,
                    'meanings': [{'en': meaning} for meaning in unique_meanings]
                })
            
            # Transform snippet to match frontend interface
            response_data = {
                'startTime': snippet.start_time,
                'endTime': snippet.end_time,
                'videoId': video.youtube_id,
                'index': snippet.index,
                'words': transformed_words
            }
            
            return Response(response_data)
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")
        except Snippet.DoesNotExist:
            raise NotFound(f"Snippet with index {index} not found for video {youtube_id}")

