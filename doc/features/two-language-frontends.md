# Two-Language Frontends

## Overview
The application supports two language frontends: Arabic (ar) and German (de). This document explains how the language framework is implemented across the frontend and backend.

## Frontend Implementation

### Environment Configuration
- Language is configured via `VITE_APP_LANG` environment variable
- Valid values: 'AR' or 'DE' (case-insensitive)
- Default: 'AR' if not specified

### API Integration
- All video-related API calls automatically include the language parameter
- Language is passed as a query parameter: `?lang=AR` or `?lang=DE`
- Frontend validates that `VITE_APP_LANG` is set before making API calls

## Backend Implementation

### Language Enum
```python
class Frontend(models.TextChoices):
    GERMAN = 'de', '🇩🇪'
    ARABIC = 'ar', '🇪🇬'
```

### Video Filtering
- All video list endpoints filter by `Video.frontend` field
- Language parameter is converted to lowercase before enum lookup
- Default language is 'ar' if not specified

### Error Handling
- Invalid language codes return 400 Bad Request
- Error message includes list of valid language options
- Logging includes language context for debugging

## API Endpoints
All video list endpoints support the `lang` parameter:
- `GET /learn/videos/` - All videos
- `GET /learn/videos/new/` - Newest videos
- `GET /learn/videos/popular/` - Most viewed videos
- `GET /learn/videos/tag/<tag_name>/` - Videos by tag
- `GET /learn/videos/onboarding/` - Onboarding videos

## Best Practices
1. Always include language parameter in video-related API calls
2. Use environment variables for language configuration
3. Handle language validation errors gracefully
4. Log language context for debugging
5. Maintain consistent language handling across all endpoints
