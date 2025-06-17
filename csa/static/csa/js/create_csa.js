console.log("CSA Create script loaded!");


class CSAListManager {
    constructor(listSelector = '#csaList', itemSelector = '.csa-item', mainContentSelector = '#mainContent') {
        this.list = document.querySelector(listSelector);
        this.itemSelector = itemSelector;
        this.mainContent = document.querySelector(mainContentSelector);
    }

    removeAndSelect(deletedCsaId) {
        console.log("Removing and selecting CSA:", deletedCsaId);
        const items = Array.from(this.list.querySelectorAll(this.itemSelector));
        const idx = items.findIndex(item => item.dataset.csaId === deletedCsaId);

        if (idx === -1) return; // Item not found

        // Remove the item from the DOM
        const deletedItem = items[idx];
        deletedItem.parentNode.removeChild(deletedItem);

        // Recompute the list after removal
        const newItems = Array.from(this.list.querySelectorAll(this.itemSelector));
        if (newItems.length === 0) {
            // No CSAs left, load the welcome message template via HTMX
            if (this.mainContent) {
                console.log("Loading welcome message template via HTMX");
                htmx.ajax('GET', '/api/csa/welcome-message/', this.mainContent);
            }
            return;
        }

        // Select next, else previous, else first
        let nextItem = newItems[idx] || newItems[idx - 1] || newItems[0];
        if (nextItem) {
            nextItem.click();
        }
    }
}



let currentStep = 1;


// Store the agent ID from when the user clicks on the csa item in the list from the code in csa_list.html
function storeAgentId(id) {
    window.agent_id = id;
    console.log("Agent ID stored:", window.agent_id);
}

// clear this so that when we are creating a new csa we don't have an agent_id sent to the view, this will affect how the plaforms buttons are shown, it will be managed with the csa id that it holds. 
function clearAgentId() {
    window.agent_id = null;
    window.csaId = null;  // Also clear the CSA ID
    console.log("Agent ID and CSA ID cleared");
}

// Add new function to reset form state
function resetFormState() {
    window.csaId = null;
    window.agent_id = null;
    // Reset any form fields if needed
    const form = document.querySelector('#createCsaForm form');  // Target the actual form element
    if (form) {
        form.reset();
    }
    // Reset step indicators
    showStep(1);
}

// Add this function at the top of your file
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

// Initialize the wizard
function initWizard() {
    console.log("Initializing wizard...");
    
    // Show first step
    showStep(1);
    
    // Add event listeners for navigation
    document.querySelectorAll('.next-step').forEach(button => {
        console.log("Adding next step listener to:", button);
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const nextStep = parseInt(button.dataset.next);
            console.log("Next step clicked, moving to step:", nextStep);
            
            if (await saveCurrentStep()) {
                showStep(nextStep);
            }
        });
    });

    document.querySelectorAll('.prev-step').forEach(button => {
        console.log("Adding prev step listener to:", button);
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const prevStep = parseInt(button.dataset.prev);
            console.log("Prev step clicked, moving to step:", prevStep);
            showStep(prevStep);
        });
    });

    // Add event listener for the final submit button
    const submitButton = document.querySelector('.csa-submit-button');
    if (submitButton) {
        submitButton.addEventListener('click', async (e) => {
            e.preventDefault(); // Prevent form submission
            await finalizeCsa();
        });
    }
}

// Show specific step
function showStep(step) {
    console.log("Showing step:", step);
    
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Show the selected step
    const stepElement = document.getElementById(`step${step}`);
    if (stepElement) {
        stepElement.classList.remove('hidden');
    }
    
    // Update progress bar
    const progress = ((step - 1) / 2) * 100;
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
    
    // Update step indicators
    document.querySelectorAll('.step-indicator').forEach(indicator => {
        indicator.classList.remove('active');
        if (parseInt(indicator.dataset.step) <= step) {
            indicator.classList.add('active');
        }
    });
    
    currentStep = step;
}

// Save current step
async function saveCurrentStep() {
    const currentStep = document.querySelector('.step-content:not(.hidden)').id.replace('step', '');
    console.log("Saving current step:", currentStep);
    
    const isEdit = document.getElementById('isEdit')?.value === 'true';
    
    switch(currentStep) {
        case '1':
            return await saveStep1();
        case '2':
            return await saveStep2();
        case '3':
            return await saveStep3();
        default:
            console.error("Unknown step:", currentStep);
            return false;
    }
}

// Save Step 1: Basic Info
async function saveStep1() {
    console.log("Saving step 1...");
    const name = document.querySelector('input[name="name"]').value;
    const description = document.querySelector('textarea[name="description"]').value;
    
    if (!name || !description) {
        alert('Please fill in all required fields');
        return false;
    }
    
    const data = {
        name,
        description
    };
    
    try {
        const isEdit = document.getElementById('isEdit')?.value === 'true';
        const csaId = document.querySelector('.delete-csa')?.dataset.csaId;
        
        console.log('Edit mode:', isEdit);
        console.log('CSA ID:', csaId);
        
        let response;
        if (isEdit && csaId) {
            // If we're in edit mode, use the CSA ID from the delete button
            console.log('Updating existing CSA:', csaId);
            response = await fetch(`/api/csa/csa/${csaId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify(data)
            });
            // Set window.csaId for edit mode to allow progression
            window.csaId = csaId;
        } else {
            // Create new CSA using step1 endpoint
            console.log('Creating new CSA');
            response = await fetch('/api/csa/csa/step1/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                const result = await response.json();
                window.csaId = result.id;  // Only set window.csaId for new CSAs
            }
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save basic info');
        }
        
        return true;
    } catch (error) {
        console.error("Error saving step 1:", error);
        alert(error.message);
        return false;
    }
}

// Add these functions before saveStep2

function getUploadedFiles() {
    const fileList = document.getElementById('fileList');
    const files = [];
    if (fileList) {
        fileList.querySelectorAll('div').forEach(fileItem => {
            const fileName = fileItem.querySelector('span').textContent;
            files.push(fileName);
        });
    }
    return files;
}

function getUrls() {
    const urlList = document.getElementById('urlList');
    const urls = [];
    if (urlList) {
        urlList.querySelectorAll('input[type="url"]').forEach(input => {
            if (input.value.trim()) {
                urls.push(input.value.trim());
            }
        });
    }
    return urls;
}

// Then modify saveStep2 to handle the case where these might be empty
async function saveStep2() {
    if (!window.csaId) {
        alert('Please complete step 1 first');
        return false;
    }
    
    const knowledgeData = {
        files: getUploadedFiles(),
        urls: getUrls(),
        text: document.querySelector('textarea[name="knowledge_text"]').value || ''
    };
    
    try {
        const response = await fetch(`/api/csa/csa/${window.csaId}/step2/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify(knowledgeData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || errorData.error || 'Failed to save knowledge base');
        }
        
        const result = await response.json();
        return true;
    } catch (error) {
        console.error("Error saving step 2:", error);
        alert(error.message);
        return false;
    }
}

// Save Step 3: Integrations & FAQ
async function saveStep3() {
    if (!window.csaId) {
        alert('Please complete step 1 first');
        return false;
    }
    
    const data = {
        integrations: {
            platforms: getPlatformConnections(),
            crm: getCrmConnection()
        }
    };
    
    try {
        const response = await fetch(`/api/csa/${window.csaId}/step3/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (response.ok) {
            return true;
        } else {
            throw new Error(result.error || 'Failed to save integrations');
        }
    } catch (error) {
        alert(error.message);
        return false;
    }
}

// Initialize the wizard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded, checking for CSA form...");
    if (document.querySelector('#createCsaForm')) {
        console.log("CSA form found, initializing...");
        window.initCsaForm();
    }
});

window.initCsaForm = function() {
    console.log("CSA form JS initialized!");

    // Initialize the wizard
    initWizard();
    
    // Add click handler for create button
    const createButton = document.getElementById('createButton');
    if (createButton) {
        createButton.addEventListener('click', () => {
            resetFormState();
        });
    }

    // Initialize other components only if they exist
            const addUrl = document.getElementById('addUrl');
    if (addUrl) {
            addUrl.addEventListener('click', () => {
                console.log("Add URL button clicked");
                const urlEntry = document.createElement('div');
                urlEntry.className = 'flex items-center gap-2';
                urlEntry.innerHTML = `
                    <input 
                        type="url" 
                        class="flex-1 p-2 border rounded-md"
                        placeholder="Enter website URL"
                    >
                    <button 
                        class="p-2 text-red-600 hover:bg-red-50 rounded"
                        onclick="this.parentElement.remove()"
                    >
                        <i data-lucide="trash-2" class="h-4 w-4"></i>
                    </button>
                `;
            document.getElementById('urlList').appendChild(urlEntry);
                    lucide.createIcons();
                });
            }

    // Initialize file upload handlers if they exist
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    if (dropZone && fileInput) {
        // ... your existing file upload code ...
    }

    // Initialize FAQ handlers if they exist
    const addFaq = document.getElementById('addFaq');
    if (addFaq) {
            addFaq.addEventListener('click', () => {
            const faqEntry = createFaqEntry();
            document.getElementById('faqList').appendChild(faqEntry);
        });
    }

    // Add delete button handler
    const deleteButton = document.querySelector('.delete-csa');
    if (deleteButton) {
        deleteButton.addEventListener('click', async function() {
            const csaId = this.dataset.csaId;
            if (!csaId) {
                alert('No CSA ID found');
                    return;
                }
                
            if (confirm('Are you sure you want to delete this CSA? This action cannot be undone.')) {
                try {
                    const response = await fetch(`/api/csa/csa/${csaId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'Content-Type': 'application/json',
                        },
                        credentials: 'same-origin'
                    });
                    
                    if (response.ok) {
                        // Redirect to dashboard or CSA list after successful deletion
                        //window.location.href = '/dashboard/';
                        const csaListManager = new CSAListManager();
                        csaListManager.removeAndSelect(csaId);
                        //showToast('CSA deleted successfully');




                    } else {
                        const data = await response.json();
                        alert(data.detail || 'Failed to delete CSA');
                    }
                } catch (error) {
                    console.error('Error deleting CSA:', error);
                    alert('Failed to delete CSA');
                }
            }
        });
    }
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '2rem';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.background = '#22c55e';
    toast.style.color = 'white';
    toast.style.padding = '1rem 2rem';
    toast.style.borderRadius = '0.5rem';
    toast.style.zIndex = 9999;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}



// Add this function to handle the final create button
async function finalizeCsa() {
    if (!window.csaId) {
        alert('Please complete all steps first');
        return false;
    }
    
    const data = {
        integrations: {
            platforms: getPlatformConnections(),
            crm: getCrmConnection()
        }
    };
    
    try {
        const response = await fetch(`/api/csa/csa/${window.csaId}/step3/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to finalize CSA');
        }
        
        // Reload the page to show the new CSA
        window.location.reload();
        
        return true;
    } catch (error) {
        console.error("Error finalizing CSA:", error);
        alert(error.message);
        return false;
    }
}

// Add this function to collect platform connections
function getPlatformConnections() {
    const platforms = {};
    
    // Get all platform connection buttons/panels
    const platformButtons = document.querySelectorAll('[data-platform]');
    
    platformButtons.forEach(button => {
        const platformType = button.dataset.platform;
        const platformId = button.dataset.platformId;
        const isConnected = button.classList.contains('connected');
        
        if (isConnected && platformId) {
            platforms[platformType] = {
                platform_id: platformId,
                csa_id: window.csaId,  // Associate with current CSA
                status: 'connected'
            };
        }
    });

    return platforms;
}

// Add this function to collect CRM connection
function getCrmConnection() {
    // For now, return an empty object or collect from your CRM connection UI
    return {};
}

document.addEventListener('faq:created', function(e) {
    console.log('faq:created event received:', e.detail);
    if (e.detail.created) {
        console.log('FAQ was created successfully!');
        const btn = document.getElementById('loadFaqBtn');
        if (btn) {
            btn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            btn.classList.add('bg-green-600', 'hover:bg-green-700');
            btn.innerHTML = '<span class="mr-2 text-white align-middle"><i data-lucide="check" class="inline h-5 w-5"></i></span>Connected to FAQ';
            if (window.lucide) lucide.createIcons();
        }
    } else {
        console.log('FAQ creation failed.');
    }
});







