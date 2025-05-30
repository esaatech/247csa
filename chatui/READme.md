Agent Chat Workflow
1. Agent Dashboard: Viewing Active Sessions
The agent dashboard displays a list of active chat sessions.
Each session represents a unique conversation with a website visitor (user).
The session list is loaded via HTMX or AJAX from the backend, showing user info and last message.
2. Agent Clicks a Chat Session
When the agent clicks on a session, the chat window for that session is loaded into the dashboard.
The chat window loads the full message history for that session (via HTMX/AJAX).
3. WebSocket Connection Established
As soon as the chat window loads, a WebSocket connection is opened from the agent’s browser to the backend:

  ws://<server>/ws/chat/<session_id>/

The agent’s browser joins the same real-time group as the user’s chat widget.
4. Real-Time Messaging
Sending Messages:
When the agent types a message and hits send, the message is sent through the WebSocket to the backend.
The backend saves the message to the database and broadcasts it to all clients connected to that session (including the user and any other agents).
Receiving Messages:
When the user sends a message from the website widget, it is also sent to the backend via WebSocket.
The backend broadcasts the message to all clients in the session group, so the agent sees it instantly in the chat window.
5. Message Display
Both agent and user see new messages appear in real time, with no need to refresh the page.
Messages are only added to the chat window when received from the server, ensuring all clients stay in sync and no duplicates appear.
6. Session Persistence
All messages are stored in the database and can be reloaded if the agent or user refreshes or reopens the chat.