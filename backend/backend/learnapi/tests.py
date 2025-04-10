from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from shared.models import Language, Video, Snippet, Word
from .models import UserProfile, VideoProgress, VocabPractice, SnippetPractice

class LearnApiTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test language
        self.language = Language.objects.create(
            code='en',
            name='English'
        )
        
        # Create test video
        self.video = Video.objects.create(
            youtube_id='test123',
            language=self.language,
            is_blacklisted=False,
            only_premium=False
        )
        
        # Create test snippet
        self.snippet = Snippet.objects.create(
            video=self.video,
            index=1,
            start=0.0,
            duration=5.0
        )
        
        # Create test word
        self.word = Word.objects.create(
            original_word='test',
            meanings=['meaning1', 'meaning2']
        )
        self.word.occurs_in_snippets.add(self.snippet)
        self.word.videos.add(self.video)

    def test_video_list_view(self):
        """Test the video list view"""
        # Test with existing language
        url = reverse('video-list', kwargs={'language_code': 'en'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['youtube_id'], 'test123')
        
        # Test with non-existent language
        url = reverse('video-list', kwargs={'language_code': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Test with blacklisted video
        self.video.is_blacklisted = True
        self.video.save()
        url = reverse('video-list', kwargs={'language_code': 'en'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_video_snippets_view(self):
        """Test the video snippets view"""
        # Test with existing video
        url = reverse('video-snippets', kwargs={'youtube_id': 'test123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['index'], 1)
        self.assertEqual(response.data[0]['start'], 0.0)
        self.assertEqual(response.data[0]['duration'], 5.0)
        
        # Test with non-existent video
        url = reverse('video-snippets', kwargs={'youtube_id': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_words_view(self):
        """Test the snippet words view"""
        # Test with existing video and snippet
        url = reverse('snippet-words', kwargs={
            'youtube_id': 'test123',
            'snippet_index': 1
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_word'], 'test')
        self.assertEqual(response.data[0]['meanings'], ['meaning1', 'meaning2'])
        
        # Test with non-existent video
        url = reverse('snippet-words', kwargs={
            'youtube_id': 'nonexistent',
            'snippet_index': 1
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test with non-existent snippet
        url = reverse('snippet-words', kwargs={
            'youtube_id': 'test123',
            'snippet_index': 999
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
