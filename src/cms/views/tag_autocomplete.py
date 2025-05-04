@staff_member_required
def tag_autocomplete(request):
    """View to provide tag suggestions for autocomplete"""
    query = request.GET.get('q', '').strip().lower()
    
    if len(query) < 2:
        return JsonResponse({'tags': []})
    
    # Search for tags that start with the query
    tags = Tag.objects.filter(
        Q(name__istartswith=query) | Q(name__icontains=f" {query}")
    ).values('name')[:10]
    
    return JsonResponse({'tags': list(tags)})
