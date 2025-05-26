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
# Load environment variables from .env file
load_dotenv()

# Twilio credentials from environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_messenger_id = os.getenv("TWILIO_MESSENGER_ID")  # Your Twilio Messenger SID
facebook_page_id = os.getenv("FACEBOOK_PAGE_ID")  # Your Facebook Page ID

# Initialize Twilio Client
client = Client(account_sid, auth_token)

@csrf_exempt
def handle_outgoing_message(request):
    """
    Handle incoming Facebook Messenger messages via Twilio and send a response.
    """
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
            print(f"Received message from {messenger_user_id}: {incoming_message}")

            # Formulate a response message
            response_message = f"Thanks for your message! You said: {incoming_message}"

            # Send a response to the user via Twilio
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
def handle_incoming_message(request):
    """
    process incoming message from facebook messenger
    """
    if request.method == "POST":
        try:
            # Parse the incoming request body
            incoming_data = parse_qs(request.body.decode("utf-8"))

            # Extract details
            message_sid = incoming_data.get("SmsMessageSid", [None])[0]
            from_user = incoming_data.get("From", [None])[0]
            to_user = incoming_data.get("To", [None])[0]
            body = incoming_data.get("Body", [""])[0]

            # Print the details to the command line
            print(f"Message SID: {message_sid}")
            print(f"From (Messenger User ID): {from_user}")
            print(f"To (Facebook Page ID): {to_user}")
            print(f"Message Body: {body}")

            # Return a success response
            return JsonResponse({"status": "Message received", "message_body": body}, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Webhook is ready to receive POST requests."}, status=200)        
    


