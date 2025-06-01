import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatSession, Message, WebsiteChatConnection
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
from django.conf import settings
from urllib.parse import urljoin
from ai.n8n import get_ai_response

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

        # 1. Immediately broadcast the user's message
        await self.channel_layer.group_send(
            
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'is_user': True
            }
        )

        # 2. Now handle AI/human routing (which may broadcast an agent/AI reply)
        await self.handle_message_with_ai_routing(message, is_user)

    async def handle_message_with_ai_routing(self, message, is_user):
        """
        Handles incoming messages with AI/human routing:
        - If session is in 'ai' mode, calls the AI app endpoint, saves AI response, and switches to human if needed.
        - If session is in 'human' mode, just saves the message.
        Broadcasts the appropriate response to the chat group.
        """
        chat_session = await sync_to_async(ChatSession.objects.get)(id=self.session_id)
        if not chat_session.is_active:
            await self.send(text_data=json.dumps({
                'event': 'session_ended',
                'message': 'This chat session has ended. Please start a new chat.'
            }))
            return
        # Save the user's message
        await sync_to_async(Message.objects.create)(
            session=chat_session,
            content=message,
            is_from_user=True
        )
        if chat_session.handling_mode == 'ai':
            ai_reply, ai_button = await sync_to_async(get_ai_response)(message, str(chat_session.user_identifier))
            # Save AI response as agent message
            await sync_to_async(Message.objects.create)(
                session=chat_session,
                content=ai_reply,
                is_from_user=False
            )
            # If button is yes, switch to human mode
            if ai_button == 'yes':
                chat_session.handling_mode = 'human'
                await sync_to_async(chat_session.save)()
            # Broadcast AI response as agent message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_reply,
                    'is_user': False
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
