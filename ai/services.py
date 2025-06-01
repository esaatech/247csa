    # ai/services.py
import requests
import json

def get_ai_response(chat_input, session_id):
    n8n_url = 'https://38d1-147-194-133-23.ngrok-free.app/webhook/9d50356f-f1b4-469f-adc6-64a8a84102ad'
    payload = {"chatInput": chat_input, "sessionId": session_id}
    try:
        n8n_resp = requests.post(n8n_url, json=payload, timeout=10)
        n8n_resp.raise_for_status()
        n8n_data = n8n_resp.json()
        output_data = json.loads(n8n_data.get('output', '{}'))
        ai_reply = output_data.get('output', 'Sorry, I did not understand that.')
        ai_button = output_data.get('button', 'no')
        return ai_reply, ai_button
    except Exception as e:
        return 'Sorry, there was an error contacting the AI.', 'no'