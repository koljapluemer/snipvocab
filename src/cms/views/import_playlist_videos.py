
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
