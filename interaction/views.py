from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Interaction
import uuid
import json

DEFAULT_UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")

def test_view(request):
    """Test interface for the interaction app."""
    return render(request, 'interaction/test.html')

def add_interaction(request):
    """Render the add_interaction form. Expects activity_uuid as GET param or context."""
    activity_uuid = request.GET.get('activity_uuid')
    if not activity_uuid:
        activity_uuid = str(DEFAULT_UUID)
    return render(request, 'interaction/add_interaction.html', {'activity_uuid': activity_uuid})

def add_interaction_slide_out(request):
    """Render the slide-out container with the add_interaction form."""
    activity_uuid = request.GET.get('activity_uuid')
    if not activity_uuid:
        activity_uuid = str(DEFAULT_UUID)
    return render(request, 'interaction/add_interaction_slide_out_container.html', {'activity_uuid': activity_uuid})

def interaction_detail_slide_out(request, interaction_id):
    """Render the slide-out container with the interaction details/edit form."""
    interaction = get_object_or_404(Interaction, id=interaction_id)
    return render(request, 'interaction/interaction_detail_slide_out_container.html', {
        'interaction': interaction,
        'activity_uuid': interaction.activity_uuid
    })

@require_http_methods(["POST"])
def create_interaction(request):
    try:
        data = json.loads(request.body)
        activity_uuid_str = data.get('activity_uuid')
        if not activity_uuid_str:
            activity_uuid_str = str(DEFAULT_UUID)
            
        interaction = Interaction.objects.create(
            activity_uuid=uuid.UUID(activity_uuid_str),
            type=data['type'],
            medium=data['medium'],
            description=data['description'],
            created_by=request.user
        )
        return JsonResponse({'interaction_id': str(interaction.id), 'status': 'created'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["PUT", "PATCH"])
def update_interaction(request, interaction_id):
    try:
        interaction = get_object_or_404(Interaction, id=interaction_id)
        data = json.loads(request.body)
        
        # Update fields if they are provided
        if 'type' in data:
            interaction.type = data['type']
        if 'medium' in data:
            interaction.medium = data['medium']
        if 'description' in data:
            interaction.description = data['description']
        if 'activity_uuid' in data:
            interaction.activity_uuid = uuid.UUID(data['activity_uuid'])
            
        interaction.save()
        return JsonResponse({
            'status': 'updated',
            'interaction': {
                'id': str(interaction.id),
                'type': interaction.type,
                'medium': interaction.medium,
                'description': interaction.description,
                'activity_uuid': str(interaction.activity_uuid)
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def interactions_list(request):
    """Render the interactions list."""
    activity_uuid = request.GET.get('activity_uuid')
    if not activity_uuid:
        activity_uuid = str(DEFAULT_UUID)
    interactions = Interaction.objects.filter(activity_uuid=activity_uuid).order_by('-created_at')
    return render(request, 'interaction/interactions.html', {'interactions': interactions})

def interactions_right_slide_out(request):
    """Render the interactions list in a slide-out container."""
    activity_uuid = request.GET.get('activity_uuid')
    if not activity_uuid:
        activity_uuid = str(DEFAULT_UUID)
    interactions = Interaction.objects.filter(activity_uuid=activity_uuid).order_by('-created_at')
    return render(request, 'interaction/interactions_right_slide_out_container.html', {'interactions': interactions})

@require_http_methods(["DELETE"])
def delete_interaction(request, interaction_id):
    try:
        interaction = get_object_or_404(Interaction, id=interaction_id)
        interaction.delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
