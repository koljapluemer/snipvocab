from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from shared.models import Word, Meaning
from .models import VocabPractice
from datetime import datetime, timezone
import json

class LearningEventsViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test word
        self.word = Word.objects.create(original_word='testword')
        Meaning.objects.create(word=self.word, en='test meaning')
        
        # Setup client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Test data
        self.valid_event = {
            'eventType': 2,  # GOOD (Rating.Good == 3)
            'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
            'originalWord': 'testword'
        }
        
        self.url = reverse('learning-events')
    
    def test_single_valid_event(self):
        """Test processing a single valid learning event"""
        response = self.client.post(
            self.url,
            [self.valid_event],
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['success'])
        self.assertIsNotNone(response.data[0]['newDueDate'])
        
        # Verify VocabPractice was created
        practice = VocabPractice.objects.get(user=self.user, word=self.word)
        self.assertIsNotNone(practice.due)
        self.assertIsNotNone(practice.last_review)
        self.assertEqual(practice.state, 'Learning')
    
    def test_multiple_valid_events(self):
        """Test processing multiple valid learning events"""
        events = [
            self.valid_event,
            {
                'eventType': 3,  # EASY (Rating.Easy == 4)
                'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
                'originalWord': 'testword'
            }
        ]
        
        response = self.client.post(
            self.url,
            events,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(all(r['success'] for r in response.data))
    
    def test_invalid_event_type(self):
        """Test processing an event with invalid event type"""
        invalid_event = {
            'eventType': 999,  # Invalid type
            'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
            'originalWord': 'testword'
        }
        
        response = self.client.post(
            self.url,
            [invalid_event],
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]['success'])
    
    def test_missing_original_word(self):
        """Test processing an event with missing original word"""
        invalid_event = {
            'eventType': 2,  # GOOD (Rating.Good == 3)
            'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000)
        }
        
        response = self.client.post(
            self.url,
            [invalid_event],
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]['success'])
    
    def test_nonexistent_word(self):
        """Test processing an event for a word that doesn't exist"""
        invalid_event = {
            'eventType': 2,  # GOOD (Rating.Good == 3)
            'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
            'originalWord': 'nonexistentword'
        }
        
        response = self.client.post(
            self.url,
            [invalid_event],
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]['success'])
    
    def test_invalid_request_format(self):
        """Test sending invalid request format (not a list)"""
        response = self.client.post(
            self.url,
            self.valid_event,  # Send single object instead of list
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
    
    def test_unauthorized_access(self):
        """Test accessing endpoint without authentication"""
        client = APIClient()  # Unauthenticated client
        response = client.post(
            self.url,
            [self.valid_event],
            format='json'
        )
        
        self.assertEqual(response.status_code, 401)
