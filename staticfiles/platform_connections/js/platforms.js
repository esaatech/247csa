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
            // Show success message
            showToast('Website chat connected successfully');
            
            // Refresh the panel content to show iframe code
            const panelContainer = document.getElementById('platformPanelContainer');
            if (panelContainer) {
                const response = await fetch(`/platform_connections/platforms-connect/website/?agent_id=${agentId}`);
                const html = await response.text();
                panelContainer.innerHTML = html;
                // Reattach event listeners after refresh
                attachEventListeners();
            }
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
    console.log("Disconnecting website chat for agent:", agentId);
    
    // Validate agent ID
    if (!agentId || agentId === 'None' || agentId === 'null') {
        console.error("Invalid agent ID:", agentId);
        showToast('Invalid agent ID', 'error');
        return;
    }
    
    try {
        const requestBody = {
            agent_id: agentId
        };
        console.log("Sending disconnect request with body:", requestBody);
        
        const response = await fetch('/platform_connections/platforms-connect/website/disconnect/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestBody)
        });

        console.log("Disconnect response status:", response.status);
        const data = await response.json();
        console.log("Disconnect response data:", data);
        
        if (data.success) {
            // Update UI to show disconnected state
            updateConnectButton('website_chat', false);
            // Show success message
            showToast('Website chat disconnected successfully');
            
            // Refresh the panel content to hide iframe code
            const panelContainer = document.getElementById('platformPanelContainer');
            if (panelContainer) {
                const response = await fetch(`/platform_connections/platforms-connect/website/?agent_id=${agentId}`);
                const html = await response.text();
                panelContainer.innerHTML = html;
                // Reattach event listeners after refresh
                attachEventListeners();
            }
        } else {
            showToast(data.error || 'Failed to disconnect website chat', 'error');
        }
    } catch (error) {
        console.error('Error disconnecting website chat:', error);
        showToast('Failed to disconnect website chat', 'error');
    }
}

// Function to attach event listeners
function attachEventListeners() {
    const connectButton = document.getElementById('connectButton');
    const disconnectButton = document.getElementById('disconnectButton');
    const agentId = document.getElementById('agentId')?.value;
    const token = document.getElementById('token')?.value;

    if (connectButton && agentId && token && agentId !== 'None' && agentId !== 'null') {
        connectButton.onclick = () => connectWebsiteChat(agentId, token);
    }

    if (disconnectButton && agentId && agentId !== 'None' && agentId !== 'null') {
        disconnectButton.onclick = () => disconnectWebsiteChat(agentId);
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

function copyIframeCode() {
    console.log("copyIframeCode called");
    const code = document.getElementById('iframeCode').innerText;
    navigator.clipboard.writeText(code).then(function() {
        // Optionally, show a toast or alert
       // alert('Iframe code copied to clipboard!');
    });
}