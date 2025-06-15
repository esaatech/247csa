# CSA App Project Map

## Overview
This document maps out the flow of data and control through the CSA (Customer Service Assistant) application, from URLs to views to models and templates.

## URL Patterns
```python
app_name = 'csa'

urlpatterns = [
    path('', include(router.urls)),  # API endpoints
    path('list/', views.csa_list, name='list'),
    path('create/', views.csa_create, name='create'),
    path('<uuid:pk>/', views.csa_detail, name='detail'),
    path('<uuid:pk>/edit/', views.csa_edit, name='edit'),
    path('crm-connect/', views.crm_connect, name='crm_connect'),
    path('<uuid:pk>/faqs/', views.csa_faqs_api, name='csa_faqs_api'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
```

## Data Flow Maps

### 1. Dashboard Flow
```
URL: /csa/dashboard/
View: dashboard()
Template: csa-dashboard.html
Context: None
Description: Renders the main CSA dashboard view
```

### 2. CSA List Flow
```
URL: /csa/list/
View: csa_list()
Template: csa_list.html
Model: CSA
Description: Lists all CSAs for the current user
```

### 3. CSA Creation Flow
```
URL: /csa/create/
View: csa_create()
Template: create.html
Model: CSA
Description: Multi-step CSA creation process
Steps:
1. Basic Info (step1)
2. Knowledge Base (step2)
3. Integrations & FAQs (step3)

- Uses HTMX to dynamically load:
    - FAQs (`faq_management:faq_template_right_panel`)
    - CRM (`csa:crm_connect`)
    - Platform connections (`platform_connections:platforms_connect`)
- Each section may load its own partial template or panel via HTMX requests for a dynamic, interactive experience.
- This allows for modular, real-time updates to the form without a full page reload.
```

### 4. CSA Detail Flow
```
URL: /csa/<uuid:pk>/
View: csa_detail()
Template: detail.html
Model: CSA
Description: Shows detailed information about a specific CSA
```

### 5. CSA Edit Flow
```
URL: /csa/<uuid:pk>/edit/
View: csa_edit()
Template: edit.html
Model: CSA
Description: Edit an existing CSA's details
```

### 6. CRM Connection Flow
```
URL: /csa/crm-connect/
View: crm_connect()
Template: crm_connect.html
Description: Interface for connecting CSAs to CRM systems
```

### 7. FAQs API Flow
```
URL: /csa/<uuid:pk>/faqs/
View: csa_faqs_api()
Model: FAQ, SubQuestion
Description: API endpoint for managing CSA FAQs
```

## Models

### 1. CSA Model
```python
class CSA(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    description = models.TextField()
    knowledge_text = models.TextField()
    firebase_path = models.CharField(max_length=255)
    status = models.CharField(choices=STATUS_CHOICES)
    default_handling_mode = models.CharField(choices=HANDLING_CHOICES)
```

### 2. FAQ Model
```python
class FAQ(models.Model):
    id = models.UUIDField(primary_key=True)
    csa = models.ForeignKey(CSA)
    question = models.TextField()
    response_type = models.CharField()
    answer = models.TextField()
```

### 3. SubQuestion Model
```python
class SubQuestion(models.Model):
    id = models.UUIDField(primary_key=True)
    faq = models.ForeignKey(FAQ)
    question = models.TextField()
    answer = models.TextField()
```

## Templates

### 1. Dashboard Templates
- `csa-dashboard.html`: Main dashboard view
- `dashboardcard.html`: Dashboard card component

### 2. CSA Management Templates
- `csa_list.html`: List of all CSAs
- `create.html`: CSA creation form
- `detail.html`: CSA details view
- `edit.html`: CSA edit form

### 3. Utility Templates
- `welcome_message.html`: Welcome message component
- `crm_connect.html`: CRM connection interface

## API Endpoints (via DRF)

### CSAViewSet
- `GET /api/csa/`: List CSAs
- `POST /api/csa/`: Create CSA
- `GET /api/csa/{id}/`: Retrieve CSA
- `PUT /api/csa/{id}/`: Update CSA
- `DELETE /api/csa/{id}/`: Delete CSA

### Custom Actions
- `POST /api/csa/step1/`: Save basic CSA info
- `POST /api/csa/{id}/step2/`: Save knowledge base
- `POST /api/csa/{id}/step3/`: Save integrations & FAQs

## External Integrations

### Firebase Integration
- `firebase_generate_path()`: Generate Firebase path
- `firebase_init()`: Initialize Firebase
- `firebase_save_faqs()`: Save FAQs to Firebase
- `firebase_delete_agent()`: Delete agent from Firebase
- `firebase_get_faqs()`: Retrieve FAQs from Firebase

### CRM Integration
- CRM connection interface available at `/csa/crm-connect/`
- Supports integration with external CRM systems
