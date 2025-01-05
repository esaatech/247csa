from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Email, WhatsAppMessage
from .serializers import EmailSerializer, WhatsAppMessageSerializer
from dotenv import load_dotenv
load_dotenv()  # Add these at the top with other imports
# Create your views here.
def assistant(request):
    return render(request, 'assistant/assistant.html')

def get_emails(request):
    pass






class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

class WhatsAppMessageViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppMessage.objects.all()
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated]



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WhatsAppMessage
import os

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        # Verification handshake with WhatsApp
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        # Get verification token from environment variable
        VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'default_token')
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return JsonResponse({"hub.challenge": challenge}, safe=False)
        return JsonResponse({"error": "Verification failed"}, status=403)

    elif request.method == "POST":
        # Handle incoming WhatsApp messages
        payload = json.loads(request.body.decode("utf-8"))
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if "messages" in change["value"]:
                    for message in change["value"]["messages"]:
                        # Save the message to the database
                        WhatsAppMessage.objects.create(
                            message_id=message["id"],
                            sender=message["from"],
                            body=message.get("text", {}).get("body", ""),
                            received_at=message.get("timestamp")
                        )
        return JsonResponse({"status": "received"}, status=200)
