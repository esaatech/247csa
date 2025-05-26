from openai import OpenAI
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import time
import json
import logging
import httpx
from decimal import Decimal

# Disable HTTP request logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = OpenAI()

# Store instances
assistants: Dict[str, str] = {}
threads: Dict[str, str] = {}

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ReturnStatus(Enum):
    INITIATED = "initiated"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

@dataclass
class Product:
    id: str
    name: str
    price: Decimal
    stock: int
    dimensions: str

class InventoryManager:
    """Manages product inventory and details"""
    
    def __init__(self):
        self.products = {
            "DESK001": Product("DESK001", "Desk (Black)", Decimal("150"), 5, "120x60x75 cm"),
            "CHAIR001": Product("CHAIR001", "Chair (Blue)", Decimal("85"), 10, "45x45x90 cm"),
            # ... add other products
        }
    
    def check_stock(self, product_id: str) -> int:
        """Check available stock for a product"""
        if product_id in self.products:
            return self.products[product_id].stock
        return 0
    
    def get_product_details(self, product_id: str) -> Optional[Product]:
        """Get detailed product information"""
        return self.products.get(product_id)

class OrderManager:
    """Manages orders and returns"""
    
    def __init__(self):
        self.orders = {
            "ORD001": {"status": OrderStatus.DELIVERED, "items": ["DESK001"], "total": Decimal("150")},
            "ORD002": {"status": OrderStatus.PROCESSING, "items": ["CHAIR001"], "total": Decimal("85")},
        }
        self.returns = {}
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get the current status of an order"""
        if order := self.orders.get(order_id):
            return order["status"]
        return None
    
    def process_return(self, order_id: str, reason: str) -> dict:
        """Process a return request"""
        if order_id not in self.orders:
            return {"success": False, "message": "Order not found"}
            
        return_id = f"RET{len(self.returns) + 1:03d}"
        self.returns[return_id] = {
            "order_id": order_id,
            "status": ReturnStatus.INITIATED,
            "reason": reason
        }
        return {
            "success": True,
            "return_id": return_id,
            "status": ReturnStatus.INITIATED.value
        }

class ShippingCalculator:
    """Calculates shipping costs"""
    
    def __init__(self):
        self.base_rate = Decimal("10.00")
        self.per_km_rate = Decimal("0.50")
    
    def calculate_shipping(self, postal_code: str, weight: float) -> Decimal:
        """Calculate shipping cost based on postal code and weight"""
        # Simplified calculation for demo
        distance_factor = len(postal_code)
        return self.base_rate + (self.per_km_rate * distance_factor * Decimal(str(weight)))

class PaymentProcessor:
    """Handles payment processing"""
    
    def process_payment(self, amount: Decimal, payment_method: str) -> dict:
        """Process a payment"""
        success = True  # In real implementation, would integrate with payment gateway
        return {
            "success": success,
            "transaction_id": f"TXN{int(time.time())}",
            "amount": str(amount),
            "method": payment_method
        }

# Initialize managers
inventory_manager = InventoryManager()
order_manager = OrderManager()
shipping_calculator = ShippingCalculator()
payment_processor = PaymentProcessor()

def check_order_status(order_id: str) -> dict:
    """Check the status of an order"""
    logger.info(f"📦 Function called: check_order_status('{order_id}')")
    status = order_manager.get_order_status(order_id)
    if status:
        return {
            "success": True,
            "order_id": order_id,
            "status": status.value
        }
    return {
        "success": False,
        "message": "Order not found"
    }

def process_return(order_id: str, reason: str) -> dict:
    """Process a return request"""
    logger.info(f"↩️ Function called: process_return('{order_id}', '{reason}')")
    return order_manager.process_return(order_id, reason)

def get_product_details(product_id: str) -> dict:
    """Get detailed product information"""
    logger.info(f"🔍 Function called: get_product_details('{product_id}')")
    product = inventory_manager.get_product_details(product_id)
    if product:
        return {
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
                "stock": product.stock,
                "dimensions": product.dimensions
            }
        }
    return {
        "success": False,
        "message": "Product not found"
    }

def calculate_shipping(postal_code: str, weight: float) -> dict:
    """Calculate shipping cost"""
    logger.info(f"🚚 Function called: calculate_shipping('{postal_code}', {weight})")
    cost = shipping_calculator.calculate_shipping(postal_code, weight)
    return {
        "success": True,
        "cost": str(cost),
        "postal_code": postal_code,
        "weight": weight
    }

def check_inventory(product_id: str) -> dict:
    """Check product inventory"""
    logger.info(f"📊 Function called: check_inventory('{product_id}')")
    stock = inventory_manager.check_stock(product_id)
    return {
        "success": True,
        "product_id": product_id,
        "stock": stock
    }

def process_payment(amount: float, payment_method: str) -> dict:
    """Process a payment"""
    logger.info(f"💳 Function called: process_payment({amount}, '{payment_method}')")
    result = payment_processor.process_payment(Decimal(str(amount)), payment_method)
    return result

def contact_support(question: str) -> dict:
    """Handle questions that require support team assistance"""
    logger.info(f"🛠️ Function called: contact_support('{question}')")
    return {
        "message": f"I've logged your question: '{question}'. Please contact our support team at 613-240-8100 for assistance.",
        "logged": True,
        "support_number": "613-240-8100"
    }

def create_thread(user_id: str) -> str:
    """Create or get a thread for a user"""
    if user_id not in threads:
        thread = client.beta.threads.create()
        threads[user_id] = thread.id
    return threads[user_id]

def create_assistant(user_id: str) -> str:
    """Create or get an assistant for a user with function calling capabilities"""
    if user_id not in assistants:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "contact_support",
                    "description": "Contact support when information is not available or user requests human assistance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question or issue that needs support team assistance"
                            }
                        },
                        "required": ["question"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_order_status",
                    "description": "Check the current status of an order",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID to check"
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            },
            # ... (other function definitions as before)
        ]

        assistant = client.beta.assistants.create(
            name="Customer Support",
            instructions=(
                "You are a friendly customer support assistant for esaathings. "
                "\n\nFor product inquiries:"
                "\n1. If asked about items in our product list, provide the information."
                "\n2. If asked about items we don't sell, simply respond: 'I apologize, but we don't carry that item in our inventory.'"
                "\n3. For questions about product details in our list, use get_product_details function."
                "\n4. For stock checks of our products, use check_inventory function."
                
                "\n\nONLY use the contact_support function when:"
                "\n1. A customer explicitly asks to speak with a human agent"
                "\n2. A customer has a complex issue that requires human intervention"
                "\n3. A customer has a complaint that needs resolution"
                "\n4. Technical issues that can't be resolved through standard responses"
                
                "\n\nFor order-related functions:"
                "\n- Use check_order_status only for order status inquiries"
                "\n- Use process_return only when customer wants to return a purchased item"
                "\n- Use calculate_shipping when asked about delivery costs"
                "\n- Use process_payment only for payment processing queries"
                
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
                      ),
            model="gpt-4-turbo-preview",
            tools=tools
        )
        assistants[user_id] = assistant.id
    return assistants[user_id]

def handle_tool_calls(thread_id: str, run_id: str, tool_calls):
    """Handle any tool calls from the assistant"""
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        logger.info(f"🔧 Handling function: {function_name}")
        
        # Call the appropriate function based on the name
        if function_name == "contact_support":
            result = contact_support(args["question"])
        elif function_name == "check_order_status":
            result = check_order_status(args["order_id"])
        elif function_name == "process_return":
            result = process_return(args["order_id"], args["reason"])
        elif function_name == "get_product_details":
            result = get_product_details(args["product_id"])
        elif function_name == "calculate_shipping":
            result = calculate_shipping(args["postal_code"], args["weight"])
        elif function_name == "check_inventory":
            result = check_inventory(args["product_id"])
        elif function_name == "process_payment":
            result = process_payment(args["amount"], args["payment_method"])
        else:
            result = {"error": "Unknown function"}
            
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result)
                }
            ]
        )

def openai_response(sender_message: str, user_id: str) -> str:
    """Process a message and return the assistant's response"""
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

        # Wait for the run to complete or require action
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run_status.status == 'requires_action':
                handle_tool_calls(
                    thread_id,
                    run.id,
                    run_status.required_action.submit_tool_outputs.tool_calls
                )
            elif run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'expired']:
                return "I apologize, but I encountered an error. Please try again."
                
            time.sleep(1)

        # Get the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value

    except Exception as e:
        logger.error(f"Error: {e}")
        return "I apologize, but I encountered an error. Please try again."

# Test section
if __name__ == "__main__":
    test_user_id = "test_user_123"
    
    print("Chat started (type 'quit' to exit)")
    print("Available commands: quit, exit, bye")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGoodbye!")
                break
                
            response = openai_response(user_input, test_user_id)
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
                