from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from learnapi.models import VideoProgress, VocabPractice, SnippetPractice
from django.db.models import Count
import json

def dashboard(request):
    # Get 3 most recently practiced videos
    recent_videos = VideoProgress.objects.filter(
        user=request.user
    ).select_related('video').order_by('-last_practiced')[:3]

    # Attach last_practiced directly to each video object
    for vp in recent_videos:
        vp.video.last_practiced = vp.last_practiced

    # Get practice data for last 10 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=10)
    
    # Vocabulary practice data
    vocab_data = VocabPractice.objects.filter(
        user=request.user,
        updated__range=(start_date, end_date)
    ).extra(
        select={'date': 'DATE(updated)'}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Snippet practice data
    snippet_data = SnippetPractice.objects.filter(
        user=request.user,
        updated__range=(start_date, end_date)
    ).extra(
        select={'date': 'DATE(updated)'}
    ).values('date').annotate(
        count=Count('id', distinct=True)
    ).order_by('date')
    
    # Prepare data for charts
    vocab_dates = []
    vocab_counts = []
    snippet_dates = []
    snippet_counts = []
    
    # Fill in all dates in the range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        vocab_dates.append(date_str)
        snippet_dates.append(date_str)
        
        # Find matching data points - date is already a string in YYYY-MM-DD format
        vocab_count = next((item['count'] for item in vocab_data if item['date'] == date_str), 0)
        snippet_count = next((item['count'] for item in snippet_data if item['date'] == date_str), 0)
        
        vocab_counts.append(vocab_count)
        snippet_counts.append(snippet_count)
        
        current_date += timedelta(days=1)
    
    context = {
        'recent_videos': [vp.video for vp in recent_videos],
        'vocab_dates': json.dumps(vocab_dates),
        'vocab_counts': json.dumps(vocab_counts),
        'snippet_dates': json.dumps(snippet_dates),
        'snippet_counts': json.dumps(snippet_counts),
    }
    
    return render(request, 'frontend/dashboard/dashboard.html', context) 