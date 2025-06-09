document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addInteractionForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const data = {
                activity_uuid: formData.get('activity_uuid'),
                type: formData.get('type'),
                medium: formData.get('medium'),
                description: formData.get('description')
            };

            try {
                const response = await fetch('/interaction/api/create_interaction/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (response.ok) {
                    console.log("........interaction added successfully.................,,,,,,,,,,,,,");
                    // Dispatch custom event
                    const interactionAddedEvent = new CustomEvent('interactionAdded', {
                        detail: {
                            interactionId: result.interaction_id,
                            type: data.type,
                            medium: data.medium,
                            description: data.description
                        }
                    });
                    document.body.dispatchEvent(interactionAddedEvent);
                    
                    // Close slide out if function exists
                    if (typeof closeSlideOut === 'function') closeSlideOut();
                    showToast('Interaction added successfully');
                } else {
                    throw new Error(result.error || 'Failed to add interaction');
                }
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
    }
});

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