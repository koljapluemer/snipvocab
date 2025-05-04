from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.conf import settings
from googleapiclient.discovery import build

from shared.models import Video, Frontend, VideoStatus, Tag
from .get_current_frontend import get_current_frontend

@staff_member_required
def search_videos(request):
    """View to search YouTube videos and automatically import them"""
    frontend = get_current_frontend(request)
    search_query = request.GET.get('q', '')
    short_videos = request.GET.get('short_videos', False) == 'on'
    
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
            
            # Build search parameters
            search_params = {
                'q': search_query,
                'part': 'id,snippet',
                'type': 'video',
                'maxResults': 10,
                'regionCode': region_code,
                'relevanceLanguage': language,
                'pageToken': last_page_token,
                'videoCaption': 'closedCaption',  # Only include videos with closed captions
            }
            
            # Add short videos filter if requested
            if short_videos:
                search_params['videoDuration'] = 'short'
            
            # Search for videos
            search_response = youtube.search().list(**search_params).execute()
            
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
                'frontend': frontend,
                'short_videos': short_videos
            }
            
        except Exception as e:
            context = {
                'error': str(e),
                'search_query': search_query,
                'frontend': frontend,
                'short_videos': short_videos
            }
    else:
        context = {
            'frontend': frontend,
            'short_videos': short_videos
        }
    
    return render(request, 'search_videos.html', context)
