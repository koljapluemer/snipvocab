@staff_member_required
@require_http_methods(["GET"])
def export_snippets_csv(request, youtube_id):
    """View to export snippets as CSV"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        snippets = video.snippets.all().order_by('index')
        
        # Create the HttpResponse object with the appropriate CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{video.youtube_id}_snippets.csv"'
        
        # Create the CSV writer
        writer = csv.writer(response)
        
        # Write the header
        writer.writerow(['Index', 'Start Time', 'Duration', 'Content'])
        
        # Write the data
        for snippet in snippets:
            writer.writerow([
                snippet.index,
                snippet.start,
                snippet.duration,
                snippet.content
            ])
        
        return response
        
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
        return redirect('video_details', youtube_id=youtube_id)
    except Exception as e:
        messages.error(request, f"Error exporting snippets: {str(e)}")
        return redirect('video_details', youtube_id=youtube_id)
