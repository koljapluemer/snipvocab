from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages

from shared.models import Video, Frontend, VideoStatus, Word, Meaning
from .get_current_frontend import get_current_frontend
from .get_words_with_translations import get_words_with_translations

@staff_member_required
@require_http_methods(["POST"])
def generate_translations_for_all_snippets(request):
    """View to generate translations for all videos with snippets"""
    frontend = get_current_frontend(request)
    try:
        # Get all videos with snippets generated for the current frontend
        videos = Video.objects.filter(frontend=frontend, status=VideoStatus.SNIPPETS_GENERATED)
        processed_count = 0
        error_count = 0
        no_snippets_count = 0
        error_videos = []
        
        for video in videos:
            try:
                if not video.snippets.exists():
                    no_snippets_count += 1
                    error_videos.append(f"{video.youtube_id} (No snippets found)")
                    continue
                
                # Delete existing words and meanings
                Word.objects.filter(videos=video).delete()
                
                # Process each snippet
                total_words = 0
                for snippet in video.snippets.all():
                    # Get words and translations for this snippet
                    words_with_translations = get_words_with_translations(snippet.content, frontend)
                    total_words += len(words_with_translations)
                    
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
                            en=word_entry.meaning,
                            snippet_context=snippet,
                            creation_method="ChatGPT 1.0.0"
                        )
                
                # Update video status
                video.status = VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED
                video.save()
                processed_count += 1
                messages.success(request, f"Video {video.youtube_id}: Generated {total_words} words and translations.")
            except Exception as e:
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
        
        if processed_count > 0:
            messages.success(request, f"Successfully processed {processed_count} videos.")
        if no_snippets_count > 0:
            messages.warning(request, f"{no_snippets_count} videos had no snippets available.")
        if error_count > 0:
            messages.error(request, f"Failed to process {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        messages.error(request, f"Error processing videos: {str(e)}")
    
    return redirect('cms:list_all_videos')
