from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages

from shared.models import Tag, TagType

@staff_member_required
def manage_tags(request, tag_id=None):
    """View to manage tags - add, edit, and list"""
    tag = None
    if tag_id:
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            messages.error(request, "Tag not found.")
            return redirect('manage_tags')

    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')

        if not name:
            messages.error(request, "Tag name is required.")
            return redirect('manage_tags')

        try:
            if tag:
                # Update existing tag
                tag.name = name
                tag.type = type
                tag.save()
                messages.success(request, "Tag updated successfully.")
            else:
                # Create new tag
                Tag.objects.create(name=name, type=type)
                messages.success(request, "Tag created successfully.")
            return redirect('manage_tags')
        except Exception as e:
            messages.error(request, f"Error saving tag: {str(e)}")
            return redirect('manage_tags')

    # Get all tags for the list
    tags = Tag.objects.all().order_by('name')
    
    context = {
        'tag': tag,
        'tags': tags,
        'tag_types': TagType.choices
    }
    
    return render(request, 'tag_management.html', context)
