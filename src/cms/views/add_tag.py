from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from shared.models import Video, Tag, TagType

@staff_member_required
@require_http_methods(["POST"])
def add_tag(request, youtube_id):
    """View to add a manual tag to a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        tag_name = request.POST.get('tag_name', '').strip()
        
        if not tag_name:
            messages.error(request, "Tag name cannot be empty.")
            return redirect('cms:video_details', youtube_id=youtube_id)
        
        # Get or create the tag (only manual tags can be created this way)
        tag, created = Tag.objects.get_or_create(
            name=tag_name.lower(),
            defaults={'type': TagType.MANUAL}
        )
        
        # Add the tag to the video
        video.tags.add(tag)
        
        if created:
            messages.success(request, f"Created and added new tag '{tag.name}' to video.")
        else:
            messages.success(request, f"Added existing tag '{tag.name}' to video.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error adding tag: {str(e)}")
    
    return redirect('cms:video_details', youtube_id=youtube_id)
