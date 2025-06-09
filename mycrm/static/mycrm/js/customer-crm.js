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

function showAddCustomerPanel() {
    fetch('/mycrm/customer/add/', {
        headers: {
            'HX-Request': 'true'
        }
    })
        .then(response => response.text())
        .then(html => {
            const customerDetail = document.getElementById('customer-detail');
            customerDetail.innerHTML = `
                <div class="p-6 bg-white h-full">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold">Add New Customer</h2>
                        <button onclick="handleCancel()" class="text-gray-600 hover:text-gray-800">
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    ${html}
                </div>
            `;
            attachFormListeners();
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to load add customer form', 'error');
        });
}

function showEditCustomerPanel(customerId) {
    fetch(`/mycrm/customer/add/?mode=edit&customer_id=${customerId}`, {
        headers: {
            'HX-Request': 'true'
        }
    })
        .then(response => response.text())
        .then(html => {
            const customerDetail = document.getElementById('customer-detail');
            customerDetail.innerHTML = `
                <div class="p-6 bg-white h-full">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold">Edit Customer</h2>
                        <button onclick="handleCancel()" class="text-gray-600 hover:text-gray-800">
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    ${html}
                </div>
            `;
            attachFormListeners();
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to load edit customer form', 'error');
        });
}

function showNextCustomer() {
    // Get all customer elements
    const customers = document.querySelectorAll('#customer-list > div[data-customer-id]');
    if (customers.length > 0) {
        // Show the first customer
        const firstCustomerId = customers[0].getAttribute('data-customer-id');
        fetch(`/mycrm/customer/${firstCustomerId}/detail/`)
            .then(response => response.text())
            .then(html => {
                const detail = document.getElementById('customer-detail');
                detail.innerHTML = html;
                htmx.process(detail);
                // Update selected state
                customers[0].classList.add('bg-blue-50');
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Failed to load customer details', 'error');
            });
    } else {
        // If no customers left, show welcome message
        document.getElementById('customer-detail').innerHTML = `
            <div class="flex items-center justify-center h-full bg-white">
                <div class="text-center p-8">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                    <h3 class="mt-4 text-lg font-medium text-gray-900">Welcome to your CRM</h3>
                    <p class="mt-2 text-sm text-gray-500">Select a customer from the list or add a new one to get started.</p>
                </div>
            </div>
        `;
    }
}

function handleCancel() {
    // Remove selected state from all customers
    document.querySelectorAll('#customer-list > div').forEach(row => {
        row.classList.remove('bg-blue-50');
    });
    
    // Show the first available customer
    showNextCustomer();
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
        let url = '/mycrm/customer/create/';
        let method = 'POST';
        
        if (mode === 'edit') {
            url = `/mycrm/customer/${customerId}/update/`;
            method = 'PUT';
            data.id = customerId;
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
            // Show error message from server
            throw new Error(result.message || `Failed to ${mode} customer`);
        }

        // Show success message
        showToast(`Customer ${mode === 'edit' ? 'updated' : 'added'} successfully`, 'success');
        
        // Refresh the customer list
        const customerList = document.getElementById('customer-list');
        if (customerList) {
            fetch('/mycrm/', {
                headers: {
                    'HX-Request': 'true'
                }
            })
                .then(response => response.text())
                .then(html => {
                    // Create a temporary div to parse the HTML
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    
                    // Find the customer list content in the response
                    const newCustomerList = tempDiv.querySelector('#customer-list');
                    if (newCustomerList) {
                        customerList.innerHTML = newCustomerList.innerHTML;
                        
                        // After refreshing the list, show the newly created/updated customer
                        if (result.customer_id) {
                            // Remove selected state from all customers
                            document.querySelectorAll('#customer-list > div').forEach(row => {
                                row.classList.remove('bg-blue-50');
                            });
                            
                            // Select the new/updated customer
                            const customerElement = document.querySelector(`[data-customer-id="${result.customer_id}"]`);
                            if (customerElement) {
                                customerElement.classList.add('bg-blue-50');
                            }
                            
                            // Show the customer details
                            fetch(`/mycrm/customer/${result.customer_id}/detail/`)
                                .then(response => response.text())
                                .then(html => {
                                    const detail = document.getElementById('customer-detail');
                                    detail.innerHTML = html;
                                    htmx.process(detail);
                                });
                        }
                    }
                });
        }
        
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
        const response = await fetch(`/mycrm/customer/${customerId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const result = await response.json();
        
        if (response.ok) {
            // Remove customer element from DOM
            const customerElement = document.querySelector(`[data-customer-id="${customerId}"]`);
            if (customerElement) {
                customerElement.remove();
            }
            
            // Show success message
            showToast('Customer deleted successfully');
            
            // Remove selected state from all customers
            document.querySelectorAll('#customer-list > div').forEach(row => {
                row.classList.remove('bg-blue-50');
            });
            
            // Show the next available customer
            showNextCustomer();
        } else {
            throw new Error(result.error || 'Failed to delete customer');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
    }
}

function showToast(message, type = 'success') {
    // Remove any existing toasts
    const existingToasts = document.querySelectorAll('.toast-message');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast-message fixed top-4 right-4 px-6 py-4 rounded-lg text-white font-medium shadow-lg z-50 flex items-center ${
        type === 'success' ? 'bg-green-600' : 'bg-red-600'
    }`;

    // Add icon based on type
    const icon = document.createElement('span');
    if (type === 'success') {
        icon.innerHTML = `
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        `;
    } else {
        icon.innerHTML = `
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
        `;
    }
    toast.appendChild(icon);

    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    toast.appendChild(messageSpan);
    
    // Add a subtle animation
    toast.style.transition = 'all 0.3s ease-in-out';
    toast.style.transform = 'translateY(-20px)';
    toast.style.opacity = '0';
    
    document.body.appendChild(toast);
    
    // Trigger animation
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    });
    
    // Remove the toast after 5 seconds
    setTimeout(() => {
        toast.style.transform = 'translateY(-20px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
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

// HTMX afterSwap handler
document.body.addEventListener('htmx:afterSwap', function(evt) {
    console.log('HTMX afterSwap event triggered');
    attachFormListeners();
}); 