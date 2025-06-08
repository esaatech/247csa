function pad(n) { return n < 10 ? '0' + n : n; }

function getCurrentDateTimeString() {
    const now = new Date();
    return now.getFullYear() + '-' +
        pad(now.getMonth() + 1) + '-' +
        pad(now.getDate()) + ' ' +
        pad(now.getHours()) + ':' +
        pad(now.getMinutes());
}

function initFlatpickr() {
    const dueDateInput = document.getElementById('due_date');
    if (window.flatpickr && dueDateInput) {
        // Destroy previous instance if exists
        if (dueDateInput._flatpickr) {
            dueDateInput._flatpickr.destroy();
        }
        // Set default value if empty
        if (!dueDateInput.value) {
            dueDateInput.value = getCurrentDateTimeString();
        }
        flatpickr("#due_date", {
            enableTime: true,
            dateFormat: "Y-m-d H:i",
            time_24hr: true,
            defaultDate: dueDateInput.value
        });
        console.log("Flatpickr initialized!");
    }
}

document.addEventListener('DOMContentLoaded', initFlatpickr);

document.body.addEventListener('htmx:afterSwap', function(evt) {
    setTimeout(initFlatpickr, 200);
    // Attach event listener to the add task form if present
    const form = document.getElementById('addTaskForm');
    if (form) {
        form.addEventListener('submit', handleAddTaskSubmit);
    }
});

async function handleAddTaskSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        task_uuid: formData.get('task_uuid'),
        title: formData.get('title'),
        description: formData.get('description'),
        due_date: formData.get('due_date'),
        priority: formData.get('priority')
    };
    try {
        const response = await fetch('/task/api/create_task/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (response.ok) {
            // Dispatch custom event for embedding apps to listen to
            const taskAddedEvent = new CustomEvent('taskAdded', { detail: { taskId: result.task_id } });
            document.body.dispatchEvent(taskAddedEvent);
            // Optionally close the slide out
            if (typeof closeSlideOut === 'function') closeSlideOut();
            showToast('Task added successfully');
        } else {
            throw new Error(result.error || 'Failed to add task');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
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