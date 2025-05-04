
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
