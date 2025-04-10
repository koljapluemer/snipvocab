from django.shortcuts import render, redirect
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

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
                            defaults={'status': VideoStatus.NEEDS_REVIEW}
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
    # Get videos that need review
    videos = Video.objects.filter(status=VideoStatus.NEEDS_REVIEW)
    
    # Get page number from request
    page_number = request.GET.get('page', 1)
    
    # Paginate the videos
    paginator = Paginator(videos, 20)
    page_obj = paginator.get_page(page_number)
    
    # Process each video to get available languages
    for video in page_obj:
        try:
            # Get available languages using youtube_transcript_api
            available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
            video.available_subtitle_languages = [lang.language_code for lang in available_languages]
            video.save()
        except Exception as e:
            # If no transcripts available, set empty list
            video.available_subtitle_languages = []
            video.save()
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj
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
