from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from frontend.models import VideoProgress, VocabPractice

@staff_member_required
def user_statistics(request):
    """View to show user statistics and activity"""
    # Get date range for charts (last 7 days)
    today = timezone.now().date()
    date_range = [today - timedelta(days=i) for i in range(7)]
    date_range.reverse()
    
    # Total users
    total_users = User.objects.count()
    
    # Users logged in today
    users_logged_in_today = User.objects.filter(
        last_login__date=today
    ).count()
    
    # New registrations today
    new_registrations_today = User.objects.filter(
        date_joined__date=today
    ).count()
    
    # Videos practiced today
    videos_practiced_today = VideoProgress.objects.filter(
        last_practiced__date=today
    ).count()
    
    # Words practiced today
    words_practiced_today = VocabPractice.objects.filter(
        last_review__date=today
    ).count()
    
    # Most popular videos (all time)
    popular_videos = VideoProgress.objects.values(
        'video__youtube_id', 'video__youtube_title'
    ).annotate(
        practice_count=Count('id')
    ).order_by('-practice_count')[:10]
    
    # Most popular videos today
    popular_videos_today = VideoProgress.objects.filter(
        last_practiced__date=today
    ).values(
        'video__youtube_id', 'video__youtube_title'
    ).annotate(
        practice_count=Count('id')
    ).order_by('-practice_count')[:10]
    
    # Daily login data for chart
    daily_logins = []
    daily_registrations = []
    daily_video_practices = []
    daily_word_practices = []
    
    for date in date_range:
        # Logins
        logins = User.objects.filter(
            last_login__date=date
        ).count()
        daily_logins.append(logins)
        
        # Registrations
        registrations = User.objects.filter(
            date_joined__date=date
        ).count()
        daily_registrations.append(registrations)
        
        # Video practices
        video_practices = VideoProgress.objects.filter(
            last_practiced__date=date
        ).count()
        daily_video_practices.append(video_practices)
        
        # Word practices
        word_practices = VocabPractice.objects.filter(
            last_review__date=date
        ).count()
        daily_word_practices.append(word_practices)
    
    context = {
        'total_users': total_users,
        'users_logged_in_today': users_logged_in_today,
        'new_registrations_today': new_registrations_today,
        'videos_practiced_today': videos_practiced_today,
        'words_practiced_today': words_practiced_today,
        'popular_videos': popular_videos,
        'popular_videos_today': popular_videos_today,
        'date_range': [date.strftime('%Y-%m-%d') for date in date_range],
        'daily_logins': daily_logins,
        'daily_registrations': daily_registrations,
        'daily_video_practices': daily_video_practices,
        'daily_word_practices': daily_word_practices,
    }
    
    return render(request, 'user_statistics.html', context)
