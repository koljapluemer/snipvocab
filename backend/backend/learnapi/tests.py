from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from shared.models import Video, Snippet, Word, VideoStatus, Meaning
from .models import UserProfile, VideoProgress, VocabPractice, SnippetPractice
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
import json

class LearnApiTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        

        
        # Create test video
        self.video = Video.objects.create(
            youtube_id='test123',
            status=VideoStatus.LIVE
        )
        
        # Create another video that's not live
        self.non_live_video = Video.objects.create(
            youtube_id='test456',
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
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a word that's due for review
        self.due_word = Word.objects.create(
            original_word='due'
        )
        self.due_word.occurs_in_snippets.add(self.snippet)
        self.due_word.videos.add(self.video)
        
        # Create meaning for due word
        self.due_meaning = Meaning.objects.create(
            word=self.due_word,
            en='due meaning',
            creation_method='manual'
        )
        
        # Create VocabPractice for due word
        self.due_practice = VocabPractice.objects.create(
            user=self.user,
            word=self.due_word,
            state='Review',
            due=datetime.now(timezone.utc) - timedelta(days=1),  # Due yesterday
            last_review=datetime.now(timezone.utc) - timedelta(days=2)
        )
        
        # Create a word that's not due
        self.not_due_word = Word.objects.create(
            original_word='not_due'
        )
        self.not_due_word.occurs_in_snippets.add(self.snippet)
        self.not_due_word.videos.add(self.video)
        
        # Create meaning for not due word
        self.not_due_meaning = Meaning.objects.create(
            word=self.not_due_word,
            en='not due meaning',
            creation_method='manual'
        )
        
        # Create VocabPractice for not due word
        self.not_due_practice = VocabPractice.objects.create(
            user=self.user,
            word=self.not_due_word,
            state='Review',
            due=datetime.now(timezone.utc) + timedelta(days=1),  # Due tomorrow
            last_review=datetime.now(timezone.utc)
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

    def test_snippet_due_words_view(self):
        """Test getting due words for a snippet"""
        url = reverse('snippet-due-words', kwargs={
            'youtube_id': 'test123',
            'index': 1,
            'user_id': self.user.id
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        
        # Should get two words:
        # 1. The new word 'test' (never seen before)
        # 2. The due word 'due' (due for review)
        self.assertEqual(len(data), 2)
        
        # Check the new word
        new_word = next(w for w in data if w['original_word'] == 'test')
        self.assertEqual(new_word['original_word'], 'test')
        self.assertEqual(len(new_word['meanings']), 1)
        self.assertEqual(new_word['meanings'][0]['en'], 'test meaning')
        self.assertTrue(new_word['isDue'])
        self.assertTrue(new_word['isNew'])
        self.assertFalse(new_word['isFavorite'])
        self.assertFalse(new_word['isBlacklisted'])
        
        # Check the due word
        due_word = next(w for w in data if w['original_word'] == 'due')
        self.assertEqual(due_word['original_word'], 'due')
        self.assertEqual(len(due_word['meanings']), 1)
        self.assertEqual(due_word['meanings'][0]['en'], 'due meaning')
        self.assertTrue(due_word['isDue'])
        self.assertFalse(due_word['isNew'])
        self.assertFalse(due_word['isFavorite'])
        self.assertFalse(due_word['isBlacklisted'])
        
        # The not_due word should not be in the response
        self.assertFalse(any(w['original_word'] == 'not_due' for w in data))

    def test_snippet_due_words_not_found_video(self):
        """Test getting due words for a non-existent video"""
        url = reverse('snippet-due-words', kwargs={
            'youtube_id': 'nonexistent',
            'index': 1,
            'user_id': self.user.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_due_words_not_found_snippet(self):
        """Test getting due words for a non-existent snippet"""
        url = reverse('snippet-due-words', kwargs={
            'youtube_id': 'test123',
            'index': 999,
            'user_id': self.user.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_due_words_not_found_user(self):
        """Test getting due words for a non-existent user"""
        url = reverse('snippet-due-words', kwargs={
            'youtube_id': 'test123',
            'index': 1,
            'user_id': 999
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snippet_due_words_non_live_video(self):
        """Test getting due words for a non-live video"""
        url = reverse('snippet-due-words', kwargs={
            'youtube_id': 'test456',
            'index': 1,
            'user_id': self.user.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
