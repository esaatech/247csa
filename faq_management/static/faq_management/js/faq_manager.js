// FAQ Management System
console.log('FAQManager: loaded');
class FAQManager {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Add FAQ button
        document.getElementById('addFaq')?.addEventListener('click', () => this.createFaqEntry());
        
        // Handle response type changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[type="radio"][name^="responseType"]')) {
                this.handleResponseTypeChange(e.target);
            }
        });

        // Handle sub-question addition
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="add-subquestion"]')) {
                this.addSubQuestion(e.target);
            } else if (e.target.matches('[data-action="delete-faq"]')) {
                this.deleteFaq(e.target);
            } else if (e.target.matches('[data-action="delete-subquestion"]')) {
                this.deleteSubQuestion(e.target);
            }
        });

        // Handle form submission
        document.getElementById('faqForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit(e.target);
        });
    }

    createFaqEntry() {
        const faqEntry = document.createElement('div');
        faqEntry.className = 'border rounded-lg p-4 space-y-4';
        
        faqEntry.innerHTML = `
            <div class="flex items-center justify-between">
                <h4 class="font-medium">FAQ Entry</h4>
                <button 
                    type="button"
                    class="p-2 text-red-600 hover:bg-red-50 rounded"
                    data-action="delete-faq"
                >
                    <i data-lucide="trash-2" class="h-4 w-4"></i>
                </button>
            </div>
            <div>
                <label class="block text-sm font-medium mb-1">Main Question</label>
                <input 
                    type="text" 
                    class="w-full p-2 border rounded-md"
                    name="question"
                    placeholder="Enter the main question"
                    required
                >
            </div>
            <div class="space-y-2">
                <label class="block text-sm font-medium">Response Type</label>
                <div class="flex gap-4">
                    <label class="flex items-center gap-2">
                        <input type="radio" name="responseType${Math.random()}" value="answer" checked>
                        <span>Direct Answer</span>
                    </label>
                    <label class="flex items-center gap-2">
                        <input type="radio" name="responseType${Math.random()}" value="subquestions">
                        <span>Sub-questions</span>
                    </label>
                </div>
            </div>
            <div class="answerSection">
                <label class="block text-sm font-medium mb-1">Answer</label>
                <textarea 
                    class="w-full p-2 border rounded-md"
                    name="answer"
                    placeholder="Enter the answer"
                    rows="3"
                ></textarea>
            </div>
            <div class="subquestionsSection hidden space-y-4">
                <div class="space-y-2">
                    <label class="block text-sm font-medium">Sub-questions</label>
                    <div class="subquestionsList space-y-2">
                    </div>
                    <button
                        type="button"
                        class="flex items-center gap-2 px-4 py-2 border rounded hover:bg-gray-50"
                        data-action="add-subquestion"
                    >
                        <i data-lucide="plus" class="h-4 w-4"></i>
                        Add Sub-question
                    </button>
                </div>
            </div>
        `;

        const addFaqButton = document.getElementById('addFaq');
        if (addFaqButton && addFaqButton.parentNode) {
            addFaqButton.parentNode.insertBefore(faqEntry, addFaqButton);
        } else {
            // Fallback: append to faqList if button not found
            document.getElementById('faqList')?.appendChild(faqEntry);
        }
        lucide.createIcons();
        return faqEntry;
    }

    createSubQuestionHTML() {
        return `
            <div class="border rounded p-3 space-y-3">
                <div class="flex items-center justify-between">
                    <h5 class="font-medium">Sub-question</h5>
                    <button 
                        type="button"
                        class="p-1 text-red-600 hover:bg-red-50 rounded"
                        data-action="delete-subquestion"
                    >
                        <i data-lucide="trash-2" class="h-4 w-4"></i>
                    </button>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Question</label>
                    <input 
                        type="text" 
                        class="w-full p-2 border rounded-md"
                        name="sub_question"
                        placeholder="Enter sub-question"
                        required
                    >
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Answer</label>
                    <textarea 
                        class="w-full p-2 border rounded-md"
                        name="sub_answer"
                        placeholder="Enter answer for this sub-question"
                        rows="2"
                        required
                    ></textarea>
                </div>
            </div>
        `;
    }

    handleResponseTypeChange(radioInput) {
        const faqEntry = radioInput.closest('.border');
        const answerSection = faqEntry.querySelector('.answerSection');
        const subquestionsSection = faqEntry.querySelector('.subquestionsSection');
        
        if (radioInput.value === 'answer') {
            answerSection.classList.remove('hidden');
            subquestionsSection.classList.add('hidden');
        } else {
            answerSection.classList.add('hidden');
            subquestionsSection.classList.remove('hidden');
        }
    }

    addSubQuestion(button) {
        const subquestionsList = button.closest('.space-y-2').querySelector('.subquestionsList');
        const subQuestionHTML = this.createSubQuestionHTML();
        subquestionsList.insertAdjacentHTML('beforeend', subQuestionHTML);
        lucide.createIcons();
    }

    deleteFaq(button) {
        const faqEntry = button.closest('.border');
        if (document.querySelectorAll('.border').length > 1) {
            faqEntry.remove();
        } else {
            alert('You must have at least one FAQ entry');
        }
    }

    deleteSubQuestion(button) {
        const subQuestion = button.closest('.border');
        subQuestion.remove();
    }

    collectFaqs() {
        const faqs = [];
        const faqEntries = document.querySelectorAll('#faqForm > .border');
        
        faqEntries.forEach(entry => {
            const question = entry.querySelector('input[name="question"]').value;
            const responseType = entry.querySelector('input[type="radio"]:checked').value;
            const answer = entry.querySelector('textarea[name="answer"]')?.value || '';
            
            const subQuestions = [];
            if (responseType === 'subquestions') {
                entry.querySelectorAll('.subquestionsList > div').forEach(subQ => {
                    const subQuestion = subQ.querySelector('input[name="sub_question"]').value;
                    const subAnswer = subQ.querySelector('textarea[name="sub_answer"]').value;
                    if (subQuestion && subAnswer) {
                        subQuestions.push({
                            question: subQuestion,
                            answer: subAnswer
                        });
                    }
                });
            }

            if (question) {
                faqs.push({
                    question,
                    response_type: responseType,
                    answer: answer,
                    sub_questions: subQuestions
                });
            }
        });

        return faqs;
    }

    async handleFormSubmit(form) {
        const faqs = this.collectFaqs();
        if (faqs.length === 0) {
            alert('Please add at least one FAQ');
            return;
        }

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify({ faqs })
            });

            if (!response.ok) {
                throw new Error('Failed to save FAQs');
            }

            const result = await response.json();
            if (result.status === 'success') {
                alert('FAQs saved successfully!');
                // Optionally redirect or clear the form
            }
        } catch (error) {
            console.error('Error saving FAQs:', error);
            alert('Failed to save FAQs: ' + error.message);
        }
    }

    getCookie(name) {
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
}

// Initialize FAQ Manager when the DOM is loaded (for normal page loads)
document.addEventListener('DOMContentLoaded', () => {
    console.log('FAQManager: DOMContentLoaded');
    window.faqManager = new FAQManager();
    if (document.querySelectorAll('#faqList > div').length === 0) {
        window.faqManager.createFaqEntry();
    }
});

// Also handle HTMX swaps (if loaded via HTMX)
document.body.addEventListener('htmx:afterSwap', function(evt) {
    console.log('FAQManager: htmx:afterSwap');
    if (evt.detail.target.id === "faqSection") {
        setTimeout(function() {
            window.faqManager = new FAQManager();
            if (document.querySelectorAll('#faqList > div').length === 0) {
                window.faqManager.createFaqEntry();
            }
        }, 0);
    }
}); 