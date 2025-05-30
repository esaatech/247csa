import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatSession, Message, WebsiteChatConnection
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        is_user = text_data_json.get('is_user', True)

        # Save message to database
        await self.save_message(message, is_user)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'is_user': is_user
            }
        )

    async def chat_message(self, event):
        message = event['message']
        is_user = event['is_user']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'is_user': is_user
        }))

    @sync_to_async
    def save_message(self, message, is_user):
        try:
            chat_session = ChatSession.objects.get(id=self.session_id)
            Message.objects.create(
                session=chat_session,
                content=message,
                is_from_user=is_user
            )
        except ChatSession.DoesNotExist:
            print(f"Chat session {self.session_id} not found")

    async def session_ended(self, event):
        await self.send(text_data=json.dumps({
            'event': 'session_ended',
            'message': event['message']
        }))

class AgentDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'agent_dashboard'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def session_update(self, event):
        # Send the update to the agent dashboard
        await self.send(text_data=json.dumps(event['data']))

def notify_session_ended(session_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{session_id}',
        {
            'type': 'session_ended',
            'message': 'This chat session has been ended by the agent/user.'
        }
    )
