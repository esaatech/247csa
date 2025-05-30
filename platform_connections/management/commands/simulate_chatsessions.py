from django.core.management.base import BaseCommand
from platform_connections.models import ChatSession
from uuid import UUID
from django.utils import timezone

class Command(BaseCommand):
    help = 'Simulate ChatSession objects for testing'

    def handle(self, *args, **kwargs):
        agent_uuid = UUID('2aec710787494943aa18ebc681c1e8b1')
        now = timezone.now()
        sessions = [
            {
                'platform_type': 'website',
                'user_identifier': 'visitor_123',
                'is_active': True,
            },
            {
                'platform_type': 'sms',
                'user_identifier': '+15551234567',
                'is_active': True,
            },
            {
                'platform_type': 'email',
                'user_identifier': 'user@example.com',
                'is_active': False,
            },
        ]
        for s in sessions:
            obj, created = ChatSession.objects.get_or_create(
                agent_id=agent_uuid,
                platform_type=s['platform_type'],
                user_identifier=s['user_identifier'],
                defaults={
                    'started_at': now,
                    'last_activity_at': now,
                    'is_active': s['is_active'],
                }
            )
            if not created:
                obj.last_activity_at = now
                obj.is_active = s['is_active']
                obj.save()
        self.stdout.write(self.style.SUCCESS('Simulated ChatSession objects created/updated.'))
