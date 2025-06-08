from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Customer, Interaction, Task
from task.models import Task as TaskApp  # Import the Task model from task app
import json





@login_required
def dashboard(request):
    """Main dashboard view"""
    return render(request, 'mycrm/crm-dashboard.html')



@login_required
def test_view(request):
    """Main test interface that loads customer form and view/edit section"""
    return render(request, 'mycrm/test.html')

@login_required
def add_customer(request):
    """Form to create or edit a customer"""
    if request.headers.get('HX-Request'):
        mode = request.GET.get('mode', 'add')
        customer = None
        if mode == 'edit':
            customer_id = request.GET.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
        return render(request, 'mycrm/addcustomer.html', {
            'mode': mode,
            'customer': customer
        })
    return HttpResponse(status=400)

@login_required
def customers_list(request):
    """List all customers with their interactions and tasks"""
    customers = Customer.objects.all().order_by('-created_at')
    if request.headers.get('HX-Request'):
        return render(request, 'mycrm/customers.html', {'customers': customers})
    return HttpResponse(status=400)

# MCP API Endpoints
@require_http_methods(["POST"])
def create_customer(request):
    try:
        data = json.loads(request.body)
        customer = Customer.objects.create(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            company_name=data.get('company_name', ''),
            industry=data.get('industry', ''),
            company_size=data.get('company_size', ''),
            relationship_status=data.get('relationship_status', 'prospect'),
            tags=data.get('tags', [])
        )
        return JsonResponse({
            'customer_id': customer.id,
            'task_uuid': customer.task_uuid,
            'activity_uuid': customer.activity_uuid,
            'status': 'created'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_customer(request):
    try:
        email = request.GET.get('email')
        customer = get_object_or_404(Customer, email=email)
        return JsonResponse({
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'address': customer.address,
                'company_name': customer.company_name,
                'industry': customer.industry,
                'company_size': customer.company_size,
                'relationship_status': customer.relationship_status,
                'notes': customer.notes,
                'tags': customer.tags,
                'created_at': customer.created_at.isoformat(),
                'updated_at': customer.updated_at.isoformat()
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["PUT"])
def update_customer(request):
    try:
        data = json.loads(request.body)
        customer = get_object_or_404(Customer, id=data['id'])
        
        fields_to_update = data.get('fields_to_update', {})
        for field, value in fields_to_update.items():
            if hasattr(customer, field):
                setattr(customer, field, value)
        
        customer.save()
        return JsonResponse({'status': 'updated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["DELETE"])
def delete_customer(request):
    try:
        data = json.loads(request.body)
        customer = get_object_or_404(Customer, id=data['id'])
        
        # Delete associated tasks from task app
        TaskApp.objects.filter(task_uuid=customer.task_uuid).delete()
        
        # Delete associated activities/interactions (if you have an Activity model)
        # ActivityApp.objects.filter(activity_uuid=customer.activity_uuid).delete()
        
        # Delete the customer (this will cascade delete interactions and old tasks)
        customer.delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
def log_interaction(request):
    try:
        data = json.loads(request.body)
        customer = get_object_or_404(Customer, id=data['customer_id'])
        
        interaction = Interaction.objects.create(
            customer=customer,
            type=data['type'],
            medium=data['medium'],
            description=data['description'],
            created_by=request.user
        )
        
        return JsonResponse({
            'interaction_id': interaction.id,
            'status': 'logged'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
def create_task(request):
    try:
        data = json.loads(request.body)
        customer = get_object_or_404(Customer, id=data['customer_id'])
        
        task = Task.objects.create(
            customer=customer,
            title=data['title'],
            due_date=data['due_date'],
            priority=data.get('priority', 'medium'),
            assigned_to=request.user
        )
        
        return JsonResponse({
            'task_id': task.id,
            'status': 'created'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_tasks(request):
    try:
        customer_id = request.GET.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        tasks = Task.objects.filter(customer=customer)
        
        return JsonResponse({
            'tasks': [{
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date.isoformat(),
                'is_completed': task.is_completed,
                'priority': task.priority
            } for task in tasks]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
