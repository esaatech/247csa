from openai import OpenAI
from typing import Dict
import time
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Store assistant instances
assistants: Dict[str, str] = {}
threads: Dict[str, str] = {}

def create_assistant(user_id: str):
    """Create or get an assistant for a user"""
    if user_id not in assistants:
        assistant = client.beta.assistants.create(
            name="Customer Support",
            instructions=(
                "You are a friendly customer support assistant for esaathings. "
                "For product information, prices, contact details, and ordering, use ONLY the information explicitly stated here. "
                "For any questions about information not listed, respond with: 'I'm sorry, I don't have information about that. "
                "Please contact us at 613-240-8100 for assistance with your question.'\n\n"
                "Here is the information you can use:\n"
                "Our address is 1290, Albert Einstein Rd, Ottawa, "
                "and our phone number is 613-240-8100. "
                "We currently have the following items available: "
                "Desk (Black, 120x60x75 cm) - $150, Chair (Blue, 45x45x90 cm) - $85..."
            ),
            model="gpt-4-turbo-preview"
        )
        assistants[user_id] = assistant.id
    return assistants[user_id]

def create_thread(user_id: str):
    """Create or get a thread for a user"""
    if user_id not in threads:
        thread = client.beta.threads.create()
        threads[user_id] = thread.id
    return threads[user_id]

def openai_response(sender_message: str, user_id: str):
    # Get or create assistant and thread
    assistant_id = create_assistant(user_id)
    thread_id = create_thread(user_id)

    try:
        # Add the user's message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=sender_message
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Wait for the run to complete
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            time.sleep(1)

        # Get the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value

    except Exception as e:
        print(f"Error: {e}")
        return "I apologize, but I encountered an error. Please try again."

# Test section
if __name__ == "__main__":
    test_user_id = "test_user_123"
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
                
            response = openai_response(user_input, test_user_id)
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")