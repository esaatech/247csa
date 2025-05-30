console.log('Chat window script loaded!');

function attachChatFormHandler() {
    const form = document.getElementById('chatInputForm');
    if (!form) {
        console.error('chatInputForm not found!');
        return;
    }
    console.log('Form submit handler attached!');
    const input = document.getElementById('chatInput');
    const fileInput = document.getElementById('fileInput');
    const messages = document.getElementById('chatMessages');
    const sessionId = form.getAttribute('data-session-id');
    const sendMessageUrl = `/chatui/chat/${sessionId}/send/`;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submit intercepted!');
        // Get message and file
        const message = input.value.trim();
        const file = fileInput.files[0];

        if (!message && !file) {
            return; // Don't send empty messages
        }

        // Prepare form data
        const formData = new FormData();
        formData.append('message', message);
        if (file) {
            formData.append('file', file);
        }

        // 1. Append user message immediately
        const userBubble = document.createElement('div');
        userBubble.className = 'flex justify-end';
        userBubble.innerHTML = `
            <div class="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-xs break-words">
                ${escapeHtml(message)}
            </div>
        `;
        messages.appendChild(userBubble);

        // 2. Show waiting indicator
        const waitingBubble = document.createElement('div');
        waitingBubble.className = 'flex justify-start';
        waitingBubble.id = 'waiting-bubble';
        waitingBubble.innerHTML = `
            <div class="bg-gray-200 text-gray-600 px-4 py-2 rounded-lg max-w-xs flex items-center gap-2">
                <span class="dot-flashing"></span>
                
            </div>
        `;
        messages.appendChild(waitingBubble);
        messages.scrollTop = messages.scrollHeight;

        // Clear input
        input.value = '';
        fileInput.value = '';

        // 3. Send AJAX request (simulate delay for test)
        setTimeout(() => {
            fetch(sendMessageUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(response => response.text())
            .then(html => {
                // Remove waiting indicator
                const waiting = document.getElementById('waiting-bubble');
                if (waiting) waiting.remove();
                // Append response
                messages.insertAdjacentHTML('beforeend', html);
                messages.scrollTop = messages.scrollHeight;
            })
            .catch(error => {
                // Remove waiting indicator
                const waiting = document.getElementById('waiting-bubble');
                if (waiting) waiting.remove();
                // Optionally show error
                console.error('Error sending message:', error);
            });
        }, 1200); // 1.2s delay for demo
    });
}

// Attach on initial load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired!');
    attachChatFormHandler();

    // Attach after HTMX swaps in new content
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Only attach if the chat window was swapped in
        if (evt.target && evt.target.id === 'chatArea') {
            attachChatFormHandler();
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