from django.shortcuts import render
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def list_channel_videos(request):
    """View to list all videos from a YouTube channel"""
    username = request.GET.get('channel_id')
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
            
            # Get videos from the uploads playlist
            videos = []
            next_page_token = None
            
            while True:
                playlist_response = youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='snippet,contentDetails',
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                
                if not playlist_response.get('items'):
                    context['error'] = "No videos found in this channel's uploads playlist."
                    return render(request, 'list_channel_videos.html', context)
                
                for item in playlist_response['items']:
                    video_id = item['contentDetails']['videoId']
                    
                    # Get video details
                    video_response = youtube.videos().list(
                        id=video_id,
                        part='snippet,contentDetails'
                    ).execute()
                    
                    if not video_response.get('items'):
                        continue
                        
                    video = video_response['items'][0]
                    # Check if video exists in our database
                    try:
                        db_video = Video.objects.get(youtube_id=video_id)
                        current_status = db_video.status
                    except Video.DoesNotExist:
                        current_status = None
                        
                    videos.append({
                        'id': video_id,
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],
                        'thumbnail': video['snippet']['thumbnails']['high']['url'],
                        'published_at': video['snippet']['publishedAt'],
                        'duration': video['contentDetails']['duration'],
                        'current_status': current_status
                    })
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            if not videos:
                context['error'] = "No videos could be loaded from this channel."
            else:
                context['videos'] = videos
                
        except Exception as e:
            error_message = str(e)
            if "quota" in error_message.lower():
                context['error'] = "YouTube API quota exceeded. Please try again later."
            elif "invalid" in error_message.lower():
                context['error'] = "Invalid username format. Please check and try again."
            else:
                context['error'] = f"An error occurred while fetching videos: {error_message}"
            
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
