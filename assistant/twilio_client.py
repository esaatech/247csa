from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class TwilioWhatsAppClient:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)

    def send_template_message(self, to_number, content_sid, variables):
        return self.client.messages.create(
            from_=f'whatsapp:{self.from_number}',
            content_sid=content_sid,
            content_variables=variables,
            to=f'whatsapp:{to_number}'
        ) 