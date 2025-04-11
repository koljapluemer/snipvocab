from django.shortcuts import render, redirect
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus, Snippet, Word, Meaning
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from django.contrib import messages
from openai import OpenAI, beta
from pydantic import BaseModel
from typing import List
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class WordEntry(BaseModel):
    word: str
    meaning: str

class WordEntryResponse(BaseModel):
    words: list[WordEntry]

def get_words_with_translations(text: str) -> list:
    prompt = (
        "You are an expert in Arabic. "
        "Extract language learning vocab from the following text, ignoring proper nouns like restaurant names, "
        "exclamations such as 'oh', and other non-translatable words. For each extracted word, provide an English translation suitable to learn the word on its own."
        "Retain correct capitalization and spelling. If a word appears in a declined, conjugated, or plural form, "
        "add both the occurring and base form as separate entries (e.g. for 'trees' and 'tree', or 'She ran' and 'running'), both including the translation. Return your answer as a structured list of vocab."
    )
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt + f"\n\nText: {text}\n\nOutput JSON:"}
            ],
            response_format=WordEntryResponse,
        )
        return response.choices[0].message.parsed.words
    except Exception as e:
        print(f"Error processing text snippet: {e}")
        return []

def cms_home(request):
    """Home view for the CMS"""
    # Get video statistics
    total_videos = Video.objects.count()
    needs_review = Video.objects.filter(status=VideoStatus.NEEDS_REVIEW).count()
    shortlisted = Video.objects.filter(status=VideoStatus.SHORTLISTED).count()
    longlisted = Video.objects.filter(status=VideoStatus.LONGLISTED).count()
    not_relevant = Video.objects.filter(status=VideoStatus.NOT_RELEVANT).count()
    
    context = {
        'total_videos': total_videos,
        'needs_review': needs_review,
        'shortlisted': shortlisted,
        'longlisted': longlisted,
        'not_relevant': not_relevant
    }
    
    return render(request, 'cms_home.html', context)

def import_channel_videos(request):
    """View to import videos from a YouTube channel"""
    if request.method == 'POST':
        username = request.POST.get('channel_id')
        context = {'channel_id': username}
        
        if username:
            try:
                youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
                
                # Remove @ if present
                if username.startswith('@'):
                    username = username[1:]
                
                # Search for channel by username
                channel_response = youtube.search().list(
                    q=username,
                    type='channel',
                    part='id',
                    maxResults=1
                ).execute()
                
                if not channel_response.get('items'):
                    context['error'] = f"Channel '@{username}' not found. Please check the username and try again."
                    return render(request, 'import_channel_videos.html', context)
                    
                channel_id = channel_response['items'][0]['id']['channelId']
                
                # Get channel's uploads playlist ID
                channel_response = youtube.channels().list(
                    id=channel_id,
                    part='contentDetails'
                ).execute()
                
                if not channel_response.get('items'):
                    context['error'] = f"Channel '@{username}' not found. Please check the username and try again."
                    return render(request, 'import_channel_videos.html', context)
                    
                uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # Get all videos from the uploads playlist
                next_page_token = None
                total_videos = 0
                
                while True:
                    playlist_response = youtube.playlistItems().list(
                        playlistId=uploads_playlist_id,
                        part='contentDetails',
                        maxResults=50,
                        pageToken=next_page_token
                    ).execute()
                    
                    # Create Video objects for each video
                    for item in playlist_response['items']:
                        video_id = item['contentDetails']['videoId']
                        # Only create if it doesn't exist
                        Video.objects.get_or_create(
                            youtube_id=video_id,
                            defaults={'status': VideoStatus.NEEDS_REVIEW, 'comment': f'Imported from channel {username}'}
                        )
                        total_videos += 1
                    
                    next_page_token = playlist_response.get('nextPageToken')
                    if not next_page_token:
                        break
                
                context['success'] = f"Successfully imported {total_videos} videos from channel @{username}"
                
            except Exception as e:
                error_message = str(e)
                error_details = {
                    'message': error_message,
                    'type': type(e).__name__,
                    'args': e.args
                }
                
                if hasattr(e, 'error_details'):
                    error_details['api_error'] = e.error_details
                
                context['error'] = f"An error occurred while importing videos. Details: {error_details}"
        
        return render(request, 'import_channel_videos.html', context)
    
    return render(request, 'import_channel_videos.html')

def review_videos(request):
    """View to review videos that need review"""
    # Get first 50 videos that need review, ordered by youtube_id
    videos = Video.objects.filter(status=VideoStatus.NEEDS_REVIEW).order_by('youtube_id')[:50]
    
    # Process each video to get available languages
    for video in videos:
        # Skip if already checked
        if video.checked_for_arabic_subtitles:
            continue
            
        try:
            # Get available languages using youtube_transcript_api
            available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
            video.available_subtitle_languages = [lang.language_code for lang in available_languages]
            video.checked_for_arabic_subtitles = True
            video.save()
        except Exception as e:
            # If no transcripts available, set empty list
            video.available_subtitle_languages = []
            video.checked_for_arabic_subtitles = True  # Mark as checked even if there was an error
            video.save()
    
    context = {
        'videos': videos
    }
    
    return render(request, 'review_videos.html', context)

@require_http_methods(["POST"])
def update_video_statuses(request):
    """API endpoint to update multiple video statuses"""
    try:
        # Get all POST data
        post_data = request.POST
        
        # Process each video's status and comment
        for key, value in post_data.items():
            if key.startswith('status_'):
                youtube_id = key.replace('status_', '')
                comment_key = f'comment_{youtube_id}'
                
                try:
                    video = Video.objects.get(youtube_id=youtube_id)
                    new_status = value
                    comment = post_data.get(comment_key, '')
                    
                    if new_status and new_status in [status[0] for status in VideoStatus.choices]:
                        video.status = new_status
                        video.comment = comment
                        video.save()
                except Video.DoesNotExist:
                    continue
        
        return redirect('review_videos')
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def list_all_videos(request):
    """View to list all videos with their status"""
    # Get page number and status filter from request
    page_number = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    
    # Get all videos ordered by status and youtube_id
    videos = Video.objects.all()
    
    # Apply status filter if provided
    if status_filter:
        videos = videos.filter(status=status_filter)
    
    videos = videos.order_by('status', 'youtube_id')
    
    # Paginate the videos
    paginator = Paginator(videos, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': VideoStatus.choices
    }
    
    return render(request, 'list_all_videos.html', context)

def video_details(request, youtube_id):
    """View to show details of a specific video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        # Get available languages if not already set
        if not video.available_subtitle_languages:
            try:
                available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                video.available_subtitle_languages = [lang.language_code for lang in available_languages]
                video.save()
            except Exception:
                video.available_subtitle_languages = []
                video.save()
        
        # Get snippet count
        snippet_count = video.snippets.count()
        
        # Get all words for this video with their meanings
        words = Word.objects.filter(videos=video).prefetch_related('meanings')
        
        context = {
            'video': video,
            'snippet_count': snippet_count,
            'words': words,
        }
        
        return render(request, 'video_details.html', context)
    except Video.DoesNotExist:
        return render(request, '404.html', {'message': 'Video not found'}, status=404)

@require_http_methods(["POST"])
def generate_snippets(request, youtube_id):
    """View to generate snippets for a video using YouTube transcript API"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
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
                return redirect('video_details', youtube_id=youtube_id)
        
        # Try to get the transcript in Arabic (prefer manual over auto-generated)
        arabic_transcripts = []
        if video.available_subtitle_languages:
            try:
                print("Fetching transcript list...")
                transcript_list = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                print(f"Found transcripts in languages: {[t.language_code for t in transcript_list]}")
                
                for transcript in transcript_list:
                    if transcript.language_code.startswith('ar'):
                        arabic_transcripts.append(transcript)
                        print(f"Found Arabic transcript: {transcript.language_code} (manual: {not transcript.is_generated})")
                
                if not arabic_transcripts:
                    print("No Arabic transcripts found")
                    messages.error(request, "No Arabic subtitles available for this video.")
                    return redirect('video_details', youtube_id=youtube_id)
                
                # Prefer manual transcripts over auto-generated ones
                manual_transcript = next((t for t in arabic_transcripts if not t.is_generated), None)
                transcript = manual_transcript or arabic_transcripts[0]
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
    
    return redirect('video_details', youtube_id=youtube_id)

@require_http_methods(["POST"])
def generate_translations(request, youtube_id):
    """View to generate translations for all snippets in a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        if not video.snippets.exists():
            messages.error(request, "No snippets available. Please generate snippets first.")
            return redirect('video_details', youtube_id=youtube_id)
        
        # Delete existing words and meanings
        Word.objects.filter(videos=video).delete()
        
        # Process each snippet
        for snippet in video.snippets.all():
            # Get words and translations for this snippet
            words_with_translations = get_words_with_translations(snippet.content)
            
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
        
        messages.success(request, "Successfully generated translations for all snippets.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error generating translations: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)

@require_http_methods(["POST"])
def publish_video(request, youtube_id):
    """View to publish a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        if video.status != VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED:
            messages.error(request, "Video must have snippets and translations generated before publishing.")
            return redirect('video_details', youtube_id=youtube_id)
        
        video.status = VideoStatus.LIVE
        video.save()
        
        messages.success(request, "Video has been published successfully.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error publishing video: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)

@require_http_methods(["POST"])
def reset_snippets(request, youtube_id):
    """View to reset snippets and translations for a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        if video.status not in [VideoStatus.SNIPPETS_GENERATED, 
                              VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED, 
                              VideoStatus.LIVE]:
            messages.error(request, "Video must have snippets generated to reset them.")
            return redirect('video_details', youtube_id=youtube_id)
        
        # Delete snippets (this will cascade delete words and meanings)
        video.snippets.all().delete()
        
        # Reset status to shortlisted
        video.status = VideoStatus.SHORTLISTED
        video.save()
        
        messages.success(request, "Snippets and translations have been reset successfully.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error resetting snippets: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)

def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]+)',
        r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def bulk_import_videos(request):
    """View for bulk importing YouTube videos."""
    if request.method == 'POST':
        youtube_links = request.POST.get('youtube_links', '').strip()
        if not youtube_links:
            messages.error(request, "Please paste at least one YouTube link.")
            return render(request, 'bulk_import_videos.html')
        
        links = youtube_links.split('\n')
        successful_imports = 0
        failed_imports = 0
        
        for link in links:
            link = link.strip()
            if not link:
                continue
                
            video_id = extract_youtube_id(link)
            if not video_id:
                failed_imports += 1
                continue
                
            try:
                Video.objects.get_or_create(
                    youtube_id=video_id,
                    defaults={'status': VideoStatus.NEEDS_REVIEW}
                )
                successful_imports += 1
            except Exception as e:
                failed_imports += 1
                print(f"Error importing video {video_id}: {str(e)}")
        
        if successful_imports > 0:
            messages.success(request, f"Successfully imported {successful_imports} video(s).")
        if failed_imports > 0:
            messages.warning(request, f"Failed to import {failed_imports} video(s). Please check the format of the links.")
        
        return render(request, 'bulk_import_videos.html')
    
    return render(request, 'bulk_import_videos.html')

@require_http_methods(["POST"])
def mark_videos_without_arabic_subtitles(request):
    """View to mark videos without Arabic subtitles as not relevant"""
    try:
        # Get all videos
        videos = Video.objects.all()
        marked_count = 0
        
        for video in videos:
            # Check if video has Arabic subtitles
            has_arabic = any(lang.startswith('ar') for lang in video.available_subtitle_languages)
            
            if not has_arabic:
                video.status = VideoStatus.NOT_RELEVANT
                video.save()
                marked_count += 1
        
        messages.success(request, f"Successfully marked {marked_count} videos without Arabic subtitles as not relevant.")
    except Exception as e:
        messages.error(request, f"Error marking videos: {str(e)}")
    
    return redirect('list_all_videos')

@require_http_methods(["POST"])
def generate_snippets_for_all_shortlisted(request):
    """View to generate snippets for all shortlisted videos"""
    try:
        # Get all shortlisted videos
        videos = Video.objects.filter(status=VideoStatus.SHORTLISTED)
        processed_count = 0
        error_count = 0
        no_arabic_count = 0
        error_videos = []
        
        for video in videos:
            try:
                # Get available languages if not already set
                if not video.available_subtitle_languages:
                    try:
                        available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                        video.available_subtitle_languages = [lang.language_code for lang in available_languages]
                        video.save()
                    except Exception:
                        video.available_subtitle_languages = []
                        video.save()
                
                # Try to get the transcript in Arabic
                arabic_transcripts = []
                if video.available_subtitle_languages:
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                        
                        for transcript in transcript_list:
                            if transcript.language_code.startswith('ar'):
                                arabic_transcripts.append(transcript)
                        
                        if arabic_transcripts:
                            # Prefer manual transcripts over auto-generated ones
                            manual_transcript = next((t for t in arabic_transcripts if not t.is_generated), None)
                            transcript = manual_transcript or arabic_transcripts[0]
                            
                            transcript_data = transcript.fetch()
                            
                            # Delete existing snippets
                            video.snippets.all().delete()
                            
                            # Create new snippets
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
                            processed_count += 1
                        else:
                            no_arabic_count += 1
                            error_videos.append(f"{video.youtube_id} (No Arabic subtitles)")
                    except Exception as e:
                        error_count += 1
                        error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
                else:
                    no_arabic_count += 1
                    error_videos.append(f"{video.youtube_id} (No subtitles available)")
            except Exception as e:
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
        
        if processed_count > 0:
            messages.success(request, f"Successfully generated snippets for {processed_count} videos.")
        if no_arabic_count > 0:
            messages.warning(request, f"{no_arabic_count} videos had no Arabic subtitles available.")
        if error_count > 0:
            messages.error(request, f"Failed to process {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        messages.error(request, f"Error processing videos: {str(e)}")
    
    return redirect('list_all_videos')

@require_http_methods(["POST"])
def generate_translations_for_all_snippets(request):
    """View to generate translations for all videos with snippets"""
    try:
        # Get all videos with snippets generated
        videos = Video.objects.filter(status=VideoStatus.SNIPPETS_GENERATED)
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
                    words_with_translations = get_words_with_translations(snippet.content)
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
    
    return redirect('list_all_videos')

def actions(request):
    """View for the actions page"""
    unchecked_count = Video.objects.filter(
        checked_for_arabic_subtitles=False
    ).exclude(
        status=VideoStatus.NOT_RELEVANT
    ).count()
    context = {
        'unchecked_count': unchecked_count
    }
    return render(request, 'actions.html', context)

@require_http_methods(["POST"])
def bulk_check_subtitles(request):
    """View to check subtitles for all videos that haven't been checked yet"""
    try:
        # Get all videos that haven't been checked for Arabic subtitles and aren't marked as not relevant
        videos = Video.objects.filter(
            checked_for_arabic_subtitles=False
        ).exclude(
            status=VideoStatus.NOT_RELEVANT
        )
        processed_count = 0
        error_count = 0
        error_videos = []
        
        for video in videos:
            try:
                # Get available languages
                available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                video.available_subtitle_languages = [lang.language_code for lang in available_languages]
                video.checked_for_arabic_subtitles = True
                video.save()
                processed_count += 1
            except Exception as e:
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
                # Mark as checked even if there was an error to avoid retrying
                video.checked_for_arabic_subtitles = True
                video.save()
        
        if processed_count > 0:
            messages.success(request, f"Successfully checked subtitles for {processed_count} videos.")
        if error_count > 0:
            messages.error(request, f"Failed to check subtitles for {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        messages.error(request, f"Error checking subtitles: {str(e)}")
    
    return redirect('actions')

@require_http_methods(["POST"])
def blacklist_video(request, youtube_id):
    """View to blacklist a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        video.status = VideoStatus.BLACKLISTED
        video.save()
        messages.success(request, "Video has been blacklisted successfully.")
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error blacklisting video: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)
