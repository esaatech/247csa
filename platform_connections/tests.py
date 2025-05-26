from django.test import TestCase, Client
from django.urls import reverse
import uuid
from .models import WebsiteChatConnection, SMSConnection

class PlatformConnectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent_id = uuid.uuid4()
        self.website_chat_token = "test_token_123"
        self.sms_phone = "+1234567890"

    def test_get_agent_connections_no_connections(self):
        """Test getting connections for an agent with no connections"""
        url = reverse('platform_connections:get_agent_connections', args=[str(self.agent_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['platforms']['website_chat']['is_connected'], False)
        self.assertEqual(data['platforms']['sms']['is_connected'], False)
        self.assertIsNone(data['platforms']['website_chat']['connection_id'])
        self.assertIsNone(data['platforms']['sms']['connection_id'])

    def test_get_agent_connections_with_website_chat(self):
        """Test getting connections when website chat is connected"""
        # Create a website chat connection
        WebsiteChatConnection.objects.create(
            agent_id=self.agent_id,
            iframe_token=self.website_chat_token,
            is_connected=True
        )

        url = reverse('platform_connections:get_agent_connections', args=[str(self.agent_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['platforms']['website_chat']['is_connected'])
        self.assertIsNotNone(data['platforms']['website_chat']['connection_id'])
        self.assertFalse(data['platforms']['sms']['is_connected'])

    def test_get_agent_connections_with_sms(self):
        """Test getting connections when SMS is connected"""
        # Create an SMS connection
        SMSConnection.objects.create(
            agent_id=self.agent_id,
            twilio_account_sid="test_sid",
            twilio_auth_token="test_token",
            phone_number=self.sms_phone,
            is_connected=True
        )

        url = reverse('platform_connections:get_agent_connections', args=[str(self.agent_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['platforms']['sms']['is_connected'])
        self.assertIsNotNone(data['platforms']['sms']['connection_id'])
        self.assertFalse(data['platforms']['website_chat']['is_connected'])

    def test_get_agent_connections_with_disconnected_platforms(self):
        """Test getting connections when platforms are disconnected"""
        # Create disconnected connections
        WebsiteChatConnection.objects.create(
            agent_id=self.agent_id,
            iframe_token=self.website_chat_token,
            is_connected=False
        )
        SMSConnection.objects.create(
            agent_id=self.agent_id,
            twilio_account_sid="test_sid",
            twilio_auth_token="test_token",
            phone_number=self.sms_phone,
            is_connected=False
        )

        url = reverse('platform_connections:get_agent_connections', args=[str(self.agent_id)])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['platforms']['website_chat']['is_connected'])
        self.assertFalse(data['platforms']['sms']['is_connected'])
        self.assertIsNotNone(data['platforms']['website_chat']['connection_id'])
        self.assertIsNotNone(data['platforms']['sms']['connection_id'])

    def test_get_agent_connections_invalid_uuid(self):
        """Test getting connections with an invalid UUID"""
        url = reverse('platform_connections:get_agent_connections', args=['00000000-0000-0000-0000-000000000000'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid agent ID format')
