from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
def openai_response(sender_message):
    # Set your OpenAI API key
      # Replace with your actual API key

    # Define the messages for the chat completion
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a friendly customer support assistant for esaathings. "
                "\n\nFor product inquiries:"
                "\n1. If asked about items in our product list, provide the information."
                "\n2. If asked about items we don't sell, simply respond: 'I apologize, but we don't carry that item in our inventory.'"
                
                "\n\n provide customer with our contact information 6132408100 and email support@esaathings.com, if "              
                "\n1. A customer explicitly asks to speak with a human agent"
                "\n2. A customer has a complex issue that requires human intervention"
                "\n3. A customer has a complaint that needs resolution"
                "\n4. Technical issues that can't be resolved through standard responses"
                
                
                "\n\nHere is the information about our products:"
                "\nOur address is 1290, Albert Einstein Rd, Ottawa, "
                "and our phone number is 613-240-8100. "
                "\nWe currently have the following items available: "
                "Desk (Black, 120x60x75 cm) - $150, Chair (Blue, 45x45x90 cm) - $85, "
                "TV Stand (White, 150x40x50 cm) - $200, Makeup Table (Pink, 100x50x140 cm) - $250, "
                "Bookshelf (Brown, 80x30x180 cm) - $120, Dining Table (Oak, 200x100x75 cm) - $300, "
                "Sofa (Grey, 220x90x85 cm) - $400, Coffee Table (Glass, 100x50x45 cm) - $100, "
                "Bed Frame (Queen, Walnut, 210x160x100 cm) - $350, Wardrobe (White, 180x60x200 cm) - $450, "
                "Nightstand (Cherry, 50x40x60 cm) - $75, Office Chair (Ergonomic, Black, 70x70x120 cm) - $180, "
                "Recliner (Leather, Brown, 100x90x100 cm) - $500, TV Cabinet (Black, 120x40x60 cm) - $220, "
                "Dresser (White, 120x50x80 cm) - $300. "
                "\nTo place an order, please visit our website at: https://www.esaathings.com/order"
                
                "\n\nExample responses:"
                "\nQ: 'Do you sell refrigerators?' A: 'I apologize, but we don't carry refrigerators in our inventory.'"
                "\nQ: 'What color is the desk?' A: 'The desk comes in Black and measures 120x60x75 cm.'"
            )
        },
        {"role": "user", "content": sender_message}
    ]

    try:
        # Create a chat completion
        completion = client.chat.completions.create(model="gpt-4-turbo-preview",  # Specify the model
        messages=messages,
        max_tokens=150,
        temperature=0.7)

        # Extract the response text
        ai_response = completion.choices[0].message.content.strip()
        return ai_response

    except Exception as e:
        return f"An error occurred: {str(e)}"






if __name__ == "__main__":
    test_message = "and whats your phone number?"
    print(openai_response(test_message))

