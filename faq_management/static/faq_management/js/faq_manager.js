// FAQ Management System (extracted from create_csa.js)
console.log('FAQManager: loaded');

function createFaqEntry(faqData = null) {
    const faqEntry = document.createElement('div');
    faqEntry.className = 'border rounded-lg p-4 space-y-4';

    // Default values
    const question = faqData?.question || '';
    const responseType = faqData?.response_type || 'answer';
    const answer = faqData?.answer || '';
    const subQuestions = Array.isArray(faqData?.sub_questions) ? faqData.sub_questions : [];

    const radioName = `responseType${Math.random()}`;

    faqEntry.innerHTML = `
        <div class="flex items-center justify-between">
            <h4 class="font-medium">FAQ Entry</h4>
            <button 
                type="button"
                class="p-2 text-red-600 hover:bg-red-50 rounded delete-faq-btn"
            >
                <i data-lucide="trash-2" class="h-4 w-4"></i>
            </button>
        </div>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-1">Main Question</label>
                <input 
                    type="text" 
                    class="w-full p-2 border rounded-md"
                    name="question"
                    placeholder="Enter the main question"
                    value="${question.replace(/"/g, '&quot;')}"
                    required
                >
            </div>
            <div class="space-y-2">
                <label class="block text-sm font-medium">Response Type</label>
                <div class="flex gap-4">
                    <label class="flex items-center gap-2">
                        <input type="radio" name="${radioName}" value="answer" ${responseType === 'answer' ? 'checked' : ''}>
                        <span>Direct Answer</span>
                    </label>
                    <label class="flex items-center gap-2">
                        <input type="radio" name="${radioName}" value="subquestions" ${responseType === 'subquestions' ? 'checked' : ''}>
                        <span>Sub-questions</span>
                    </label>
                </div>
            </div>
            <div class="answerSection" ${responseType === 'answer' ? '' : 'hidden'}>
                <label class="block text-sm font-medium mb-1">Answer</label>
                <textarea 
                    class="w-full p-2 border rounded-md"
                    name="answer"
                    placeholder="Enter the answer"
                    rows="3"
                    required
                >${answer}</textarea>
            </div>
            <div class="subquestionsSection ${responseType === 'subquestions' ? '' : 'hidden'} space-y-4">
                <div class="space-y-2">
                    <label class="block text-sm font-medium">Sub-questions</label>
                    <div class="subquestionsList space-y-2">
                        ${subQuestions.map(subQ => `
                            <div class="border rounded p-3 space-y-3 sub-question-entry">
                                <div class="flex items-center justify-between">
                                    <h5 class="font-medium">Sub-question</h5>
                                    <button 
                                        type="button"
                                        class="p-1 text-red-600 hover:bg-red-50 rounded delete-subquestion-btn"
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
                                        value="${subQ.question.replace(/"/g, '&quot;')}"
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
                                    >${subQ.answer}</textarea>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <button
                        type="button"
                        class="flex items-center gap-2 px-4 py-2 border rounded hover:bg-gray-50 add-subquestion-btn"
                    >
                        <i data-lucide="plus" class="h-4 w-4"></i>
                        Add Sub-question
                    </button>
                </div>
            </div>
        </div>
    `;
    lucide.createIcons();
    return faqEntry;
}

function collectFaqs() {
    const faqs = [];
    const faqEntries = document.querySelectorAll('#faqList > .border');
    faqEntries.forEach(entry => {
        const questionInput = entry.querySelector('input[name="question"]');
        const question = questionInput ? questionInput.value.trim() : '';
        const responseType = entry.querySelector('input[type="radio"]:checked').value;
        const answer = entry.querySelector('textarea[name="answer"]')?.value.trim() || '';
        const subQuestions = [];
        if (responseType === 'subquestions') {
            entry.querySelectorAll('.subquestionsList > .sub-question-entry').forEach(subQ => {
                const subQuestion = subQ.querySelector('input[name="sub_question"]').value.trim();
                const subAnswer = subQ.querySelector('textarea[name="sub_answer"]').value.trim();
                if (subQuestion && subAnswer) {
                    subQuestions.push({ question: subQuestion, answer: subAnswer });
                }
            });
        }
        if (question) {
            faqs.push({
                question,
                response_type: responseType,
                answer,
                sub_questions: subQuestions
            });
        }
    });
    return faqs;
}

function validateFaqs() {
    let valid = true;
    let firstInvalid = null;
    const faqEntries = document.querySelectorAll('#faqList > .border');
    faqEntries.forEach(entry => {
        const questionInput = entry.querySelector('input[name="question"]');
        const question = questionInput ? questionInput.value.trim() : '';
        if (!question) {
            valid = false;
            firstInvalid = firstInvalid || questionInput;
            questionInput.classList.add('border-red-500');
        } else {
            questionInput.classList.remove('border-red-500');
        }
        const responseType = entry.querySelector('input[type="radio"]:checked').value;
        if (responseType === 'answer') {
            const answerInput = entry.querySelector('textarea[name="answer"]');
            const answer = answerInput.value.trim();
            if (!answer) {
                valid = false;
                firstInvalid = firstInvalid || answerInput;
                answerInput.classList.add('border-red-500');
            } else {
                answerInput.classList.remove('border-red-500');
            }
        } else if (responseType === 'subquestions') {
            const subQuestions = entry.querySelectorAll('.subquestionsList > .sub-question-entry');
            if (subQuestions.length === 0) {
                valid = false;
                firstInvalid = firstInvalid || entry.querySelector('.add-subquestion-btn');
            }
            subQuestions.forEach(subQ => {
                const subQuestionInput = subQ.querySelector('input[name="sub_question"]');
                const subAnswerInput = subQ.querySelector('textarea[name="sub_answer"]');
                if (!subQuestionInput.value.trim() || !subAnswerInput.value.trim()) {
                    valid = false;
                    firstInvalid = firstInvalid || subQuestionInput || subAnswerInput;
                    subQuestionInput.classList.add('border-red-500');
                    subAnswerInput.classList.add('border-red-500');
                } else {
                    subQuestionInput.classList.remove('border-red-500');
                    subAnswerInput.classList.remove('border-red-500');
                }
            });
        }
    });
    if (!valid && firstInvalid) {
        firstInvalid.focus();
        alert('Please fill in all required fields before saving.');
    }
    return valid;
}

function initFaqHandlers() {
    const faqList = document.getElementById('faqList');
    if (!faqList) return;
    const addFaqBtn = document.getElementById('addFaq');
    if (addFaqBtn) {
        addFaqBtn.onclick = function() {
            const entry = createFaqEntry();
            faqList.appendChild(entry);
            attachEntryHandlers(entry);
        };
    }
    // Attach handlers to existing entries
    faqList.querySelectorAll('.border').forEach(attachEntryHandlers);
}

function attachEntryHandlers(entry) {
    console.log('attachEntryHandlers', entry);
    if (entry === null) return;
    // Delete FAQ
    const deleteBtn = entry.querySelector('.delete-faq-btn');
    if (deleteBtn) {
        deleteBtn.onclick = function() {
            if (document.querySelectorAll('#faqList > .border').length > 1) {
                entry.remove();
            } else {
                alert('You must have at least one FAQ entry');
            }
        };
    }
    // Response type toggle
    const responseTypeInputs = entry.querySelectorAll('input[type="radio"][name^="responseType"]');
    if (responseTypeInputs) {
        responseTypeInputs.forEach(input => {
            input.onchange = function(e) {
                const answerSection = entry.querySelector('.answerSection');
                const subquestionsSection = entry.querySelector('.subquestionsSection');
                console.log('Radio changed:', e.target.value);
                if (!answerSection || !subquestionsSection) {
                    console.log('Missing answerSection or subquestionsSection');
                    return;
                }
                if (e.target.value === 'answer') {
                    answerSection.classList.remove('hidden');
                    subquestionsSection.classList.add('hidden');
                    console.log('Show answerSection, hide subquestionsSection');
                    // Focus the answer textarea
                    const answerInput = entry.querySelector('textarea[name="answer"]');
                    if (answerInput) {
                        answerInput.focus();
                        console.log('Focused answer textarea');
                    }
                } else {
                    answerSection.classList.add('hidden');
                    subquestionsSection.classList.remove('hidden');
                    console.log('Show subquestionsSection, hide answerSection');
                    // Focus the first sub-question input if it exists
                    const subQ = entry.querySelector('.sub-question-entry input[name="sub_question"]');
                    if (subQ) {
                        subQ.focus();
                        console.log('Focused first sub-question input');
                    }
                }
                console.log('answerSection hidden:', answerSection.classList.contains('hidden'));
                console.log('subquestionsSection hidden:', subquestionsSection.classList.contains('hidden'));
            };
        });
    }
    // Add sub-question
    const addSubBtn = entry.querySelector('.add-subquestion-btn');
    if (addSubBtn) {
        addSubBtn.onclick = function() {
            const subquestionsList = entry.querySelector('.subquestionsList');
            if (!subquestionsList) return;
            const subQ = document.createElement('div');
            subQ.className = 'border rounded p-3 space-y-3 sub-question-entry';
            subQ.innerHTML = `
                <div class="flex items-center justify-between">
                    <h5 class="font-medium">Sub-question</h5>
                    <button type="button" class="p-1 text-red-600 hover:bg-red-50 rounded delete-subquestion-btn">
                        <i data-lucide="trash-2" class="h-4 w-4"></i>
                    </button>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Question</label>
                    <input type="text" class="w-full p-2 border rounded-md" name="sub_question" placeholder="Enter sub-question" required>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Answer</label>
                    <textarea class="w-full p-2 border rounded-md" name="sub_answer" placeholder="Enter answer for this sub-question" rows="2" required></textarea>
                </div>
            `;
            subquestionsList.appendChild(subQ);
            // Delete sub-question
            const delSubBtn = subQ.querySelector('.delete-subquestion-btn');
            if (delSubBtn) {
                delSubBtn.onclick = function() {
                    subQ.remove();
                };
            }
            lucide.createIcons();
        };
    }
    // Delete sub-question for existing ones
    const delSubBtns = entry.querySelectorAll('.delete-subquestion-btn');
    if (delSubBtns) {
        delSubBtns.forEach(btn => {
            btn.onclick = function() {
                const subEntry = btn.closest('.sub-question-entry');
                if (subEntry) subEntry.remove();
            };
        });
    }
    lucide.createIcons();
}

// Initialization
function initFaqForm() {
    const faqList = document.getElementById('faqList');
    if (!faqList) return;
    if (faqList && faqList.children.length === 0) {
        const entry = createFaqEntry();
        faqList.appendChild(entry);
        attachEntryHandlers(entry);
    } else if (faqList) {
        faqList.querySelectorAll('.border').forEach(attachEntryHandlers);
    }
    initFaqHandlers();
}

function dispatchFaqCreatedEvent(success) {
    document.dispatchEvent(new CustomEvent('faq:created', {
        detail: { created: !!success }
    }));
}

// Save button handler
function handleFaqSave(form) {
    if (!validateFaqs()) return;
    const faqs = collectFaqs();
    const faqid = document.getElementById('faqid')?.value || '';
    fetch(form.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include',
        body: JSON.stringify({ faqs, faqid })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            alert('FAQs saved successfully!');
            dispatchFaqCreatedEvent(true);
        } else {
            alert('Failed to save FAQs: ' + (result.message || 'Unknown error'));
            dispatchFaqCreatedEvent(false);
        }
    })
    .catch(error => {
        alert('Failed to save FAQs: ' + error.message);
        dispatchFaqCreatedEvent(false);
    });
}

// DOMContentLoaded and HTMX swap
function faqInitAll() {
    initFaqForm();
    const saveBtn = document.getElementById('saveFaqs');
    if (saveBtn) {
        saveBtn.onclick = function() {
            handleFaqSave(document.getElementById('faqForm'));
        };
    }
}

document.addEventListener('DOMContentLoaded', faqInitAll);
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === "faqSection") {
        setTimeout(faqInitAll, 0);
    }
});

window.faqManager = { handleFormSubmit: handleFaqSave };

// New functions for accordion behavior
function toggleFaq(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('.toggle-icon');
    
    // Close other FAQs
    document.querySelectorAll('.faq-content:not(.hidden)').forEach(el => {
        if (el !== content) {
            el.classList.add('hidden');
            el.previousElementSibling.querySelector('.toggle-icon').textContent = '▼';
        }
    });
    
    // Toggle current FAQ
    content.classList.toggle('hidden');
    icon.textContent = content.classList.contains('hidden') ? '▼' : '▲';
}

function toggleSubQuestion(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('.toggle-icon');
    
    content.classList.toggle('hidden');
    icon.textContent = content.classList.contains('hidden') ? '▼' : '▲';
}

function editFaq(faqId) {
    // Load the edit form for this FAQ
    htmx.ajax('GET', `/faq-management/faq/${faqId}/edit/`, {
        target: '#editFormContainer',
        swap: 'innerHTML'
    });
}
