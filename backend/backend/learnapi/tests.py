from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from shared.models import Language, Video, Snippet, Word, VideoStatus, Meaning
from .models import UserProfile, VideoProgress, VocabPractice, SnippetPractice
import json

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
            status=VideoStatus.LIVE
        )
        
        # Create another video that's not live
        self.non_live_video = Video.objects.create(
            youtube_id='test456',
            language=self.language,
            status=VideoStatus.NEEDS_REVIEW
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
            original_word='test'
        )
        self.word.occurs_in_snippets.add(self.snippet)
        self.word.videos.add(self.video)
        
        # Create test meaning
        self.meaning = Meaning.objects.create(
            word=self.word,
            en='test meaning',
            creation_method='manual'
        )

    def test_video_list_view(self):
        """Test the video list view returns only live video IDs"""
        url = reverse('video-list')
        response = self.client.get(url)
        
        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response format is a list
        self.assertIsInstance(response.data, list)
        
        # Check only live video is returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'test123')
        
        # Check non-live video is not returned
        self.assertNotIn('test456', response.data)

    def test_video_snippets_view(self):
        """Test the video snippets view"""
        # Test with existing video
        url = reverse('video-snippets', kwargs={'youtube_id': 'test123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['index'], 1)
        self.assertEqual(response.data[0]['start_time'], -1)  # start - 1
        self.assertEqual(response.data[0]['end_time'], 6)     # start + duration + 1
        
        # Test with non-existent video
        url = reverse('video-snippets', kwargs={'youtube_id': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_details_view(self):
        """Test the snippet details view"""
        url = reverse('snippet-details', kwargs={
            'youtube_id': 'test123',
            'index': 1
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        
        # Check snippet details
        self.assertEqual(data['video_id'], 'test123')
        self.assertEqual(data['index'], 1)
        self.assertEqual(data['start_time'], -1)  # start - 1
        self.assertEqual(data['end_time'], 6)     # start + duration + 1
        
        # Check words
        self.assertEqual(len(data['words']), 1)
        word = data['words'][0]
        self.assertEqual(word['original_word'], 'test')
        self.assertEqual(len(word['meanings']), 1)
        self.assertEqual(word['meanings'][0]['en'], 'test meaning')

    def test_snippet_details_not_found_video(self):
        """Test getting details for a non-existent video"""
        url = reverse('snippet-details', kwargs={
            'youtube_id': 'nonexistent',
            'index': 1
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_details_not_found_snippet(self):
        """Test getting details for a non-existent snippet index"""
        url = reverse('snippet-details', kwargs={
            'youtube_id': 'test123',
            'index': 999
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_details_non_live_video(self):
        """Test getting details for a non-live video"""
        url = reverse('snippet-details', kwargs={
            'youtube_id': 'test456',
            'index': 1
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
