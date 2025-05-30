console.log('Chat window script loaded!');

let socket = null;

function openAgentWebSocket(sessionId) {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/chat/${sessionId}/`);

    socket.onopen = function() {
        console.log('[Agent WebSocket] Connected');
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        addMessageToChat(data.message, data.is_user);
    };

    socket.onclose = function() {
        console.log('[Agent WebSocket] Disconnected');
    };

    socket.onerror = function(e) {
        console.error('[Agent WebSocket] Error:', e);
    };
}

function addMessageToChat(message, isUser) {
    const messagesDiv = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = isUser ? 'flex justify-start' : 'flex justify-end';
    msgDiv.innerHTML = `
        <div class="${isUser ? 'bg-gray-200 text-gray-800' : 'bg-blue-600 text-white'} px-4 py-2 rounded-lg max-w-xs break-words">
            ${escapeHtml(message)}
        </div>
    `;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function attachChatFormHandler() {
    const form = document.getElementById('chatInputForm');
    if (!form) {
        console.error('chatInputForm not found!');
        return;
    }
    console.log('Form submit handler attached!');
    const input = document.getElementById('chatInput');
    const fileInput = document.getElementById('fileInput');
    const sessionId = form.getAttribute('data-session-id');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = input.value.trim();
        // For now, ignore file sending in WebSocket version
        if (!message) {
            return;
        }
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                'message': message,
                'is_user': false // agent
            }));
            input.value = '';
            fileInput.value = '';
        } else {
            console.error('[Agent WebSocket] Not open, message not sent.');
        }
    });
}

// Attach on initial load and after HTMX swaps
function initializeChatWindow() {
    const form = document.getElementById('chatInputForm');
    if (!form) return;
    const sessionId = form.getAttribute('data-session-id');
    openAgentWebSocket(sessionId);
    attachChatFormHandler();

    // Attach End Chat button handler
    const endBtn = document.getElementById('endChatBtn');
    if (endBtn) {
        endBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to end this chat?')) {
                fetch(`/platform_connections/end_chat_session/${sessionId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Chat ended.');
                        // Optionally, disable input or close chat window here
                    } else {
                        alert('Failed to end chat: ' + (data.error || 'Unknown error'));
                    }
                });
            }
        });
    } else {
        console.log('End chat button not found!');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired!');
    initializeChatWindow();

    // Attach after HTMX swaps in new content
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Only attach if the chat window was swapped in
        if (evt.target && evt.target.id === 'chatArea') {
            initializeChatWindow();
        }
    });
});

// Helper to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
