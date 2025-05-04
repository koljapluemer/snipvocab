from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages
from youtube_transcript_api import YouTubeTranscriptApi

from shared.models import Video, Frontend, VideoStatus, Snippet

@staff_member_required
@require_http_methods(["POST"])
def generate_snippets(request, youtube_id):
    """View to generate snippets for a video using YouTube transcript API"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        frontend = video.frontend
        print(f"Processing video: {youtube_id}")
        
        # Get available languages if not already set
        if not video.available_subtitle_languages:
            print("Fetching available languages...")
            try:
                available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                video.available_subtitle_languages = [lang.language_code for lang in available_languages]
                video.save()
                print(f"Found languages: {video.available_subtitle_languages}")
            except Exception as e:
                print(f"Error fetching languages: {str(e)}")
                video.available_subtitle_languages = []
                video.save()
                messages.error(request, f"Error fetching available languages: {str(e)}")
                return redirect('cms:video_details', youtube_id=youtube_id)
        
        # Try to get the transcript in the target language (prefer manual over auto-generated)
        target_transcripts = []
        if video.available_subtitle_languages:
            try:
                print("Fetching transcript list...")
                transcript_list = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                print(f"Found transcripts in languages: {[t.language_code for t in transcript_list]}")
                
                for transcript in transcript_list:
                    if frontend == Frontend.ARABIC and transcript.language_code.startswith('ar'):
                        target_transcripts.append(transcript)
                        print(f"Found Arabic transcript: {transcript.language_code} (manual: {not transcript.is_generated})")
                    elif frontend == Frontend.GERMAN and transcript.language_code.startswith('de'):
                        target_transcripts.append(transcript)
                        print(f"Found German transcript: {transcript.language_code} (manual: {not transcript.is_generated})")
                
                if not target_transcripts:
                    print(f"No {frontend} transcripts found")
                    messages.error(request, f"No {frontend} subtitles available for this video.")
                    return redirect('cms:video_details', youtube_id=youtube_id)
                
                # Prefer manual transcripts over auto-generated ones
                manual_transcript = next((t for t in target_transcripts if not t.is_generated), None)
                transcript = manual_transcript or target_transcripts[0]
                print(f"Selected transcript: {transcript.language_code} (manual: {not transcript.is_generated})")
                
                print("Fetching transcript data...")
                transcript_data = transcript.fetch()
                print(f"Found {len(transcript_data)} segments")
                
                # Delete existing snippets
                print("Deleting existing snippets...")
                video.snippets.all().delete()
                
                # Create new snippets
                print("Creating new snippets...")
                for index, segment in enumerate(transcript_data):
                    Snippet.objects.create(
                        video=video,
                        index=index,
                        content=segment.text,
                        start=segment.start,
                        duration=segment.duration
                    )
                
                # Update video status
                video.status = VideoStatus.SNIPPETS_GENERATED
                video.save()
                
                print(f"Successfully created {len(transcript_data)} snippets")
                messages.success(request, f"Successfully generated {len(transcript_data)} snippets from {transcript.language_code} subtitles.")
            except Exception as e:
                print(f"Error in transcript processing: {str(e)}")
                messages.error(request, f"Error generating snippets: {str(e)}")
        else:
            print("No available languages found")
            messages.error(request, "No subtitles available for this video.")
            
    except Video.DoesNotExist:
        print(f"Video not found: {youtube_id}")
        messages.error(request, "Video not found.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.error(request, f"An unexpected error occurred: {str(e)}")
    
    return redirect('cms:video_details', youtube_id=youtube_id)
