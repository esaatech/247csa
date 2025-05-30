Website Chat Widget
Overview
The website chat widget is a reusable, embeddable component that allows visitors to chat in real time with agents. It is designed to be easily integrated into any website and provides a seamless, real-time chat experience using Django Channels and WebSockets.
Workflow
1. Session Initialization (Before WebSocket Connection)
Why?
To ensure every user’s chat is tracked and messages are grouped correctly, we first establish a unique chat session for each browser.
How?
When the widget loads, it checks for a browser_session_id in the browser’s localStorage.
If not present, it generates a new one and saves it.
The widget then sends a POST request to the backend to either create or retrieve a ChatSession for this browser session.
Frontend Example:
// On widget load
const browserSessionId = getOrCreateBrowserSessionId();
fetch(`/platform_connections/widget/chat/${connectionId}/init_session/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify({ browser_session_id: browserSessionId })
})
.then(response => response.json())
.then(data => {
    // Save session_id for later use
    window.chatSessionId = data.session_id;
});

@csrf_exempt
@require_POST
def init_chat_session(request, connection_id):
    # Get or create a ChatSession for the browser_session_id
    ...
    return JsonResponse({'session_id': str(chat_session.id)})



2. WebSocket Connection (When User Opens Chat)
Why?
To enable real-time, two-way communication, we use WebSockets. However, we only open the WebSocket after the session is initialized and the user interacts with the widget (e.g., clicks the chat icon).
How?
When the user clicks the chat icon, the widget opens a WebSocket connection to /ws/chat/<session_id>/.
The widget joins the chat session group on the backend.
Frontend Example:


// When user opens chat
const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/chat/${window.chatSessionId}/`);

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


3. Sending and Receiving Messages
Sending:
When the user sends a message, it is sent through the WebSocket to the backend, which saves it and broadcasts it to all clients in the session (including the agent).
Receiving:
When a message is received from the backend (from the agent or another user), it is displayed in the chat window in real time.
Frontend Example:        
// Send message
socket.send(JSON.stringify({ 'message': message, 'is_user': true }));

// Receive message
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    addMessageToChat(data.message, data.is_user);
};

async def receive(self, text_data):
    # Save message and broadcast to group
    ...
    await self.channel_layer.group_send(
        self.room_group_name,
        {
            'type': 'chat_message',
            'message': message,
            'is_user': is_user
        }
    )

async def chat_message(self, event):
    await self.send(text_data=json.dumps({
        'message': event['message'],
        'is_user': event['is_user']
    }))

Key Architectural Decisions
Session Initialization Before WebSocket:
We always initialize the chat session via a REST endpoint before opening the WebSocket. This ensures the backend can track and group messages by session, and the WebSocket always has a valid session ID.
WebSocket Only After User Interaction:
The WebSocket is only opened when the user actually opens the chat, reducing unnecessary server load and connections.
Messages Only Added When Received from Server:
To prevent duplicates and ensure consistency, messages are only displayed in the chat window when received from the server via WebSocket.



[User Widget] --(POST: init_session)--> [Django Backend: create/get ChatSession]
      |                                             |
      |<-- session_id ------------------------------|
      |
      |--(WebSocket: /ws/chat/<session_id>/)-------> [Django Channels/ChatConsumer]
      |<------------------ real-time messages ------------------->|