from django.shortcuts import render, get_object_or_404
from platform_connections.models import ChatSession, Message
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from platform_connections.models import WebsiteChatConnection
from django.urls import reverse

# Create your views here.
def chat_window(request, session_id):
    """Render the chat window for a specific session"""
    session = get_object_or_404(ChatSession, id=session_id)
    messages = session.messages.all()
    
    return render(request, 'chatui/chat_window.html', {
        'chat_session': session,
        'messages': messages
    })

@require_http_methods(["POST"])
def send_message(request, session_id):
    """Handle sending a message from the chatui"""
    session = get_object_or_404(ChatSession, id=session_id)
    message = request.POST.get('message')
    
    if not message:
        return HttpResponse(status=400)
        
    # Save the message
    Message.objects.create(
        session=session,
        content=message,
        is_from_user=False  # This is from the agent
    )
    
    # For now, just echo back a response
    response_message = "I received your message!"
    Message.objects.create(
        session=session,
        content=response_message,
        is_from_user=True
    )
    
    # Return the response message HTML
    return render(request, 'chatui/message.html', {
        'message': response_message,
        'is_user': True
    })  