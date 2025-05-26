# Create your tests here.
# csa/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import CSA
import json
import os
from django.conf import settings

class FirebaseFAQTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Get the correct path to credentials file
        self.cred_path = os.path.join(settings.BASE_DIR, 'csa-1a82c-firebase-adminsdk-fbsvc-5f3d988418.json')
        
        # Test FAQ data
        self.test_faq_data = {
            "name": "Test CSA",
            "description": "Test Description",
            "faqs": [
                {
                    "question": "How do I reset my password?",
                    "response_type": "answer",
                    "answer": "Click on 'Forgot Password' and follow the steps."
                },
                {
                    "question": "What are your working hours?",
                    "response_type": "subquestions",
                    "sub_questions": [
                        {
                            "question": "Are you open on weekends?",
                            "answer": "Yes, we're open 24/7!"
                        }
                    ]
                }
            ]
        }

    def verify_firebase_data(self, csa):
        """Helper method to verify data in Firebase"""
        import firebase_admin
        from firebase_admin import credentials, db
        
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.cred_path)  # Use the path from setUp
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://csa-1a82c-default-rtdb.firebaseio.com/'
            })
        
        # Get reference to the CSA's data
        ref = db.reference(csa.firebase_path)
        
        # Get the data
        data = ref.get()
        
        # Verify the data structure
        self.assertIsNotNone(data)
        self.assertIn('faqs', data)
        
        # Verify FAQ data
        faqs = data['faqs']
        self.assertEqual(len(faqs), len(self.test_faq_data['faqs']))
        
        # Verify first FAQ
        first_faq = next(iter(faqs.values()))
        self.assertEqual(first_faq['question'], self.test_faq_data['faqs'][0]['question'])
        self.assertEqual(first_faq['response_type'], self.test_faq_data['faqs'][0]['response_type'])
        self.assertEqual(first_faq['answer'], self.test_faq_data['faqs'][0]['answer'])

    def test_create_csa_with_faqs(self):
        """Test creating a CSA with FAQs and verify Firebase storage"""
        # Make the API request
        response = self.client.post(
            '/api/csa/',
            data=json.dumps(self.test_faq_data),
            content_type='application/json'
        )
        
        # Print response content for debugging
        print("Response content:", response.content)
        
        # Check if the request was successful
        self.assertEqual(response.status_code, 201)
        
        # Verify CSA was created in Django
        csa = CSA.objects.get(name="Test CSA")
        self.assertIsNotNone(csa)
        self.assertEqual(csa.user, self.user)
        
        # Verify Firebase path was saved
        self.assertIsNotNone(csa.firebase_path)
        
        # Add Firebase verification
        self.verify_firebase_data(csa)

    def test_create_csa_with_invalid_faq(self):
        """Test creating a CSA with invalid FAQ data"""
        invalid_data = self.test_faq_data.copy()
        invalid_data['faqs'][0]['response_type'] = 'invalid_type'
        
        response = self.client.post(
            '/api/csa/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_csa_without_faqs(self):
        """Test creating a CSA without FAQs"""
        data = {
            "name": "Test CSA",
            "description": "Test Description"
        }
        
        response = self.client.post(
            '/api/csa/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        csa = CSA.objects.get(name="Test CSA")
        self.assertIsNotNone(csa)