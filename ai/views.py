from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import JsonResponse

    
# Create your views here.
def ai_view(request):
    return render(request, 'ai/ai.html')


@csrf_exempt
@require_POST
def process_chat_message(request):
    """
    Receives a chat message, sends it to the n8n AI endpoint, and returns the AI's response.
    Expects JSON: {"chatInput": <str>, "sessionId": <str>}
    Returns: {"output": <str>, "button": <str>}
    """
    import json
    try:
        data = json.loads(request.body)
        chat_input = data.get('chatInput')
        session_id = data.get('sessionId')
        if not chat_input or not session_id:
            return JsonResponse({'error': 'Missing chatInput or sessionId'}, status=400)
        # Call the n8n endpoint
        n8n_url = 'https://38d1-147-194-133-23.ngrok-free.app/webhook/9d50356f-f1b4-469f-adc6-64a8a84102ad'
        payload = {"chatInput": chat_input, "sessionId": session_id}
        try:
            n8n_resp = requests.post(n8n_url, json=payload, timeout=10)
            n8n_resp.raise_for_status()
            n8n_data = n8n_resp.json()
            # n8n returns output as a stringified JSON
            output_data = json.loads(n8n_data.get('output', '{}'))
            ai_reply = output_data.get('output', 'Sorry, I did not understand that.')
            ai_button = output_data.get('button', 'no')
            return JsonResponse({'output': ai_reply, 'button': ai_button})
        except Exception as e:
            return JsonResponse({'output': 'Sorry, there was an error contacting the AI.', 'button': 'no', 'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
