from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus, Tag, TagType
from .get_current_frontend import get_current_frontend

@staff_member_required
@require_http_methods(["POST"])
def enrich_video_metadata(request):
    """View to enrich video metadata using YouTube API"""
    print("Starting enrich_video_metadata view")  # Debug log
    frontend = get_current_frontend(request)
    try:
        print(f"Building YouTube API client for frontend: {frontend}")  # Debug log
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        
        # Get videos that are either live OR have snippets and translations generated
        # AND don't have a title set yet (to avoid unnecessary API calls)
        videos = Video.objects.filter(
            frontend=frontend,
            status__in=[VideoStatus.LIVE, VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED],
            youtube_title__isnull=True
        )
        
        print(f"Found {videos.count()} videos to process")  # Debug log
        
        processed_count = 0
        error_count = 0
        error_videos = []
        skipped_count = 0
        
        messages.info(request, f"Found {videos.count()} videos to process.")
        
        for video in videos:
            try:
                print(f"Processing video {video.youtube_id}")  # Debug log
                # Get video details from YouTube API
                video_response = youtube.videos().list(
                    id=video.youtube_id,
                    part='snippet,topicDetails,statistics'
                ).execute()
                
                if not video_response.get('items'):
                    print(f"Video {video.youtube_id} not found on YouTube")  # Debug log
                    error_count += 1
                    error_videos.append(f"{video.youtube_id} (Not found on YouTube)")
                    continue
                
                video_data = video_response['items'][0]
                snippet = video_data['snippet']
                statistics = video_data.get('statistics', {})
                topic_details = video_data.get('topicDetails', {})
                
                # Update video title and channel name
                video.youtube_title = snippet['title']
                video.channel_name = snippet['channelTitle']
                print(f"Updated title for {video.youtube_id}: {snippet['title']}")  # Debug log
                print(f"Updated channel name for {video.youtube_id}: {snippet['channelTitle']}")  # Debug log
                
                # Update view and like counts
                if 'statistics' in video_data:
                    video.video_views = int(video_data['statistics'].get('viewCount', 0))
                    video.video_likes = int(video_data['statistics'].get('likeCount', 0))
                    print(f"Updated stats for {video.youtube_id}: {video.video_views} views, {video.video_likes} likes")  # Debug log
                
                # Clear existing tags before adding new ones
                video.tags.clear()
                
                # Add YouTube tags
                if 'tags' in snippet:
                    for tag_name in snippet['tags']:
                        try:
                            tag, _ = Tag.objects.get_or_create(
                                name=tag_name.lower(),
                                defaults={'type': TagType.FROM_YOUTUBE}
                            )
                            video.tags.add(tag)
                            print(f"Added tag '{tag_name}' to {video.youtube_id}")  # Debug log
                        except Exception as e:
                            print(f"Error creating tag '{tag_name}': {str(e)}")  # Debug log
                            messages.warning(request, f"Error creating tag '{tag_name}': {str(e)}")
                
                # Add topic IDs as tags
                if 'topicIds' in topic_details:
                    for topic_id in topic_details['topicIds']:
                        try:
                            tag, _ = Tag.objects.get_or_create(
                                name=f"topic:{topic_id}",
                                defaults={'type': TagType.FROM_YOUTUBE}
                            )
                            video.tags.add(tag)
                            print(f"Added topic tag '{topic_id}' to {video.youtube_id}")  # Debug log
                        except Exception as e:
                            print(f"Error creating topic tag '{topic_id}': {str(e)}")  # Debug log
                            messages.warning(request, f"Error creating topic tag '{topic_id}': {str(e)}")
                
                # Add relevant topic IDs as tags
                if 'relevantTopicIds' in topic_details:
                    for topic_id in topic_details['relevantTopicIds']:
                        try:
                            tag, _ = Tag.objects.get_or_create(
                                name=f"relevant_topic:{topic_id}",
                                defaults={'type': TagType.FROM_YOUTUBE}
                            )
                            video.tags.add(tag)
                            print(f"Added relevant topic tag '{topic_id}' to {video.youtube_id}")  # Debug log
                        except Exception as e:
                            print(f"Error creating relevant topic tag '{topic_id}': {str(e)}")  # Debug log
                            messages.warning(request, f"Error creating relevant topic tag '{topic_id}': {str(e)}")
                
                video.save()
                processed_count += 1
                print(f"Successfully processed video {video.youtube_id}")  # Debug log
                
            except Exception as e:
                print(f"Error processing video {video.youtube_id}: {str(e)}")  # Debug log
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
                messages.error(request, f"Error processing video {video.youtube_id}: {str(e)}")
        
        # Get count of videos that were skipped because they already had titles
        skipped_count = Video.objects.filter(
            frontend=frontend,
            status__in=[VideoStatus.LIVE, VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED],
            youtube_title__isnull=False
        ).count()
        
        print(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}")  # Debug log
        
        if processed_count > 0:
            messages.success(request, f"Successfully enriched metadata for {processed_count} videos.")
        if skipped_count > 0:
            messages.info(request, f"Skipped {skipped_count} videos that already had metadata.")
        if error_count > 0:
            messages.error(request, f"Failed to process {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        print(f"Error in enrich_video_metadata: {str(e)}")  # Debug log
        messages.error(request, f"Error enriching video metadata: {str(e)}")
    
    return redirect('cms:actions')
