from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.contenttypes.models import ContentType
from platform_connections.models import PlatformConnection
from csa.models import CSA
from secrets import token_urlsafe
from platform_connections.models import WebsiteChatConnection
from platform_connections.models import BasePlatformConnection
import json
from django.views.decorators.http import require_http_methods
import uuid
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_exempt

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
                print(f"Creating/updating connection for agent: {agent_uuid}")

                # Try to get existing connection
                connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
                
                if connection:
                    print(f"Found existing connection: {connection.id}")
                    # Only update is_connected status, keep the same token
                    connection.is_connected = True
                    connection.save()
                    print(f"Updated connection {connection.id} to connected")
                else:
                    # Create new connection with the token
                    connection = WebsiteChatConnection.objects.create(
                        agent_id=agent_uuid,
                        iframe_token=token,
                        theme='dark',
                        allowed_domains=["example.com"],
                        is_connected=True
                    )
                    print(f"Created new connection: {connection.id}")

                return JsonResponse({
                    'success': True,
                    'connection_id': str(connection.id),
                    'message': 'Website chat connection created successfully.'
                })

            except ValueError:
                print(f"Invalid UUID format for agent_id: {agent_id}")
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid agent ID format.'
                }, status=400)
                
        except json.JSONDecodeError:
            print("Invalid JSON data received")
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
        existing_connection = None  # Initialize existing_connection
        
        # Use new_agent_id if provided, otherwise use agent_id
        active_agent_id = new_agent_id if new_agent_id and new_agent_id != 'null' else agent_id
        
        # Check if connection exists and get its token
        if active_agent_id and active_agent_id != 'null':  # Add check for 'null' string
            try:
                agent_uuid = uuid.UUID(active_agent_id)
                existing_connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
                
                if existing_connection:
                    token = existing_connection.iframe_token
                    is_connected = existing_connection.is_connected
                    
            except ValueError:
                print(f"Invalid UUID format for agent_id: {active_agent_id}")
                # Keep default values

        return render(request, 'platform_connections/website_chat_config.html', {
            'title': 'Connect to Website Chat',
            'chat_id': {'id': active_agent_id},
            'connection_id': existing_connection.id if existing_connection and is_connected else None,
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
    print("Disconnect website chat called")
    try:
        print("Request body:", request.body)
        data = json.loads(request.body)
        print("Parsed data:", data)
        agent_id = data.get('agent_id')
        print("Agent ID:", agent_id)
        
        if not agent_id:
            print("Missing agent ID")
            return JsonResponse({
                'success': False,
                'error': 'Missing agent ID'
            }, status=400)

        try:
            agent_uuid = uuid.UUID(agent_id)
            print(f"Looking for connection with agent_id: {agent_uuid}")
            # Update the connection status instead of deleting
            connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
            
            if connection:
                print(f"Found connection: {connection.id}")
                connection.is_connected = False
                connection.save()
                print(f"Updated connection {connection.id} to disconnected")
                return JsonResponse({
                    'success': True,
                    'message': 'Website chat disconnected successfully.'
                })
            else:
                print("No connection found")
                return JsonResponse({
                    'success': False,
                    'error': 'No active connection found'
                }, status=404)

        except ValueError as e:
            print(f"Invalid UUID error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid agent ID format'
            }, status=400)

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error in disconnect_website_chat: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@xframe_options_exempt
@ensure_csrf_cookie
@require_http_methods(["GET"])
def chat_widget(request, website_id, token):
    try:
        print(f"Chat widget view called with website_id: {website_id}, token: {token}")
        print(f"Request path: {request.path}")
        
        # Get the website chat connection
        connection = get_object_or_404(WebsiteChatConnection, id=website_id, iframe_token=token)
        print(f"Found connection: {connection.id}, token: {connection.iframe_token}")
        
        if not connection.is_connected:
            print(f"Connection {connection.id} is not active")
            # Return empty response, 200 OK
            return HttpResponse("")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://unpkg.com/htmx.org@1.9.10"></script>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
            {render(request, 'platform_connections/chat_widget.html', {
                'connection': connection
            }).content.decode('utf-8')}
        </body>
        </html>
        """
        
        response = HttpResponse(html_content)
        
        # Add CORS headers
        response["Access-Control-Allow-Origin"] = request.headers.get('Origin', '*')
        response["Access-Control-Allow-Credentials"] = "true"
        
        return response
        
    except Exception as e:
        print(f"Error in chat_widget: {str(e)}")
        print(f"Connection details - ID: {website_id}, Token: {token}")
        # Print all connections for debugging
        all_connections = WebsiteChatConnection.objects.all()
        print("All connections in database:")
        for conn in all_connections:
            print(f"ID: {conn.id}, Token: {conn.iframe_token}, Connected: {conn.is_connected}")
        return JsonResponse({
            'error': str(e)
        }, status=500)

@xframe_options_exempt
@ensure_csrf_cookie
@require_http_methods(["GET"])
def chat_widget_container(request, website_id, token):
    try:
        print(f"Chat widget container view called with website_id: {website_id}, token: {token}")
        print(f"Request path: {request.path}")
        
        # Get the website chat connection
        connection = get_object_or_404(WebsiteChatConnection, id=website_id, iframe_token=token)
        print(f"Found connection: {connection.id}, token: {connection.iframe_token}")
        
        if not connection.is_connected:
            print(f"Connection {connection.id} is not active")
            # Return empty response, 200 OK
            return HttpResponse("")
        
        response = render(request, 'platform_connections/chat_widget_container.html', {
            'connection': connection
        })
        response["Access-Control-Allow-Origin"] = request.headers.get('Origin', '*')
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    except Exception as e:
        print(f"Error in chat_widget_container: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@xframe_options_exempt
@require_http_methods(["POST"])
def send_message(request, connection_id):
    """Handle incoming chat messages"""
    print(f"Send message view called with connection_id: {connection_id}")
    print(f"Request method: {request.method}")
    print(f"Request POST data: {request.POST}")
    print(f"Request headers: {request.headers}")
    
    try:
        connection = get_object_or_404(WebsiteChatConnection, id=connection_id)
        print(f"Found connection: {connection.id}")
        
        message = request.POST.get('message')
        print(f"Received message: {message}")
        
        if not message:
            print("No message provided")
            return JsonResponse({'error': 'Message is required'}, status=400)
            
        # Here you would typically:
        # 1. Save the message to your database
        # 2. Process it through your AI/chat system
        # 3. Return the response
        
        response = render(request, 'platform_connections/message.html', {
            'message': message,
            'is_user': True
        })
        
        # Add CORS headers
        response["Access-Control-Allow-Origin"] = request.headers.get('Origin', '*')
        response["Access-Control-Allow-Credentials"] = "true"
        
        return response
        
    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@xframe_options_exempt
@require_http_methods(["GET"])
def get_messages(request, connection_id):
    """Get chat history"""
    print(f"Get messages view called with connection_id: {connection_id}")
    try:
        connection = get_object_or_404(WebsiteChatConnection, id=connection_id)
        print(f"Found connection: {connection.id}")
        
        # Here you would typically:
        # 1. Fetch message history from your database
        # 2. Return the messages
        
        response = render(request, 'platform_connections/messages.html', {
            'messages': []  # Replace with actual messages
        })
        
        # Add CORS headers
        response["Access-Control-Allow-Origin"] = request.headers.get('Origin', '*')
        response["Access-Control-Allow-Credentials"] = "true"
        
        return response
        
    except Exception as e:
        print(f"Error in get_messages: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)