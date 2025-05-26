from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from platform_connections.models import PlatformConnection
from csa.models import CSA
from secrets import token_urlsafe
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from platform_connections.models import PlatformConnection
from csa.models import CSA
from secrets import token_urlsafe
from platform_connections.models import WebsiteChatConnection
from platform_connections.models import BasePlatformConnection
import json
from django.views.decorators.http import require_http_methods
import uuid

# Create your views here.

def platforms_connect(request):
    # Get the CSA ID from the request
    agent_id = request.GET.get('agent_id')
    print(".............agent_id.................", agent_id)
    
    if agent_id:
        try:
            agent_uuid = uuid.UUID(agent_id)
            # Get platform connections status
            platform_status = BasePlatformConnection.get_connected_platforms(agent_uuid)
        except ValueError:
            platform_status = {
                'website_chat': {'is_connected': False, 'connection_id': None},
                'sms': {'is_connected': False, 'connection_id': None}
            }
    else:
        platform_status = {
            'website_chat': {'is_connected': False, 'connection_id': None},
            'sms': {'is_connected': False, 'connection_id': None}
        }

    return render(request, 'platform_connections/platforms_connect.html', {
        'platform_status': platform_status
    })

@require_http_methods(["GET", "POST"])
def website_chat_config(request):
    print("website_chat_config called")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)
            
            agent_id = data.get('agent_id')
            token = data.get('token')

            if not agent_id or not token:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields'
                }, status=400)

            try:
                agent_uuid = uuid.UUID(agent_id)

                # Try to get existing connection
                connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
                
                if connection:
                    # Only update is_connected status, keep the same token
                    connection.is_connected = True
                    connection.save()
                else:
                    # Create new connection with the token
                    connection = WebsiteChatConnection.objects.create(
                        agent_id=agent_uuid,
                        iframe_token=token,
                        theme='dark',
                        allowed_domains=["example.com"],
                        is_connected=True
                    )

                return JsonResponse({
                    'success': True,
                    'connection_id': str(connection.id),
                    'message': 'Website chat connection created successfully.'
                })

            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid agent ID format.'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Exception as e:
            print("Error in website_chat_config:", str(e))
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    else:
        # Handle GET request
        agent_id = request.GET.get('agent_id') # get the agent_id if one exists
        new_agent_id = request.GET.get('newagent_id') # get the new agent_id if one exists

        print(".............agent_id.................", agent_id)
        print(".............new_agent_id.................", new_agent_id)
        
        # Initialize default values
        token = token_urlsafe(32)
        is_connected = False
        
        # Check if connection exists and get its token
        if agent_id and agent_id != 'null':  # Add check for 'null' string
            try:
                agent_uuid = uuid.UUID(agent_id)
                existing_connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
                
                if existing_connection:
                    token = existing_connection.iframe_token
                    is_connected = existing_connection.is_connected
                    
            except ValueError:
                print(f"Invalid UUID format for agent_id: {agent_id}")
                # Keep default values

        return render(request, 'platform_connections/website_chat_config.html', {
            'title': 'Connect to Website Chat',
            'chat_id': {'id': new_agent_id},
            'token': token,
            'is_connected': is_connected
        })

def sms_config(request):
    return render(request, 'platform_connections/sms_config.html')

def get_agent_connections(request, agent_id):
    """Get all platform connections for an agent"""
    try:
        agent_uuid = uuid.UUID(agent_id)
        platform_status = BasePlatformConnection.get_connected_platforms(agent_uuid)
        return JsonResponse({
            'success': True,
            'platforms': platform_status
        })
    except ValueError as e:
        print(f"Invalid UUID error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid agent ID format'
        }, status=400)
    except Exception as e:
        print(f"Error in get_agent_connections: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["POST"])
def disconnect_website_chat(request):
    try:
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing agent ID'
            }, status=400)

        try:
            agent_uuid = uuid.UUID(agent_id)
            # Update the connection status instead of deleting
            connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
            
            if connection:
                connection.is_connected = False
                connection.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Website chat disconnected successfully.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No active connection found'
                }, status=404)

        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid agent ID format'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print("Error in disconnect_website_chat:", str(e))
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)