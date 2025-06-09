document.body.addEventListener('interactionAdded', async (event) => {
    const interactionsContainer = document.querySelector('#interactions-container');
    const activity_uuid = interactionsContainer.getAttribute('data-activity-uuid');
    console.log("........activity_uuid..............,,,,,,,,,,,,,", activity_uuid);

    try {
        // Use activity_uuid to fetch interactions
        const response = await fetch(`/interaction/interactions/?activity_uuid=${activity_uuid}`);
        const interactionHtml = await response.text();
        
        if (interactionsContainer) {
            // Create a temporary container to parse the HTML
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = interactionHtml;
            
            // Get the actual interaction list content
            const newInteractionList = tempContainer.querySelector('#interactions-container');
            if (newInteractionList) {
                interactionsContainer.innerHTML = newInteractionList.innerHTML;
                // Re-initialize any necessary components or event handlers
                initializeInteractions();
            }
        }
    } catch (error) {
        console.error('Error loading interactions:', error);
        showToast('Error loading interactions', 'error');
    }
});

// Initialize interaction event listeners and UI components
function initializeInteractions() {
    // Add click handlers for delete buttons
    document.querySelectorAll('.deleteInteractionBtn').forEach(btn => {
        btn.onclick = async function() {
            if (!confirm('Are you sure you want to delete this interaction?')) return;
            
            const interactionId = btn.getAttribute('data-interaction-id');
            try {
                const response = await fetch(`/interaction/api/delete_interaction/${interactionId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                const result = await response.json();
                if (response.ok) {
                    document.body.dispatchEvent(new CustomEvent('interactionDeleted'));
                    btn.closest('.border').remove();
                    showToast('Interaction deleted successfully');
                } else {
                    throw new Error(result.error || 'Failed to delete interaction');
                }
            } catch (error) {
                showToast(error.message, 'error');
            }
        }
    });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded-md text-white ${
        type === 'success' ? 'bg-green-600' : 'bg-red-600'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

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

// Initialize when the document loads
document.addEventListener('DOMContentLoaded', initializeInteractions); 