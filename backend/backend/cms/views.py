from django.shortcuts import render
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

def list_channel_videos(request):
    """View to list all videos from a YouTube channel"""
    username = request.GET.get('channel_id')
    page_number = request.GET.get('page', 1)
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
                return render(request, 'list_channel_videos.html', context)
                
            channel_id = channel_response['items'][0]['id']['channelId']
            
            # Get channel's uploads playlist ID
            channel_response = youtube.channels().list(
                id=channel_id,
                part='contentDetails,snippet'
            ).execute()
            
            if not channel_response.get('items'):
                context['error'] = f"Channel '@{username}' not found. Please check the username and try again."
                return render(request, 'list_channel_videos.html', context)
                
            channel = channel_response['items'][0]
            context['channel_title'] = channel['snippet']['title']
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
            
            # Get first 15 videos from the uploads playlist
            videos = []
            playlist_response = youtube.playlistItems().list(
                playlistId=uploads_playlist_id,
                part='snippet,contentDetails',
                maxResults=15,
                pageToken=None
            ).execute()
            
            if not playlist_response.get('items'):
                context['error'] = "No videos found in this channel's uploads playlist."
                return render(request, 'list_channel_videos.html', context)
            
            # Get video IDs for batch processing
            video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]
            
            # Get video details in a single batch request
            video_response = youtube.videos().list(
                id=','.join(video_ids),
                part='snippet,contentDetails'
            ).execute()
            
            # Create a mapping of video IDs to their details
            video_details = {item['id']: item for item in video_response.get('items', [])}
            
            # Process each video
            for item in playlist_response['items']:
                video_id = item['contentDetails']['videoId']
                video = video_details.get(video_id)
                
                if not video:
                    continue
                
                # Get available captions for this video
                try:
                    caption_response = youtube.captions().list(
                        part='snippet',
                        videoId=video_id
                    ).execute()
                    
                    available_languages = []
                    if caption_response.get('items'):
                        available_languages = [item['snippet']['language'] for item in caption_response['items']]
                except Exception as caption_error:
                    # If caption API fails, continue without captions
                    available_languages = []
                    print(f"Caption API error for video {video_id}: {str(caption_error)}")
                
                # Check if video exists in our database
                try:
                    db_video = Video.objects.get(youtube_id=video_id)
                    current_status = db_video.status
                except Video.DoesNotExist:
                    # Create new video with default status
                    db_video = Video.objects.create(
                        youtube_id=video_id,
                        status=VideoStatus.NEEDS_REVIEW,
                        available_subtitle_languages=available_languages
                    )
                    current_status = VideoStatus.NEEDS_REVIEW
                
                videos.append({
                    'id': video_id,
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'thumbnail': video['snippet']['thumbnails']['high']['url'],
                    'published_at': video['snippet']['publishedAt'],
                    'duration': video['contentDetails']['duration'],
                    'current_status': current_status,
                    'available_languages': available_languages
                })
            
            if not videos:
                context['error'] = "No videos could be loaded from this channel."
            else:
                # Create a simple paginator for the 15 videos
                paginator = Paginator(videos, 15)
                page_obj = paginator.get_page(page_number)
                context['videos'] = page_obj
                context['page_obj'] = page_obj
                
        except Exception as e:
            error_message = str(e)
            error_details = {
                'message': error_message,
                'type': type(e).__name__,
                'args': e.args
            }
            
            if hasattr(e, 'error_details'):
                error_details['api_error'] = e.error_details
            
            context['error'] = f"An error occurred while fetching videos. Details: {error_details}"
            
    return render(request, 'list_channel_videos.html', context)

@require_http_methods(["POST"])
def update_video_status(request, youtube_id):
    """API endpoint to update video status"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        new_status = request.POST.get('status')
        
        if new_status not in [status[0] for status in VideoStatus.choices]:
            return JsonResponse({'error': 'Invalid status'}, status=400)
            
        video.status = new_status
        video.save()
        
        return JsonResponse({'status': 'success'})
        
    except Video.DoesNotExist:
        return JsonResponse({'error': 'Video not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
