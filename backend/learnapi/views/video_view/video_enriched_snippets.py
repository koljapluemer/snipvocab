from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from learnapi.models import SnippetPractice, VideoProgress
from learnapi.views.utils.meanings import deduplicate_meanings
from shared.models import Video, Snippet, Word, VideoStatus
import logging
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class VideoEnrichedSnippetsView(generics.GenericAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        
        try:
            # Get the video
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            
            # Get video progress if it exists
            try:
                video_progress = VideoProgress.objects.get(user=request.user, video=video)
                last_practiced = video_progress.last_practiced.isoformat() if video_progress.last_practiced else None
                snippet_percentage_watched = video_progress.snippet_percentage_watched
                perceived_difficulty = video_progress.perceived_difficulty
            except VideoProgress.DoesNotExist:
                last_practiced = None
                snippet_percentage_watched = None
                perceived_difficulty = None
            
            # Get all snippets for this video
            snippets = Snippet.objects.filter(video=video).order_by('index')
            
            # Transform snippets to match frontend interface
            enriched_snippets = []
            for snippet in snippets:
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
                
                # Get practice data if it exists
                try:
                    practice = SnippetPractice.objects.get(user=request.user, snippet=snippet)
                    snippet_perceived_difficulty = practice.perceived_difficulty
                    last_updated = practice.updated
                except SnippetPractice.DoesNotExist:
                    snippet_perceived_difficulty = None
                    last_updated = None
                
                # Create enriched snippet details
                enriched_snippet = {
                    'startTime': snippet.start_time,
                    'endTime': snippet.end_time,
                    'videoId': video.youtube_id,
                    'index': snippet.index,
                    'words': transformed_words,
                    'perceivedDifficulty': snippet_perceived_difficulty,
                    'lastUpdated': last_updated.isoformat() if last_updated else None
                }
                
                enriched_snippets.append(enriched_snippet)
            
            return Response({
                'snippets': enriched_snippets,
                'lastPracticed': last_practiced,
                'snippetPercentageWatched': snippet_percentage_watched,
                'perceivedDifficulty': perceived_difficulty,
                'title': video.youtube_title
            })
            
        except Video.DoesNotExist:
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")

