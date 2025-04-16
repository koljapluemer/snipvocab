from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from shared.models import Word
from learnapi.models import VocabPractice

class LearningEventsViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test word
        self.word = Word.objects.create(
            original_word='testword'
        )
        
        # Test data
        self.valid_event = {
            'eventType': 'GOOD',
            'originalWord': 'testword',
            'timestamp': int(timezone.now().timestamp() * 1000)
        }

    def test_valid_learning_event_creates_vocab_practice(self):
        """Test that a valid learning event creates a VocabPractice with correct initial state"""
        response = self.client.post('/api/learn/learning-events/', [self.valid_event], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify VocabPractice was created with correct relationships
        practice = VocabPractice.objects.get(user=self.user, word=self.word)
        self.assertEqual(practice.user, self.user)
        self.assertEqual(practice.word, self.word)
        self.assertEqual(practice.state, 'Learning')
        self.assertIsNotNone(practice.step)
        self.assertIsNotNone(practice.stability)
        self.assertIsNotNone(practice.difficulty)
        self.assertIsNotNone(practice.due)
        self.assertIsNotNone(practice.last_review)
        self.assertFalse(practice.is_blacklisted)
        self.assertFalse(practice.is_favorite)
