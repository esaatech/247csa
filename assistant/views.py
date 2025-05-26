from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Email, WhatsAppMessage
from .serializers import EmailSerializer, WhatsAppMessageSerializer
from dotenv import load_dotenv
from django.http import HttpResponse
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from dotenv import load_dotenv
import json
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import parse_qs
import time
import requests
from django.urls import reverse
from twilio.rest import Client as thisClient
from test.test_openai import openai_response
import logging
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)



load_dotenv()  # Add these at the top with other imports
# Create your views here.



print(f"TWILIO_ACCOUNT_SID top of views.py ........: {os.getenv('TWILIO_ACCOUNT_SID')}")
print(f"TWILIO_AUTH_TOKEN top of views.py ..............: {os.getenv('TWILIO_AUTH_TOKEN')}")











from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import WhatsAppMessage
import os
from .twilio_client import TwilioWhatsAppClient
from twilio.twiml.messaging_response import MessagingResponse

# Add debug logging
print(f"TWILIO_ACCOUNT_SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
print(f"TWILIO_AUTH_TOKEN: {os.getenv('TWILIO_AUTH_TOKEN')}")

twilio_client = TwilioWhatsAppClient()

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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    if request.method == 'GET':
        # Handle WhatsApp verification
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        # Log verification attempt
        logger.info(f"Webhook verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}")
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                # Convert challenge to integer and return
                try:
                    challenge_int = int(challenge)
                    logger.info(f"Webhook verified successfully with challenge: {challenge_int}")
                    return HttpResponse(challenge_int)
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid challenge value: {challenge}. Error: {str(e)}")
                    return HttpResponse('Invalid challenge value', status=400)
            else:
                logger.warning("Invalid verification token or mode")
                return HttpResponse('Invalid verification token', status=403)
        else:
            logger.warning("Missing verification parameters")
            return HttpResponse('Missing parameters', status=400)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received WhatsApp webhook: {data}")
            
            # Extract message data
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            message = value['messages'][0]
            
            """ 
            # Get or create conversation
            conversation, created = WhatsAppConversation.objects.get_or_create(
                customer_id=message['from'],
                defaults={
                    'customer_phone': message['from'],
                    'status': 'active'
                }
            )
            """
            conversation = None
            
            # Save message
            WhatsAppMessage.objects.create(
                conversation=conversation,
                message_id=message['id'],
                direction='incoming',
                content=message.get('text', {}).get('body', ''),
                media_url=message.get('media', {}).get('url', ''),
                media_type=message.get('type', 'text'),
                status='received'
            )
            
            logger.info(f"Saved WhatsApp message from {message['from']}")
            return HttpResponse('OK')
            
        except KeyError as e:
            logger.error(f"Invalid webhook data structure: {str(e)}")
            return HttpResponse('Invalid webhook data', status=400)
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {str(e)}")
            return HttpResponse('Error processing webhook', status=500)   



@csrf_exempt
def send_whatsapp_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            to_number = data.get('to')
            
            # Send template message
            message = twilio_client.send_template_message(
                to_number=to_number,
                content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
                variables='{"1":"12/1","2":"3pm"}'
            )
            
            return JsonResponse({
                'status': 'success',
                'message_sid': message.sid
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)



# Twilio credentials from environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_messenger_id = os.getenv("TWILIO_MESSENGER_ID")  # Your Twilio Messenger SID
facebook_page_id = os.getenv("FACEBOOK_PAGE_ID")  # Your Facebook Page ID

# Initialize Twilio Client
client = Client(account_sid, auth_token)

@csrf_exempt
def facebook_messenger(request):
    
    if request.method == "POST":
        try:
            # Parse incoming JSON request
            incoming_data = json.loads(request.body)

            # Extract messenger user ID and incoming message
            messenger_user_id = incoming_data.get("sender_id")
            incoming_message = incoming_data.get("message")

            if not messenger_user_id or not incoming_message:
                return JsonResponse({"error": "Invalid request data"}, status=400)

            # Log received message
            #print(f"Received message from {messenger_user_id}: {incoming_message}")

            # Formulate a response message
            #response_message = f"Thanks! did you mean : {incoming_message}"
            # Send a response to the user via Twilio
            
            response_message = openai_response(incoming_message)
            message = client.messages.create(
                to=f"messenger:{messenger_user_id}",
                from_=f"messenger:{facebook_page_id}",
                body=response_message,
            )

            # Log sent message
            print(f"Sent message: {message.body}")

            return JsonResponse({"status": "Message sent", "message_sid": message.sid}, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Webhook is active."}, status=200)




    

@csrf_exempt
def facebook_messenger_webhook(request):
    """
    Webhook to receive Facebook Messenger messages and print details to the command line.
    
    Handle incoming Facebook Messenger messages via Twilio and send a response.

    This endpoint processes incoming Facebook Messenger messages received through Twilio's API.
    It extracts the sender ID and message content, logs the received message, formulates a 
    response, and sends it back to the user via Twilio.

    Args:
        request: HTTP request object containing the message data in JSON format
                Expected format: {"sender_id": "<messenger_user_id>", "message": "<message_text>"}

    Returns:
        JsonResponse with status and details:
        - On success: {"status": "Message sent", "message_sid": "<twilio_message_sid>"}, status 200
        - On invalid data: {"error": "Invalid request data"}, status 400 
        - On error: {"error": "<error_message>"}, status 500
        - On GET request: {"message": "Webhook is active."}, status 200

    Raises:
        Exception: If there are any errors in processing the message or sending the response
    
    
    
    """
    if request.method == "POST":
        try:
            # Parse URL-encoded data
            incoming_data = parse_qs(request.body.decode('utf-8'))
            messenger_user_id = incoming_data.get("From", [None])[0].replace('messenger:', '')
            incoming_message = incoming_data.get("Body", [None])[0]

            if not messenger_user_id or not incoming_message:
                return JsonResponse({"error": "Invalid request data"}, status=400)

            # Log received message
            print(f"Received message from {messenger_user_id}: {incoming_message}")

            # Simulate a delayed response
            #time.sleep(5)

            

            url = request.build_absolute_uri(reverse('assistant:facebook_messenger'))
            
            response = requests.post(url, json={
                'sender_id': messenger_user_id,
                'message': incoming_message
            })

            # Log the response from the facebook_messenger endpoint
            print(f"Response status: {response.status_code}, Response body: {response.text}")

            return JsonResponse({"status": "Message sent"}, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Webhook is active."}, status=200)        
    




