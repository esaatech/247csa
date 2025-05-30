window.initAgentDetail = function () {
    console.log("calling Init Agent Detail");
    // Get references to the toggle, input, and send button
    const aiToggle = document.getElementById('aiToggle');
    const toggleDot = document.getElementById('toggleDot');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.querySelector('#chatForm button[type="submit"]');

    function updateInputState() {
        if (aiToggle && chatInput) {
            if (aiToggle.checked) {
                // Human Takeover: enable input and button
                chatInput.disabled = false;
                if (sendButton) sendButton.disabled = false;
                // Move dot right
                toggleDot.style.transform = 'translateX(16px)';
                toggleDot.style.backgroundColor = '#2563eb'; // blue-600
            } else {
                // AI Handling: disable input and button
                chatInput.disabled = true;
                if (sendButton) sendButton.disabled = true;
                // Move dot left
                toggleDot.style.transform = 'translateX(0)';
                toggleDot.style.backgroundColor = '#fff';
            }
        }
    }

    // Initial state
    updateInputState();

    // Listen for toggle changes
    if (aiToggle) {
        aiToggle.addEventListener('change', updateInputState);
    }

    lucide.createIcons();
};
