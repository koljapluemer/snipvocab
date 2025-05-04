from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.conf import settings
from googleapiclient.discovery import build

from shared.models import Video, Frontend, VideoStatus
from .get_current_frontend import get_current_frontend

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
