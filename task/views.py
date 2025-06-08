from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Task
import uuid
import json
from django.utils.dateparse import parse_datetime
from django.utils import timezone

# Create your views here.

DEFAULT_UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")

def test_view(request):
    """Test interface for the task app."""
    return render(request, 'task/test.html')

def add_task(request):
    """Render the add_task form. Expects task_uuid as GET param or context."""
    task_uuid = request.GET.get('task_uuid')
    if not task_uuid:
        task_uuid = str(DEFAULT_UUID)
    return render(request, 'task/add_task.html', {'task_uuid': task_uuid})

def add_task_slide_out(request):
    """Render the slide-out container with the add_task form."""
    task_uuid = request.GET.get('task_uuid')
    if not task_uuid:
        task_uuid = str(DEFAULT_UUID)
    return render(request, 'task/add_task_slide_out_container.html', {'task_uuid': task_uuid})

@require_http_methods(["POST"])
def create_task(request):
    try:
        data = json.loads(request.body)
        print('Received data:', data)  # Debug print
        task_uuid_str = data.get('task_uuid')
        if not task_uuid_str:
            task_uuid_str = str(DEFAULT_UUID)
        due_date_str = data.get('due_date')
        due_date = None
        if due_date_str:
            # Try parsing as ISO format first, then as naive and localize
            dt = parse_datetime(due_date_str.replace(' ', 'T'))  # Flatpickr gives 'YYYY-MM-DD HH:mm'
            if dt is not None and timezone.is_naive(dt):
                due_date = timezone.make_aware(dt)
            else:
                due_date = dt
        task = Task.objects.create(
            task_uuid=uuid.UUID(task_uuid_str),
            title=data['title'],
            description=data.get('description', ''),
            due_date=due_date,
            priority=data.get('priority', 'medium')
        )
        return JsonResponse({'task_id': str(task.id), 'status': 'created'})
    except Exception as e:
        print('Error in create_task:', e)  # Debug print
        return JsonResponse({'error': str(e)}, status=400)

def tasks_list(request):
    print(".............tasks_list.................")    
    """Render the tasks list for the slide-out container."""
    task_uuid = request.GET.get('task_uuid')
    if not task_uuid:
        task_uuid = str(DEFAULT_UUID)
    tasks = Task.objects.filter(task_uuid=task_uuid).order_by('-created_at')
    print(f"Fetching tasks for task_uuid={task_uuid}, found {tasks.count()} tasks.")  # Debug print
    return render(request, 'task/tasks.html', {'tasks': tasks})

def tasks_right_slide_out(request):
    print(".............tasks_right_slide_out.................")
    task_uuid = request.GET.get('task_uuid')
    if not task_uuid:
        task_uuid = str(DEFAULT_UUID)
    tasks = Task.objects.filter(task_uuid=task_uuid).order_by('-created_at')
    print(f"Fetching tasks for task_uuid={task_uuid}, found {tasks.count()} tasks.")  # Debug print
    return render(request, 'task/tasks_right_slide_out_container.html', {'tasks': tasks})

@require_http_methods(["POST"])
def update_task(request, task_id):
    try:
        data = json.loads(request.body)
        task = get_object_or_404(Task, id=task_id)
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'due_date' in data:
            dt = parse_datetime(data['due_date'].replace(' ', 'T'))
            if dt is not None and timezone.is_naive(dt):
                task.due_date = timezone.make_aware(dt)
            else:
                task.due_date = dt
        if 'priority' in data:
            task.priority = data['priority']
        task.save()
        return JsonResponse({'status': 'updated'})
    except Exception as e:
        print('Error in update_task:', e)
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        print('Error in delete_task:', e)
        return JsonResponse({'error': str(e)}, status=400)
