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



Session Highlight Feature Documentation
Purpose
The session highlight feature visually indicates which chat session is currently selected in the agent dashboard’s session list. This improves usability by making it clear to the agent which conversation is in focus, mirroring the behavior of the CSA highlight in the main dashboard.


How It Works
Auto-Highlight on Load
When the dashboard loads or the session list is refreshed (e.g., via HTMX), the first session in the list is automatically highlighted and selected.
Highlight on Click
When an agent clicks on any session in the list, that session is highlighted, and the highlight is removed from all others.
Consistent Visual Feedback
The highlight uses the CSS classes session-selected and bg-blue-100 for a clear, consistent look.


You can further customize this in chatui/static/chatui/css/chat_window.css.
JavaScript
The logic is implemented in chatui/static/chatui/chat_window.js.
Key functions:
highlightAndClickFirstSession(): Highlights and clicks the first session in the list.
highlightSelectedSession(item): Adds highlight classes to the selected session and removes them from others.
Event listeners:
On page load and after HTMX swaps, the first session is auto-highlighted and selected.
On click, the clicked session is highlighted.
HTML Structure
Each session item in the list has the class session-item and is contained within an element with the ID sessionList.


HTML Structure
Each session item in the list has the class session-item and is contained within an element with the ID sessionList.
How to Use
No manual action is needed—the highlight is managed automatically.
If you want to change the highlight color or style, edit the .session-selected class in your CSS.