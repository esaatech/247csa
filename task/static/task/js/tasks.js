document.body.addEventListener('htmx:afterSwap', function(evt) {
    setTimeout(initTaskDropdowns, 100);
});
document.addEventListener('DOMContentLoaded', initTaskDropdowns);

function initTaskDropdowns() {
    // Dropdown expand/collapse
    document.querySelectorAll('.task-dropdown-btn').forEach(btn => {
        btn.onclick = function() {
            const id = btn.getAttribute('data-task-id');
            const content = document.getElementById('task-content-' + id);
            if (content) {
                content.classList.toggle('hidden');
                // Initialize Flatpickr for edit form
                const dueDateInput = content.querySelector('.due-date-edit');
                if (window.flatpickr && dueDateInput) {
                    if (dueDateInput._flatpickr) dueDateInput._flatpickr.destroy();
                    flatpickr(dueDateInput, {
                        enableTime: true,
                        dateFormat: "Y-m-d H:i",
                        time_24hr: true,
                        defaultDate: dueDateInput.value
                    });
                }
            }
        }
    });
    // Edit task
    document.querySelectorAll('.editTaskForm').forEach(form => {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const taskId = form.getAttribute('data-task-id');
            const formData = new FormData(form);
            const data = {
                title: formData.get('title'),
                description: formData.get('description'),
                due_date: formData.get('due_date'),
                priority: formData.get('priority')
            };
            try {
                const response = await fetch(`/task/api/update_task/${taskId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (response.ok) {
                    showToast('Task updated successfully');
                    document.body.dispatchEvent(new CustomEvent('taskUpdated', { detail: { taskId } }));
                } else {
                    throw new Error(result.error || 'Failed to update task');
                }
            } catch (error) {
                showToast(error.message, 'error');
            }
        }
    });
    // Delete task
    document.querySelectorAll('.deleteTaskBtn').forEach(btn => {
        btn.onclick = async function() {
            const taskId = btn.getAttribute('data-task-id');
            if (!confirm('Are you sure you want to delete this task?')) return;
            try {
                const response = await fetch(`/task/api/delete_task/${taskId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                const result = await response.json();
                if (response.ok) {
                    showToast('Task deleted successfully');
                    document.body.dispatchEvent(new CustomEvent('taskDeleted', { detail: { taskId } }));
                    // Remove from DOM
                    btn.closest('.border').remove();
                } else {
                    throw new Error(result.error || 'Failed to delete task');
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

document.body.addEventListener('taskAdded', async (event) => {
    // Get the task_uuid from the URL since that's what we're using in the page
    const tasksContainer = document.querySelector('#tasks-container');
    const task_uuid = tasksContainer.getAttribute('data-task-uuid');
    console.log("........task_uuid..............,,,,,,,,,,,,,", task_uuid)    

    
    try {
        // Use task_uuid instead of task_id to fetch tasks
        const response = await fetch(`/task/tasks/?task_uuid=${task_uuid}`);
        const taskHtml = await response.text();
        const tasksContainer = document.querySelector('#tasks-container');
        if (tasksContainer) {
            if (tasksContainer.querySelector('.text-gray-500')) {
                // Remove "No tasks found" message if it exists
                tasksContainer.innerHTML = '';
            }
            // Create a temporary container to parse the HTML
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = taskHtml;
            
            // Get the actual task list content
            const newTaskList = tempContainer.querySelector('.space-y-4');
            if (newTaskList) {
                tasksContainer.innerHTML = newTaskList.innerHTML;
                initTaskDropdowns(); // Re-initialize dropdowns and event handlers
                initFlatpickr(); // Re-initialize date pickers
            }
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        showToast('Error loading tasks', 'error');
    }
});
            