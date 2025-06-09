from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Customer
import json

@login_required
def dashboard(request, customer_id=None):
    """Main CRM dashboard view."""
    customers = Customer.objects.filter(created_by=request.user).order_by('-created_at')
    
    if customer_id:
        selected_customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
    else:
        selected_customer = customers.first()
    
    welcome_message = "Welcome to your Customer Relationship Management System"
    
    return render(request, 'mycrm/crm-dashboard.html', {
        'customers': customers,
        'customer': selected_customer,
        'welcome_message': welcome_message,
        'selected_customer_id': customer_id  # Pass this to help with highlighting
    })

@login_required
def get_customer_detail(request, customer_id):
    """Get detailed view of a customer."""
    customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
    return render(request, 'mycrm/detail.html', {'customer': customer})

@login_required
def add_customer(request):
    """Form to create or edit a customer"""
    if request.headers.get('HX-Request'):
        mode = request.GET.get('mode', 'add')
        customer = None
        if mode == 'edit':
            customer_id = request.GET.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
        return render(request, 'mycrm/add_customer.html', {
            'mode': mode,
            'customer': customer
        })
    return HttpResponse(status=400)

@require_http_methods(["POST"])
@login_required
def create_customer(request):
    """Create a new customer."""
    try:
        data = json.loads(request.body)
        
        # Check if email already exists
        if Customer.objects.filter(email=data['email'], created_by=request.user).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'A customer with this email address already exists'
            }, status=400)
            
        customer = Customer.objects.create(
            created_by=request.user,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            company_name=data.get('company_name', ''),
            industry=data.get('industry', ''),
            company_size=data.get('company_size', ''),
            relationship_status=data.get('relationship_status', 'lead')
        )
        return JsonResponse({
            'status': 'success',
            'customer_id': customer.id,
            'message': 'Customer created successfully'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        # Get the specific error message
        error_message = str(e)
        if 'unique constraint' in error_message.lower() and 'email' in error_message.lower():
            message = 'A customer with this email address already exists'
        else:
            message = 'Failed to create customer: ' + error_message
            
        return JsonResponse({
            'status': 'error',
            'message': message
        }, status=400)

@require_http_methods(["PUT", "PATCH"])
@login_required
def update_customer(request, customer_id):
    """Update an existing customer."""
    try:
        customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
        data = json.loads(request.body)
        
        # Check if email is being changed and if it already exists
        if 'email' in data and data['email'] != customer.email:
            if Customer.objects.filter(email=data['email'], created_by=request.user).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'A customer with this email address already exists'
                }, status=400)
        
        # Update fields
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.company_name = data.get('company_name', customer.company_name)
        customer.industry = data.get('industry', customer.industry)
        customer.company_size = data.get('company_size', customer.company_size)
        customer.relationship_status = data.get('relationship_status', customer.relationship_status)
        
        customer.save()
        return JsonResponse({
            'status': 'success',
            'customer_id': customer.id,
            'message': 'Customer updated successfully'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        # Get the specific error message
        error_message = str(e)
        if 'unique constraint' in error_message.lower() and 'email' in error_message.lower():
            message = 'A customer with this email address already exists'
        else:
            message = 'Failed to update customer: ' + error_message
            
        return JsonResponse({
            'status': 'error',
            'message': message
        }, status=400)

@require_http_methods(["DELETE"])
@login_required
def delete_customer(request, customer_id):
    """Delete a customer."""
    try:
        customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
        customer.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Customer deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["POST"])
@login_required
def search_customers(request):
    """Search customers and return updated list."""
    search_term = request.POST.get('search', '').strip()
    customers = Customer.objects.filter(created_by=request.user)
    
    if search_term:
        customers = customers.filter(
            name__icontains=search_term
        ) | customers.filter(
            email__icontains=search_term
        ) | customers.filter(
            company_name__icontains=search_term
        )
    
    return render(request, 'mycrm/customers_list.html', {
        'customers': customers
    })
