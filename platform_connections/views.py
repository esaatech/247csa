from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
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
from .models import ChatSession, Message
import asyncio
from asgiref.sync import sync_to_async
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .consumers import notify_session_ended

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
            # Handle form data instead of JSON
            agent_id = request.POST.get('agent_id')
            token = request.POST.get('token')
            custom_icon = request.FILES.get('custom_icon')

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
                    # Update connection
                    connection.is_connected = True
                    if custom_icon:
                        connection.custom_icon = custom_icon
                    connection.save()
                    print(f"Updated connection {connection.id}")
                else:
                    # Create new connection
                    connection = WebsiteChatConnection.objects.create(
                        agent_id=agent_uuid,
                        iframe_token=token,
                        theme='dark',
                        allowed_domains=["example.com"],
                        is_connected=True,
                        custom_icon=custom_icon
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
                
        except Exception as e:
            print("Error in website_chat_config:", str(e))
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    else:
        # Handle GET request
        agent_id = request.GET.get('agent_id')
        new_agent_id = request.GET.get('newagent_id')
        
        print(".............agent_id.................", agent_id)
        print(".............new_agent_id.................", new_agent_id)
        
        # Initialize default values
        token = token_urlsafe(32)
        is_connected = False
        existing_connection = None
        
        # Use new_agent_id if provided, otherwise use agent_id
        active_agent_id = new_agent_id if new_agent_id and new_agent_id != 'null' else agent_id
        
        # Check if connection exists and get its token
        if active_agent_id and active_agent_id != 'null':
            try:
                agent_uuid = uuid.UUID(active_agent_id)
                existing_connection = WebsiteChatConnection.objects.filter(agent_id=agent_uuid).first()
                
                if existing_connection:
                    token = existing_connection.iframe_token
                    is_connected = existing_connection.is_connected
                    
            except ValueError:
                print(f"Invalid UUID format for agent_id: {active_agent_id}")

        return render(request, 'platform_connections/website_chat_config.html', {
            'title': 'Connect to Website Chat',
            'chat_id': {'id': active_agent_id},
            'connection_id': existing_connection.id if existing_connection and is_connected else None,
            'token': token,
            'is_connected': is_connected,
            'custom_icon': existing_connection.custom_icon if existing_connection else None
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

def chat_session_list(request, agent_id):
    chat_sessions = ChatSession.objects.filter(agent_id=agent_id).order_by('-is_active', '-last_activity_at')
    for s in chat_sessions:
        print(f"Session {s.id}: handling_mode={s.handling_mode}")
    return render(request, 'platform_connections/chat_session_list.html', {
        'chat_sessions': chat_sessions,
        'agent_id': agent_id
    })

async def chat_events(request, session_id):
    """Server-Sent Events endpoint for chat updates"""
    print(f"Chat events view called with session_id: {session_id}")
    async def event_stream():
        try:
            chat_session = await sync_to_async(ChatSession.objects.get)(id=session_id)

            last_message_id = None

            def get_latest_message():
                return Message.objects.filter(session=chat_session).order_by('-created_at').first()

            while True:
                latest_message = await sync_to_async(get_latest_message)()
                
                # If we have a new message and it's from the agent
                if latest_message and (not last_message_id or latest_message.id != last_message_id):
                    if not latest_message.is_from_user:  # Only send agent messages
                        # Format the message for SSE
                        message_data = {
                            'id': str(latest_message.id),
                            'content': latest_message.content,
                            'is_user': latest_message.is_from_user,
                            'created_at': latest_message.created_at.isoformat()
                        }
                        
                        # Send the message as an SSE event
                        yield f"data: {json.dumps(message_data)}\n\n"
                        last_message_id = latest_message.id
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error in event_stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response["Access-Control-Allow-Origin"] = request.headers.get('Origin', '*')
    response["Access-Control-Allow-Credentials"] = "true"
    return response

@csrf_exempt
def init_chat_session(request, connection_id):
    """Initialize or get a chat session for the chat widget browser session ID."""
    print(f"............Init chat session view called with connection_id:......... {connection_id}")
    import json
    try:
        connection = get_object_or_404(WebsiteChatConnection, id=connection_id)
        data = json.loads(request.body.decode('utf-8'))
        browser_session_id = data.get('browser_session_id')
        if not browser_session_id:
            return JsonResponse({'error': 'browser_session_id required'}, status=400)
        session_tracking = connection.session_tracking or {}
        chat_session_id = session_tracking.get(browser_session_id)
        if chat_session_id:
            try:
                chat_session = ChatSession.objects.get(id=chat_session_id)
            except ChatSession.DoesNotExist:
                chat_session = None
        else:
            chat_session = None
        if not chat_session:
            chat_session = ChatSession.objects.create(
                agent_id=connection.agent_id,
                platform_type='website',
                user_identifier=browser_session_id
            )
            session_tracking[browser_session_id] = str(chat_session.id)
            connection.session_tracking = session_tracking
            connection.save()
            # Notify dashboard
            notify_agent_dashboard({
                'event': 'new_session',
                'session_id': str(chat_session.id),
                'user_identifier': browser_session_id,
                'platform_type': 'website',
                # Add more fields as needed
            })
        return JsonResponse({'session_id': str(chat_session.id)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def notify_agent_dashboard(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'agent_dashboard',
        {
            'type': 'session_update',
            'data': data
        }
    )

@require_POST
def end_chat_session(request, session_id):
    try:
        chat_session = ChatSession.objects.get(id=session_id)
        chat_session.is_active = False
        chat_session.save()
        # Notify both agent and user via WebSocket
        notify_session_ended(session_id)
        # Also notify agent dashboard to refresh session list
        notify_agent_dashboard({
            'event': 'session_update',
            'session_id': str(chat_session.id),
            'user_identifier': chat_session.user_identifier,
            'platform_type': chat_session.platform_type,
            'is_active': chat_session.is_active,
            'last_activity_at': chat_session.last_activity_at.isoformat(),
        })
        return JsonResponse({'success': True})
    except ChatSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)

@require_POST
def delete_chat_session(request, session_id):
    try:
        chat_session = ChatSession.objects.get(id=session_id)
        # Delete all messages for this session
        Message.objects.filter(session=chat_session).delete()
        # Delete the session itself
        chat_session.delete()
        # Notify agent dashboard to refresh session list
        notify_agent_dashboard({
            'event': 'session_update',
            'session_id': str(session_id),
            'deleted': True
        })
        return JsonResponse({'success': True})
    except ChatSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)

@csrf_exempt
@require_POST
def set_handling_mode(request, session_id):
    try:
        data = json.loads(request.body)
        mode = data.get('mode')
        if mode not in ['ai', 'human']:
            return JsonResponse({'success': False, 'error': 'Invalid mode'}, status=400)
        session = ChatSession.objects.get(id=session_id)
        session.handling_mode = mode
        session.save()
        # Optionally, broadcast mode change to clients via WebSocket
        notify_agent_dashboard({
            'event': 'session_update',
            'session_id': str(session.id),
            'user_identifier': session.user_identifier,
            'platform_type': session.platform_type,
            'handling_mode': session.handling_mode,
            'last_activity_at': session.last_activity_at.isoformat(),
        })
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["POST"])
def update_chat_widget_icon(request, website_id, token):
    try:
        connection = get_object_or_404(WebsiteChatConnection, id=website_id, iframe_token=token)
        custom_icon = request.FILES.get('custom_icon')
        if not custom_icon:
            return JsonResponse({'success': False, 'error': 'No icon file provided.'}, status=400)
        connection.custom_icon = custom_icon
        connection.save()
        return JsonResponse({'success': True, 'icon_url': connection.custom_icon.url})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



