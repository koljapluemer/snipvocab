


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
            
            # Search for videos with captions
            search_response = youtube.search().list(
                q=search_query,
                part='id,snippet',
                type='video',
                maxResults=10,
                regionCode=region_code,
                relevanceLanguage=language,
                pageToken=last_page_token,
                videoCaption='any'  # Only include videos with captions
            ).execute()
            
            # Store the next page token for future searches
            next_page_token = search_response.get('nextPageToken')
            if next_page_token:
                request.session[f'last_page_token_{search_query}'] = next_page_token
            else:
                # If no more pages, reset to start from beginning
                request.session[f'last_page_token_{search_query}'] = ''
            
            # Get or create tag for this search query
            tag, _ = Tag.objects.get_or_create(name=search_query.lower())
            
            imported_count = 0
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                if video_id not in existing_video_ids:
                    video = Video.objects.create(
                        youtube_id=video_id,
                        frontend=frontend,
                        status=VideoStatus.NEEDS_REVIEW,
                        comment=f'Imported from search: {search_query}',
                        youtube_title=item['snippet']['title']
                    )
                    # Add the tag to the video
                    video.tags.add(tag)
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
