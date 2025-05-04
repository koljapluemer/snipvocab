from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages

from shared.models import Video, VideoStatus, Word, Meaning
from .get_words_with_translations import get_words_with_translations

@staff_member_required
@require_http_methods(["POST"])
def generate_translations(request, youtube_id):
    """View to generate translations for all snippets in a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        if not video.snippets.exists():
            messages.error(request, "No snippets available. Please generate snippets first.")
            return redirect('cms:video_details', youtube_id=youtube_id)
        
        # Delete existing words and meanings
        Word.objects.filter(videos=video).delete()
        
        # Process each snippet
        for snippet in video.snippets.all():
            # Get words and translations for this snippet
            words_with_translations = get_words_with_translations(snippet.content, video.frontend)
            
            # Process each word
            for word_entry in words_with_translations:
                # Get or create the word
                word_obj, _ = Word.objects.get_or_create(
                    original_word=word_entry.word
                )
                
                # Add the video and snippet to the word's relationships
                word_obj.videos.add(video)
                word_obj.occurs_in_snippets.add(snippet)
                
                # Create the meaning
                Meaning.objects.create(
                    word=word_obj,
                    en=word_entry.translation,
                    snippet_context=snippet,
                    creation_method="ChatGPT 1.0.0"
                )
        
        # Update video status
        video.status = VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED
        video.save()
        
        messages.success(request, "Successfully generated translations for all snippets.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error generating translations: {str(e)}")
    
    return redirect('cms:video_details', youtube_id=youtube_id)
