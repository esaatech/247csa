class WhatsAppProcessor:
    def __init__(self):
        pass

    def process_incoming_message(self, request_data):
        """
        Process incoming WhatsApp message data and extract relevant information.
        
        Args:
            request_data (dict): The parsed request data containing WhatsApp message information
            
        Returns:
            dict: Processed message data containing:
                - phone_number (str): Sender's phone number
                - message (str): Message content
                - media_url (str, optional): URL of any media content
                - location (dict, optional): Location data if shared
        """
        try:
            # Extract basic message information
            phone_number = request_data.get('From', [''])[0].replace('whatsapp:', '')
            message = request_data.get('Body', [''])[0]
            
            # Initialize response dictionary
            processed_data = {
                'phone_number': phone_number,
                'message': message,
            }

            # Check for media content
            num_media = int(request_data.get('NumMedia', ['0'])[0])
            if num_media > 0:
                media_types = request_data.get('MediaContentType0', [''])
                media_urls = request_data.get('MediaUrl0', [''])
                processed_data['media'] = {
                    'type': media_types[0] if media_types else None,
                    'url': media_urls[0] if media_urls else None
                }

            # Check for location data
            if 'Latitude' in request_data and 'Longitude' in request_data:
                processed_data['location'] = {
                    'latitude': request_data.get('Latitude', [''])[0],
                    'longitude': request_data.get('Longitude', [''])[0]
                }

            return processed_data

        except Exception as e:
            raise Exception(f"Error processing WhatsApp message: {str(e)}")
