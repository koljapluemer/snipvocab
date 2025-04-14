from django.shortcuts import render, redirect
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus, Snippet, Word, Meaning, Frontend
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from django.contrib import messages
from openai import OpenAI, beta
from pydantic import BaseModel
from typing import List
import re
import csv
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.urls import reverse

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class WordEntry(BaseModel):
    word: str
    meaning: str

class WordEntryResponse(BaseModel):
    words: list[WordEntry]

def get_words_with_translations(text: str, frontend: str) -> list:
    """Get words and translations for a given text based on the frontend language"""
    if frontend == Frontend.ARABIC:
        prompt = (
            "You are an expert in Spoken, Egyptian Arabic. "
            "Extract language learning vocabulary from the following natural language transcript, ignoring proper nouns like restaurant names, "
            "exclamations such as 'oh', and other non-translatable words. For each extracted word, provide an English translation suitable to learn the word on its own."
            "Retain correct capitalization and spelling. If a word appears in a declined, conjugated, or plural form, "
            "add both the occurring and base form as separate entries (e.g. for 'أشجار' and 'شجرة', or 'بناكل' and 'كل'), both including the translation. Return your answer as a structured list of vocab."
        )
    else:  # German
        prompt = (
            "You are an expert in German. "
            "Extract language learning vocabulary from the following text, ignoring proper nouns like restaurant names, "
            "exclamations such as 'oh', and other non-translatable words. For each extracted word, provide an English translation suitable to learn the word on its own."
            "Retain correct capitalization and spelling. If a word appears in a declined, conjugated, or plural form, "
            "add both the occurring and base form as separate entries (e.g. for 'Bäume' and 'Baum', or 'Sie lief' and 'laufen'), both including the translation. Return your answer as a structured list of vocab."
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

@staff_member_required
@require_http_methods(["POST"])
def set_frontend(request):
    """Set the frontend in the session"""
    frontend = request.POST.get('frontend')
    if frontend in [f[0] for f in Frontend.choices]:
        request.session['frontend'] = frontend
    return redirect(request.POST.get('next', 'cms_home'))

def get_current_frontend(request):
    """Get the current frontend from session or default to Arabic"""
    return request.session.get('frontend', Frontend.ARABIC)

@staff_member_required
def cms_home(request):
    """Home view for the CMS"""
    frontend = get_current_frontend(request)
    # Get video statistics
    total_videos = Video.objects.filter(frontend=frontend).count()
    needs_review = Video.objects.filter(frontend=frontend, status=VideoStatus.NEEDS_REVIEW).count()
    shortlisted = Video.objects.filter(frontend=frontend, status=VideoStatus.SHORTLISTED).count()
    longlisted = Video.objects.filter(frontend=frontend, status=VideoStatus.LONGLISTED).count()
    not_relevant = Video.objects.filter(frontend=frontend, status=VideoStatus.NOT_RELEVANT).count()
    snippets_generated = Video.objects.filter(frontend=frontend, status=VideoStatus.SNIPPETS_GENERATED).count()
    snippets_and_translations_generated = Video.objects.filter(frontend=frontend, status=VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED).count()
    live = Video.objects.filter(frontend=frontend, status=VideoStatus.LIVE).count()
    blacklisted = Video.objects.filter(frontend=frontend, status=VideoStatus.BLACKLISTED).count()
    
    context = {
        'total_videos': total_videos,
        'needs_review': needs_review,
        'shortlisted': shortlisted,
        'longlisted': longlisted,
        'not_relevant': not_relevant,
        'snippets_generated': snippets_generated,
        'snippets_and_translations_generated': snippets_and_translations_generated,
        'live': live,
        'blacklisted': blacklisted,
        'frontend': frontend
    }
    
    return render(request, 'cms_home.html', context)

@staff_member_required
def import_channel_videos(request):
    """View to import videos from a YouTube channel"""
    frontend = get_current_frontend(request)
    if request.method == 'POST':
        username = request.POST.get('channel_id')
        import_all = request.POST.get('import_all') == 'true'
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
                
                # Get total number of videos in the playlist
                playlist_response = youtube.playlists().list(
                    id=uploads_playlist_id,
                    part='contentDetails',
                    maxResults=1
                ).execute()
                
                total_videos = playlist_response['items'][0]['contentDetails']['itemCount']
                
                # Get existing video IDs from our database
                existing_video_ids = set(Video.objects.filter(frontend=frontend).values_list('youtube_id', flat=True))
                
                # Get the most recent video ID we've processed for this channel
                last_processed_video = Video.objects.filter(
                    frontend=frontend,
                    comment__startswith=f'Imported from channel {username}'
                ).order_by('-youtube_id').first()
                
                # Get videos from the playlist
                next_page_token = None
                imported_count = 0
                remaining_videos = total_videos
                batch_size = 100
                found_last_processed = False
                
                while True:
                    playlist_response = youtube.playlistItems().list(
                        playlistId=uploads_playlist_id,
                        part='contentDetails,snippet',
                        maxResults=50,
                        pageToken=next_page_token
                    ).execute()
                    
                    # Create Video objects for each video that doesn't exist yet
                    for item in playlist_response['items']:
                        video_id = item['contentDetails']['videoId']
                        
                        # If we've found our last processed video, we can start importing
                        if last_processed_video and video_id == last_processed_video.youtube_id:
                            found_last_processed = True
                            continue
                            
                        # If we haven't found our last processed video yet, skip
                        if last_processed_video and not found_last_processed:
                            continue
                        
                        if video_id not in existing_video_ids:
                            Video.objects.get_or_create(
                                youtube_id=video_id,
                                frontend=frontend,
                                defaults={
                                    'status': VideoStatus.NEEDS_REVIEW,
                                    'comment': f'Imported from channel {username}',
                                    'youtube_title': item['snippet']['title']
                                }
                            )
                            imported_count += 1
                            existing_video_ids.add(video_id)
                        
                        remaining_videos -= 1
                        
                        # If we've imported the batch size and not importing all, stop
                        if imported_count >= batch_size and not import_all:
                            break
                    
                    if not import_all and imported_count >= batch_size:
                        break
                        
                    next_page_token = playlist_response.get('nextPageToken')
                    if not next_page_token:
                        break
                
                context['success'] = f"Successfully imported {imported_count} new videos from channel @{username}"
                if remaining_videos > 0:
                    context['remaining'] = remaining_videos
                    context['channel_id'] = username
                
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

@staff_member_required
def review_videos(request):
    """View to review videos that need review"""
    frontend = get_current_frontend(request)
    # Get first 50 videos that need review, ordered by priority (descending) and youtube_id
    videos = Video.objects.filter(frontend=frontend, status=VideoStatus.NEEDS_REVIEW).order_by('-priority', 'youtube_id')[:50]
    
    # Process each video to get available languages
    for video in videos:
        # Skip if already checked
        if video.checked_for_relevant_subtitles:
            continue
            
        try:
            # Get available languages using youtube_transcript_api
            available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
            video.available_subtitle_languages = [lang.language_code for lang in available_languages]
            video.checked_for_relevant_subtitles = True
            video.save()
        except Exception as e:
            # If no transcripts available, set empty list
            video.available_subtitle_languages = []
            video.checked_for_relevant_subtitles = True  # Mark as checked even if there was an error
            video.save()
    
    context = {
        'videos': videos,
        'frontend': frontend
    }
    
    return render(request, 'review_videos.html', context)

@staff_member_required
@require_http_methods(["POST"])
def update_video_statuses(request):
    """API endpoint to update multiple video statuses"""
    try:
        # Get all POST data
        post_data = request.POST
        
        # Check for bulk status update
        bulk_status = post_data.get('bulk_status')
        if bulk_status:
            # Get all videos in the current review queue
            videos = Video.objects.filter(status=VideoStatus.NEEDS_REVIEW).order_by('youtube_id')[:50]
            for video in videos:
                video.status = bulk_status
                video.save()
            messages.success(request, f"Successfully updated status for all videos to {bulk_status}.")
            return redirect('review_videos')
        
        # Process individual video statuses
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

@staff_member_required
def list_all_videos(request):
    """View to list all videos with their status"""
    frontend = get_current_frontend(request)
    # Get page number and status filter from request
    page_number = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    comment_filter = request.GET.get('comment', '')
    
    # Get all videos ordered by status and youtube_id
    videos = Video.objects.filter(frontend=frontend)
    
    # Apply status filter if provided
    if status_filter:
        videos = videos.filter(status=status_filter)
    
    # Apply comment filter if provided
    if comment_filter:
        videos = videos.filter(comment__icontains=comment_filter)
    
    videos = videos.order_by('status', 'youtube_id')
    
    # Paginate the videos
    paginator = Paginator(videos, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'comment_filter': comment_filter,
        'status_choices': VideoStatus.choices,
        'frontend': frontend
    }
    
    return render(request, 'list_all_videos.html', context)

@staff_member_required
def video_details(request, youtube_id):
    """View to show details of a specific video"""
    frontend = get_current_frontend(request)
    try:
        video = Video.objects.get(youtube_id=youtube_id, frontend=frontend)
        
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
            'frontend': frontend
        }
        
        return render(request, 'video_details.html', context)
    except Video.DoesNotExist:
        return render(request, '404.html', {'message': 'Video not found'}, status=404)

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
                return redirect('video_details', youtube_id=youtube_id)
        
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
                    return redirect('video_details', youtube_id=youtube_id)
                
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
    
    return redirect('video_details', youtube_id=youtube_id)

@staff_member_required
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

@staff_member_required
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

@staff_member_required
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

@staff_member_required
def bulk_import_videos(request):
    """View for bulk importing YouTube videos."""
    frontend = get_current_frontend(request)
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
                    frontend=frontend,
                    defaults={'status': VideoStatus.NEEDS_REVIEW, 'comment': 'bulk imported'}
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

@staff_member_required
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

@staff_member_required
@require_http_methods(["POST"])
def generate_snippets_for_all_shortlisted(request):
    """View to generate snippets for all shortlisted videos"""
    frontend = get_current_frontend(request)
    try:
        # Get all shortlisted videos for the current frontend
        videos = Video.objects.filter(frontend=frontend, status=VideoStatus.SHORTLISTED)
        processed_count = 0
        error_count = 0
        no_subtitles_count = 0
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
                
                # Try to get the transcript in the target language
                target_transcripts = []
                if video.available_subtitle_languages:
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                        
                        for transcript in transcript_list:
                            if frontend == Frontend.ARABIC and transcript.language_code.startswith('ar'):
                                target_transcripts.append(transcript)
                            elif frontend == Frontend.GERMAN and transcript.language_code.startswith('de'):
                                target_transcripts.append(transcript)
                        
                        if target_transcripts:
                            # Prefer manual transcripts over auto-generated ones
                            manual_transcript = next((t for t in target_transcripts if not t.is_generated), None)
                            transcript = manual_transcript or target_transcripts[0]
                            
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
                            no_subtitles_count += 1
                            error_videos.append(f"{video.youtube_id} (No {frontend} subtitles)")
                    except Exception as e:
                        error_count += 1
                        error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
                else:
                    no_subtitles_count += 1
                    error_videos.append(f"{video.youtube_id} (No subtitles available)")
            except Exception as e:
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
        
        if processed_count > 0:
            messages.success(request, f"Successfully generated snippets for {processed_count} videos.")
        if no_subtitles_count > 0:
            messages.warning(request, f"{no_subtitles_count} videos had no {frontend} subtitles available.")
        if error_count > 0:
            messages.error(request, f"Failed to process {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        messages.error(request, f"Error processing videos: {str(e)}")
    
    return redirect('list_all_videos')

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
    
    return redirect('list_all_videos')

@staff_member_required
def actions(request):
    """View for the actions page"""
    frontend = get_current_frontend(request)
    unchecked_count = Video.objects.filter(
        frontend=frontend,
        checked_for_relevant_subtitles=False
    ).exclude(
        status=VideoStatus.NOT_RELEVANT
    ).count()
    context = {
        'unchecked_count': unchecked_count,
        'frontend': frontend
    }
    return render(request, 'actions.html', context)

@staff_member_required
@require_http_methods(["POST"])
def bulk_check_subtitles(request):
    """View to check subtitles for all videos that haven't been checked yet"""
    try:
        # Get all videos that haven't been checked for Arabic subtitles and aren't marked as not relevant
        videos = Video.objects.filter(
            checked_for_relevant_subtitles=False
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
                video.checked_for_relevant_subtitles = True
                video.save()
                processed_count += 1
            except Exception as e:
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
                # Mark as checked even if there was an error to avoid retrying
                video.checked_for_relevant_subtitles = True
                video.save()
        
        if processed_count > 0:
            messages.success(request, f"Successfully checked subtitles for {processed_count} videos.")
        if error_count > 0:
            messages.error(request, f"Failed to check subtitles for {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        messages.error(request, f"Error checking subtitles: {str(e)}")
    
    return redirect('actions')

@staff_member_required
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

@staff_member_required
def import_playlist_videos(request):
    """View to import videos from a YouTube playlist"""
    frontend = get_current_frontend(request)
    if request.method == 'POST':
        playlist_url = request.POST.get('playlist_url')
        import_all = request.POST.get('import_all') == 'true'
        context = {'playlist_url': playlist_url}
        
        if playlist_url:
            try:
                youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
                
                # Extract playlist ID from URL
                playlist_id = None
                if 'list=' in playlist_url:
                    playlist_id = playlist_url.split('list=')[1].split('&')[0]
                elif 'youtube.com/playlist' in playlist_url:
                    playlist_id = playlist_url.split('/playlist/')[1].split('?')[0]
                
                if not playlist_id:
                    context['error'] = "Invalid playlist URL. Please provide a valid YouTube playlist URL."
                    return render(request, 'import_playlist_videos.html', context)
                
                # Get playlist details
                playlist_response = youtube.playlists().list(
                    id=playlist_id,
                    part='snippet'
                ).execute()
                
                if not playlist_response.get('items'):
                    context['error'] = "Playlist not found. Please check the URL and try again."
                    return render(request, 'import_playlist_videos.html', context)
                
                playlist_title = playlist_response['items'][0]['snippet']['title']
                
                # Get total number of videos in the playlist
                playlist_items_response = youtube.playlistItems().list(
                    playlistId=playlist_id,
                    part='contentDetails',
                    maxResults=1
                ).execute()
                
                total_videos = playlist_items_response['pageInfo']['totalResults']
                
                # Get existing video IDs from our database
                existing_video_ids = set(Video.objects.filter(frontend=frontend).values_list('youtube_id', flat=True))
                
                # Get the most recent video ID we've processed for this playlist
                last_processed_video = Video.objects.filter(
                    frontend=frontend,
                    comment__startswith=f'Imported from playlist {playlist_id}'
                ).order_by('-youtube_id').first()
                
                # Get videos from the playlist
                next_page_token = None
                imported_count = 0
                remaining_videos = total_videos
                batch_size = 100
                found_last_processed = False
                
                while True:
                    playlist_items_response = youtube.playlistItems().list(
                        playlistId=playlist_id,
                        part='contentDetails,snippet',
                        maxResults=50,
                        pageToken=next_page_token
                    ).execute()
                    
                    # Create Video objects for each video that doesn't exist yet
                    for item in playlist_items_response['items']:
                        video_id = item['contentDetails']['videoId']
                        
                        # If we've found our last processed video, we can start importing
                        if last_processed_video and video_id == last_processed_video.youtube_id:
                            found_last_processed = True
                            continue
                            
                        # If we haven't found our last processed video yet, skip
                        if last_processed_video and not found_last_processed:
                            continue
                        
                        if video_id not in existing_video_ids:
                            Video.objects.get_or_create(
                                youtube_id=video_id,
                                frontend=frontend,
                                defaults={
                                    'status': VideoStatus.NEEDS_REVIEW,
                                    'comment': f'Imported from playlist {playlist_id}: {playlist_title}',
                                    'youtube_title': item['snippet']['title']
                                }
                            )
                            imported_count += 1
                            existing_video_ids.add(video_id)
                        
                        remaining_videos -= 1
                        
                        # If we've imported the batch size and not importing all, stop
                        if imported_count >= batch_size and not import_all:
                            break
                    
                    if not import_all and imported_count >= batch_size:
                        break
                        
                    next_page_token = playlist_items_response.get('nextPageToken')
                    if not next_page_token:
                        break
                
                context['success'] = f"Successfully imported {imported_count} new videos from playlist '{playlist_title}'"
                if remaining_videos > 0:
                    context['remaining'] = remaining_videos
                    context['playlist_id'] = playlist_id
                    context['playlist_title'] = playlist_title
                
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
        
        return render(request, 'import_playlist_videos.html', context)
    
    return render(request, 'import_playlist_videos.html')

@staff_member_required
@require_http_methods(["GET"])
def export_snippets_csv(request, youtube_id):
    """View to export snippets as CSV"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        snippets = video.snippets.all().order_by('index')
        
        # Create the HttpResponse object with the appropriate CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{video.youtube_id}_snippets.csv"'
        
        # Create the CSV writer
        writer = csv.writer(response)
        
        # Write the header
        writer.writerow(['Index', 'Start Time', 'Duration', 'Content'])
        
        # Write the data
        for snippet in snippets:
            writer.writerow([
                snippet.index,
                snippet.start,
                snippet.duration,
                snippet.content
            ])
        
        return response
        
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
        return redirect('video_details', youtube_id=youtube_id)
    except Exception as e:
        messages.error(request, f"Error exporting snippets: {str(e)}")
        return redirect('video_details', youtube_id=youtube_id)

@staff_member_required
@require_http_methods(["POST"])
def update_video_priorities(request):
    """View to update priorities for all videos in the current filter"""
    try:
        # Get the current filter parameters
        status_filter = request.POST.get('status_filter', '')
        comment_filter = request.POST.get('comment_filter', '')
        frontend = get_current_frontend(request)
        
        # Get all videos matching the current filter
        videos = Video.objects.filter(frontend=frontend)
        
        if status_filter:
            videos = videos.filter(status=status_filter)
        if comment_filter:
            videos = videos.filter(comment__icontains=comment_filter)
        
        # Get the action (increase or decrease)
        action = request.POST.get('action')
        
        # Update priorities
        if action == 'increase':
            videos.update(priority=models.F('priority') + 1)
            messages.success(request, "Successfully increased priority for all videos in the current filter.")
        elif action == 'decrease':
            videos.update(priority=models.F('priority') - 1)
            messages.success(request, "Successfully decreased priority for all videos in the current filter.")
        
    except Exception as e:
        messages.error(request, f"Error updating priorities: {str(e)}")
    
    # Redirect back to the list view with the same filters
    redirect_url = reverse('list_all_videos')
    if status_filter:
        redirect_url += f"?status={status_filter}"
    if comment_filter:
        redirect_url += f"{'&' if status_filter else '?'}comment={comment_filter}"
    
    return redirect(redirect_url)

@staff_member_required
def search_videos(request):
    """View to search YouTube videos and automatically import them"""
    frontend = get_current_frontend(request)
    search_query = request.GET.get('q', '')
    
    # Set country and language based on frontend
    if frontend == Frontend.ARABIC:
        region_code = 'EG'
        language = 'ar'
    else:  # German
        region_code = 'DE'
        language = 'de'
    
    if search_query:
        try:
            youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
            
            # Get existing video IDs to exclude
            existing_video_ids = set(Video.objects.filter(frontend=frontend).values_list('youtube_id', flat=True))
            
            # Get the last page token used for this search query
            last_page_token = request.session.get(f'last_page_token_{search_query}', '')
            
            # Search for videos
            search_response = youtube.search().list(
                q=search_query,
                part='id,snippet',
                type='video',
                maxResults=10,
                regionCode=region_code,
                relevanceLanguage=language,
                pageToken=last_page_token
            ).execute()
            
            # Store the next page token for future searches
            next_page_token = search_response.get('nextPageToken')
            if next_page_token:
                request.session[f'last_page_token_{search_query}'] = next_page_token
            else:
                # If no more pages, reset to start from beginning
                request.session[f'last_page_token_{search_query}'] = ''
            
            imported_count = 0
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                if video_id not in existing_video_ids:
                    Video.objects.create(
                        youtube_id=video_id,
                        frontend=frontend,
                        status=VideoStatus.NEEDS_REVIEW,
                        comment=f'Imported from search: {search_query}',
                        youtube_title=item['snippet']['title']
                    )
                    imported_count += 1
            
            context = {
                'search_query': search_query,
                'imported_count': imported_count,
                'frontend': frontend
            }
            
        except Exception as e:
            context = {
                'error': str(e),
                'search_query': search_query,
                'frontend': frontend
            }
    else:
        context = {
            'frontend': frontend
        }
    
    return render(request, 'search_videos.html', context)
