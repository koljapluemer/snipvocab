from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from learnapi.models import VocabPractice
from learnapi.views.utils.meanings import deduplicate_meanings
from shared.models import Video, Snippet, Word, VideoStatus
import logging
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)
class SnippetDueWordsView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        youtube_id = self.kwargs.get('youtube_id')
        index = self.kwargs.get('index')
        
        logger.info(f"Fetching due words for video {youtube_id}, snippet {index}, user {request.user.id}")
        
        try:
            # Get the video and snippet
            video = Video.objects.get(youtube_id=youtube_id, status=VideoStatus.LIVE)
            snippet = Snippet.objects.get(video=video, index=index)
            
            # Get all words associated with this snippet
            words = Word.objects.filter(occurs_in_snippets=snippet)
            logger.debug(f"Found {words.count()} words in snippet")
            
            # Transform words to match frontend interface
            transformed_words = []
            for word in words:
                try:
                    # Get all meanings for this word and deduplicate them
                    meanings = [meaning.en for meaning in word.meanings.all()]
                    unique_meanings = deduplicate_meanings(meanings)
                    
                    # Try to get existing practice
                    try:
                        vocab_practice = VocabPractice.objects.get(user=request.user, word=word)
                        # If practice exists and is due, add to response
                        if vocab_practice.is_due:
                            transformed_words.append({
                                'originalWord': word.original_word,
                                'meanings': [{'en': meaning} for meaning in unique_meanings],
                                'isDue': True,
                                'isNew': False,
                                'isFavorite': vocab_practice.is_favorite,
                                'isBlacklisted': vocab_practice.is_blacklisted
                            })
                    except VocabPractice.DoesNotExist:
                        # No practice exists for this word - it's new and due
                        transformed_words.append({
                            'originalWord': word.original_word,
                            'meanings': [{'en': meaning} for meaning in unique_meanings],
                            'isDue': True,
                            'isNew': True,
                            'isFavorite': False,
                            'isBlacklisted': False
                        })
                except Exception as e:
                    logger.error(f"Error processing word {word.original_word}: {str(e)}")
                    continue
            
            logger.info(f"Returning {len(transformed_words)} due words")
            return Response(transformed_words)
            
        except Video.DoesNotExist:
            logger.warning(f"Video {youtube_id} not found or not live")
            raise NotFound(f"Video with YouTube ID {youtube_id} not found or not live")
        except Snippet.DoesNotExist:
            logger.warning(f"Snippet {index} not found for video {youtube_id}")
            raise NotFound(f"Snippet with index {index} not found for video {youtube_id}")
        except Exception as e:
            logger.error(f"Unexpected error in SnippetDueWordsView: {str(e)}")
            raise