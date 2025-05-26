console.log("platforms.js loaded");

// Function to handle website chat connection
async function connectWebsiteChat(agentId, token) {
    console.log("connectWebsiteChat called");
    try {
        const response = await fetch('/platform_connections/platforms-connect/website/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                agent_id: agentId,
                token: token
            })
        });

        const data = await response.json();
        
        if (data.success) {
            // Update main connect button to show connected state
            updateConnectButton('website_chat', true);
            // Show disconnect button in config panel
            showDisconnectButton(agentId);
            // Show success message
            showToast('Website chat connected successfully');
        } else {
            showToast(data.error || 'Failed to connect website chat', 'error');
        }
    } catch (error) {
        console.error('Error connecting website chat:', error);
        showToast('Failed to connect website chat', 'error');
    }
}

// Function to handle disconnection
async function disconnectWebsiteChat(agentId) {
    try {
        const response = await fetch('/platform_connections/platforms-connect/website/disconnect/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                agent_id: agentId
            })
        });

        const data = await response.json();
        
        if (data.success) {
            // Update UI to show disconnected state
            updateConnectButton('website_chat', false);
            // Hide disconnect button in config panel
            document.getElementById('disconnectButton').classList.add('hidden');
            // Show connect button
            document.getElementById('connectButton').classList.remove('hidden');
            // Show success message
            showToast('Website chat disconnected successfully');
        } else {
            showToast(data.error || 'Failed to disconnect website chat', 'error');
        }
    } catch (error) {
        console.error('Error disconnecting website chat:', error);
        showToast('Failed to disconnect website chat', 'error');
    }
}

// Helper function to update connect button state
function updateConnectButton(platform, isConnected) {
    const button = document.querySelector(`[data-platform="${platform}"]`);
    if (button) {
        const checkmark = button.querySelector('.checkmark');
        const buttonText = button.querySelector('.button-text');
        
        if (isConnected) {
            // Show checkmark and update text
            checkmark.classList.remove('hidden');
            buttonText.textContent = 'Connected to Website Chat';
            button.classList.add('connected');
            // Add green background when connected
            button.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            button.classList.add('bg-green-600', 'hover:bg-green-700');
        } else {
            // Hide checkmark and reset text
            checkmark.classList.add('hidden');
            buttonText.textContent = 'Connect to Website Chat';
            button.classList.remove('connected');
            // Reset to original gray background
            button.classList.remove('bg-green-600', 'hover:bg-green-700');
            button.classList.add('bg-gray-500', 'hover:bg-gray-600');
        }
    }
}

// Helper function to show disconnect button
function showDisconnectButton(agentId) {
    const connectButton = document.getElementById('connectButton');
    const disconnectButton = document.getElementById('disconnectButton');
    
    if (connectButton && disconnectButton) {
        connectButton.classList.add('hidden');
        disconnectButton.classList.remove('hidden');
    }
}

// Helper function to remove disconnect button
function removeDisconnectButton() {
    const connectButton = document.getElementById('connectButton');
    const disconnectButton = document.getElementById('disconnectButton');
    
    if (connectButton && disconnectButton) {
        connectButton.classList.remove('hidden');
        disconnectButton.classList.add('hidden');
    }
}

// Helper function to show toast messages
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}