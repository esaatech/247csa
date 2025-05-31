console.log('Chat window script loaded!');

let socket = null;
let chatFormHandler = null;

function openAgentWebSocket(sessionId) {
    if (socket) {
        socket.close();
        socket = null;
    }
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/chat/${sessionId}/`);

    socket.onopen = function() {
        console.log('[Agent WebSocket] Connected');
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.event === 'session_ended') {
            handleSessionEnded(data.message);
            return;
        }
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

    if (chatFormHandler) {
        form.removeEventListener('submit', chatFormHandler);
    }
    chatFormHandler = function(e) {
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
    };
    form.addEventListener('submit', chatFormHandler);
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

    // Highlight and auto-load the first session on initial page load
    highlightAndClickFirstSession();

    // Attach after HTMX swaps in new content
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.target && evt.target.id === 'chatArea') {
            if (socket) {
                socket.close();
                socket = null;
            }
            initializeChatWindow();
        }
        // If the session list was swapped in, auto-load and highlight the first session
        if (evt.target && evt.target.id === 'sessionList') {
            setTimeout(function() {
                highlightAndClickFirstSession();
            }, 50); // 50ms delay, adjust as needed
        }
    });

    // Attach click handler to session items (delegated)
    document.body.addEventListener('click', function(evt) {
        const item = evt.target.closest('#sessionList .session-item');
        if (item) {
            highlightSelectedSession(item);
        }
    });
});

function highlightAndClickFirstSession() {
    const firstSession = document.querySelector('#sessionList .session-item');
    if (firstSession) {
        highlightSelectedSession(firstSession);
        firstSession.click();
    } else {
        const chatArea = document.getElementById('chatArea');
        if (chatArea) chatArea.innerHTML = '<div class="text-gray-400 text-center py-8">No session selected.</div>';
    }
}

function highlightSelectedSession(item) {
    document.querySelectorAll('#sessionList .session-item').forEach(el => {
        el.classList.remove('session-selected', 'bg-blue-100');
    });
    item.classList.add('session-selected', 'bg-blue-100');
}

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

function handleSessionEnded(message) {
    // Disable input and send button
    const input = document.getElementById('chatInput');
    const sendBtn = document.querySelector('#chatInputForm button[type="submit"]');
    if (input) input.disabled = true;
    if (sendBtn) sendBtn.disabled = true;
    // Disable End Chat button
    const endBtn = document.getElementById('endChatBtn');
    if (endBtn) {
        endBtn.disabled = true;
        endBtn.style.opacity = 0.5;
        endBtn.style.cursor = 'not-allowed';
    }
    // Show ended message
    addMessageToChat(message || 'This chat has ended.', false);
    // Close the WebSocket connection
    if (socket) socket.close();
    // Do NOT add a 'Start New Chat' button in the agent UI
}

function deleteChatSession(sessionId) {
    if (!confirm('Are you sure you want to delete this chat session? This cannot be undone.')) {
        return;
    }
    fetch(`/platform_connections/delete_chat_session/${sessionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Chat session deleted.');
            // The rest is handled by the WebSocket/HTMX logic
        } else {
            alert('Failed to delete chat: ' + (data.error || 'Unknown error'));
        }
    });
}
