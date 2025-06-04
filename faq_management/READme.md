Page Load
│
├── DOMContentLoaded Event
│   └── faqInitAll()
│       ├── initFaqForm()
│       │   ├── Check if #faqList exists
│       │   │   └── If empty, create initial FAQ entry
│       │   │       └── createFaqEntry()
│       │   │           └── attachEntryHandlers(entry)
│       │   │
│       │   └── initFaqHandlers()
│       │       └── Attach click handler to #addFaq button
│       └── Attach click handler to #saveFaqs button
│
├── HTMX Swap (if loaded via HTMX)
│   └── htmx:afterSwap Event
│       └── faqInitAll() (with setTimeout)
│
└── Button Interactions
    │
    ├── "Add FAQ Entry" Button Click
    │   └── createFaqEntry()
    │       └── attachEntryHandlers(newEntry)
    │           ├── Attach delete handler
    │           ├── Attach radio button toggle handlers
    │           └── Attach sub-question handlers
    │
    ├── "Add Sub-question" Button Click
    │   └── Create new sub-question entry
    │       └── Attach delete handler
    │
    ├── "Delete FAQ" Button Click
    │   └── Remove FAQ entry (if more than one exists)
    │
    ├── "Delete Sub-question" Button Click
    │   └── Remove sub-question entry
    │
    ├── Radio Button Change
    │   └── Toggle between answer/subquestions sections
    │
    └── "Save FAQs" Button Click
        └── handleFaqSave(form)
            ├── validateFaqs()
            │   └── Check all required fields
            ├── collectFaqs()
            │   └── Gather all FAQ data
            └── POST to server
                └── Show success/error alert




DOMContentLoaded
│
└── faqInitAll()
    ├── initFaqForm()  // Sets up initial FAQ entry
    └── Attach save button handler                



HTMX Swap
│
└── htmx:afterSwap
    └── faqInitAll()  // Re-initializes after content swap    

Add FAQ
│
└── createFaqEntry()
    └── attachEntryHandlers()
        ├── Delete handler
        ├── Radio toggle handlers
        └── Sub-question handlers

Delete FAQ
│
└── Remove entry (if > 1 exists)

Add Sub-question
│
└── Create sub-question entry
    └── Attach delete handler

Delete Sub-question
│
└── Remove sub-question entry

Save FAQs
│
└── handleFaqSave()
    ├── validateFaqs()  // Validate all entries
    ├── collectFaqs()   // Gather data
    └── POST to server  // Save data
        └── Show result alert

Radio Change
│
└── Toggle Sections
    ├── Show/hide answer section
    └── Show/hide sub-questions section


--------------------------------- Updating the FAQS FLOWCHAT  faqs.html,   ------------------------------------


+-----------------------------+
|  User clicks "▼" on FAQ     |
+-------------+---------------+
              |
              v
+-----------------------------+
| Accordion expands, showing  |
| the FAQ edit form           |
+-------------+---------------+
              |
              v
+-----------------------------+
| User edits fields (question,|
| response type, answer,      |
| sub-questions)              |
+-------------+---------------+
              |
              v
+-----------------------------+
| User clicks "Save Changes"  |
| button                      |
+-------------+---------------+
              |
              v
+-----------------------------+
| saveFaq(form) JS function   |
| is called                   |
+-------------+---------------+
              |
              v
+-----------------------------+
| JS collects form data and   |
| builds JSON object          |
+-------------+---------------+
              |
              v
+-----------------------------+
| JS sends POST request to    |
| /faq-management/faq/<faq_id>|
| /update/ with JSON data     |
+-------------+---------------+
              |
              v
+-----------------------------+
| Django view: update_faq     |
| - Looks up FAQ by id        |
| - Updates FAQ fields        |
| - Deletes & recreates       |
|   sub-questions if needed   |
| - Saves changes             |
| - Returns JSON response     |
+-------------+---------------+
              |
              v
+-----------------------------+
| JS receives response        |
| If success: show alert      |
| "FAQ updated successfully!" |
| If error: show alert        |
| "Failed to update FAQ: ..." |
+-------------+---------------+
              |
              v
+-----------------------------+
| JS dispatches 'faq:updated' |
| event with {updated: true/false} |
dispatchFaqUpdatedEvent()
+-----------------------------+


------------adding faqto chat widget-----------
chat_widget.html — chat UI, includes FAQ block via HTMX
faq_in_chat_widget.html — renders FAQ buttons, handles click
faq_in_chat_widget view in faq_management/views.py — serves FAQ block HTML