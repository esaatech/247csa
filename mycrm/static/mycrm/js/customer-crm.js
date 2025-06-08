document.addEventListener('DOMContentLoaded', function() {
    attachFormListeners();
});

function attachFormListeners() {
    const customerForm = document.getElementById('customerForm');
    if (customerForm) {
        console.log('Attaching submit listener to form');
        customerForm.addEventListener('submit', handleCustomerSubmit);
    }
}

async function handleCustomerSubmit(event) {
    event.preventDefault();
    console.log('Form submit handler called');
    
    const form = event.target;
    const formData = new FormData(form);
    const mode = form.getAttribute('data-mode') || 'add';
    const customerId = form.getAttribute('data-customer-id');
    
    console.log('Form mode:', mode);
    console.log('Customer ID:', customerId);
    
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        address: formData.get('address'),
        company_name: formData.get('company_name'),
        industry: formData.get('industry'),
        company_size: formData.get('company_size'),
        relationship_status: formData.get('relationship_status'),
        tags: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag)
    };

    try {
        let url = '/mycrm/mcp/create_customer/';
        let method = 'POST';
        
        if (mode === 'edit') {
            url = '/mycrm/mcp/update_customer/';
            method = 'PUT';
            data.id = customerId;
            data.fields_to_update = { ...data };
            delete data.fields_to_update.id;
        }

        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `Failed to ${mode} customer`);
        }

        // Clear form if adding
        if (mode === 'add') {
            form.reset();
        } else {
            // Close modal if editing
            closeModal('editCustomerModal');
        }
        
        // Dispatch custom event to refresh the list
        document.body.dispatchEvent(new CustomEvent('customerUpdated'));

        // Show success message
        showToast(`Customer ${mode === 'edit' ? 'updated' : 'added'} successfully`);
        
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

async function deleteCustomer(customerId) {
    if (!confirm('Are you sure you want to delete this customer?')) {
        return;
    }

    try {
        const response = await fetch('/mycrm/mcp/delete_customer/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ id: customerId })
        });

        const result = await response.json();
        
        if (response.ok) {
            // Remove customer element from DOM
            document.getElementById(`customer-${customerId}`).remove();
            
            // Show success message
            showToast('Customer deleted successfully');
        } else {
            throw new Error(result.error || 'Failed to delete customer');
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

function editCustomer(customerId) {
    console.log('editCustomer', customerId);
    // Show modal
    const modal = document.createElement('div');
    modal.id = 'editCustomerModal';
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
    modal.innerHTML = `
        <div class="relative top-20 mx-auto p-5 border w-3/4 shadow-lg rounded-md bg-white">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-bold">Edit Customer</h2>
                <button onclick="closeModal('editCustomerModal')" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <div id="editCustomerForm"></div>
        </div>
    `;
    document.body.appendChild(modal);

    // Load the edit form
    fetch(`/mycrm/add/?mode=edit&customer_id=${customerId}`, {
        headers: {
            'HX-Request': 'true'
        }
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('editCustomerForm').innerHTML = html;
        // Attach submit event listener to the form
        const form = document.querySelector('#editCustomerForm form');
        if (form) {
            console.log('Attaching submit listener to edit form');
            form.addEventListener('submit', handleCustomerSubmit);
        }
    })
    .catch(error => {
        showToast('Failed to load edit form', 'error');
        console.error('Error:', error);
    });
}

// HTMX afterSwap handler
document.body.addEventListener('htmx:afterSwap', function(evt) {
    console.log('HTMX afterSwap event triggered');
    attachFormListeners();
}); 