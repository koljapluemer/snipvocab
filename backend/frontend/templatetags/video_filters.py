from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_left_position(index, snippets):
    if index == 0:
        return 0
    total_duration = snippets.last().end_time
    previous_snippet = snippets[index - 1]
    return (previous_snippet.end_time / total_duration) * 100

@register.filter
def get_width(snippet, snippets):
    total_duration = snippets.last().end_time
    return ((snippet.end_time - snippet.start_time) / total_duration) * 100

@register.filter
def get_difficulty_color(snippet, index):
    difficulty = snippet.perceived_difficulty
    if difficulty is None:
        # Alternate between light and dark gray for unrated snippets
        return 'hsl(0, 0%, 85%)' if index % 2 == 0 else 'hsl(0, 0%, 75%)'
    
    # Map difficulty to HSL color space
    # 0 -> 120 (green), 50 -> yellow, 100 -> 0 (red)
    hue = difficulty * 1.2  # 0 is green, 120 is red
    saturation = 100
    lightness = 45  # Keep it dark enough for good contrast
    
    return f'hsl({hue}, {saturation}%, {lightness}%)'

@register.filter
def get_end_time(snippet):
    return snippet.end_time

@register.filter
def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}:{remaining_seconds:02d}" 