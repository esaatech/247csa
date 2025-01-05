from django.core.management.base import BaseCommand
from dashboard.models import Channel

class Command(BaseCommand):
    help = 'Creates initial set of communication channels for integrations'

    def handle(self, *args, **kwargs):
        channels = [
            {
                'name': 'email',
                'display_name': 'Email Integration',
                'description': 'Connect your assistant to handle email communications. Supports SMTP and IMAP protocols.'
            },
            {
                'name': 'whatsapp',
                'display_name': 'WhatsApp Business',
                'description': 'Enable your assistant to handle WhatsApp conversations using the WhatsApp Business API.'
            },
            {
                'name': 'messenger',
                'display_name': 'Facebook Messenger',
                'description': 'Integrate your assistant with Facebook Messenger to handle customer inquiries.'
            },
            {
                'name': 'instagram',
                'display_name': 'Instagram DM',
                'description': 'Connect your assistant to Instagram Direct Messages for customer support.'
            },
            {
                'name': 'slack',
                'display_name': 'Slack',
                'description': 'Enable your assistant to communicate through Slack channels and direct messages.'
            },
            {
                'name': 'teams',
                'display_name': 'Microsoft Teams',
                'description': 'Integrate your assistant with Microsoft Teams for internal support and communications.'
            },
            {
                'name': 'sms',
                'display_name': 'SMS',
                'description': 'Enable your assistant to handle SMS communications through various providers.'
            },
            {
                'name': 'voice',
                'display_name': 'Voice Calls',
                'description': 'Connect your assistant to handle voice calls and provide voice-based support.'
            }
        ]

        for channel_data in channels:
            Channel.objects.get_or_create(
                name=channel_data['name'],
                defaults={
                    'display_name': channel_data['display_name'],
                    'description': channel_data['description']
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created channel "{channel_data["display_name"]}"')
            ) 