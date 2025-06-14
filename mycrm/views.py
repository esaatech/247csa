from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from .models import Customer
from team.models import Team
import json

@login_required
def dashboard(request, customer_id=None):
    """Main CRM dashboard view."""
    customers = Customer.objects.filter(teams__members__user=request.user, teams__members__is_active=True).distinct().order_by('-created_at')
    customer_list = []
    for customer in customers:
        customer.can_edit = customer.can_edit(request.user)
        customer_list.append(customer)
    if customer_id:
        selected_customer = get_object_or_404(Customer, id=customer_id)
        if not selected_customer.can_view(request.user):
            raise PermissionDenied("You don't have permission to access this customer.")
    else:
        selected_customer = customer_list[0] if customer_list else None
    can_edit = selected_customer.can_edit if selected_customer else False
    welcome_message = "Welcome to your Customer Relationship Management System"
    return render(request, 'mycrm/crm-dashboard.html', {
        'customers': customer_list,
        'customer': selected_customer,
        'can_edit': can_edit,
        'welcome_message': welcome_message,
        'selected_customer_id': customer_id
    })

@login_required
def get_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    can_edit = customer.can_edit(request.user)
    print("DEBUG can_edit:", can_edit, "user:", request.user, "customer:", customer)
    return render(request, 'mycrm/detail.html', {'customer': customer, 'can_edit': can_edit})

@login_required
def add_customer(request):
    if request.headers.get('HX-Request'):
        mode = request.GET.get('mode', 'add')
        customer = None
        if mode == 'edit':
            customer_id = request.GET.get('customer_id')
            customer = get_object_or_404(Customer, id=customer_id)
            if not customer.can_edit(request.user):
                raise PermissionDenied("You don't have permission to edit this customer.")
        return render(request, 'mycrm/add_customer.html', {
            'mode': mode,
            'customer': customer
        })
    return HttpResponse(status=400)

@require_http_methods(["POST"])
@login_required
def create_customer(request):
    try:
        data = json.loads(request.body)
        # Check if email already exists for any of the user's teams
        user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
        if Customer.objects.filter(email=data['email'], teams__in=user_teams).exists():
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
        customer.teams.add(*user_teams)
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
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        if not customer.can_edit(request.user):
            raise PermissionDenied("You don't have permission to edit this customer.")
        data = json.loads(request.body)
        # Check if email is being changed and if it already exists for any of the user's teams
        user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
        if 'email' in data and data['email'] != customer.email:
            if Customer.objects.filter(email=data['email'], teams__in=user_teams).exclude(id=customer.id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'A customer with this email address already exists'
                }, status=400)
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
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        if not customer.can_edit(request.user):
            raise PermissionDenied("You don't have permission to delete this customer.")
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
    search_term = request.POST.get('search', '').strip()
    customers = Customer.objects.filter(teams__members__user=request.user, teams__members__is_active=True).distinct()
    if search_term:
        customers = customers.filter(
            name__icontains=search_term
        ) | customers.filter(
            email__icontains=search_term
        ) | customers.filter(
            company_name__icontains=search_term
        )
    # Add can_edit property for each customer and print debug info
    customer_list = []
    for customer in customers:
        customer.can_edit = customer.can_edit(request.user)
        print(f"DEBUG Customer: {customer.id}, can_edit: {customer.can_edit}, user: {request.user}, name: {customer.name}")
        customer_list.append(customer)
    return render(request, 'mycrm/customers_list.html', {
        'customers': customer_list
    })
