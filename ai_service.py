import os
import json
from dotenv import load_dotenv
from groq import Groq
from services import add_stock, reduce_stock, query_stock, TOOL_REGISTRY

load_dotenv()

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_stock",
            "description": "Add incoming stock to inventory or register a new product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "The title of the product/item."},
                    "quantity": {"type": "integer", "description": "Number of units to add."},
                    "unit_price": {"type": "number", "description": "Price per unit (optional)."}
                },
                "required": ["product_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reduce_stock",
            "description": "Record a sale, dispatch, or write-off of existing stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Name of the product sold."},
                    "quantity": {"type": "integer", "description": "Number of units sold."}
                },
                "required": ["product_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_stock",
            "description": "Inspect stock levels for a specific product or view all products.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Product name to look up. Leave empty to see all."}
                }
            }
        }
    }
]

class InventoryAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in your .env file.")
        self.client = Groq(api_key=api_key)
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert autonomous inventory manager. You track physical stock and ledger logs "
                    "by calling tools. Always use add_stock, reduce_stock, or query_stock when the user describes "
                    "inventory operations. Keep confirmations concise."
                )
            }
        ]

    def send_user_message(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=self.messages,
            tools=GROQ_TOOLS,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            self.messages.append(response_message)
            tool_outputs = []

            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                if func_name in TOOL_REGISTRY:
                    result = TOOL_REGISTRY[func_name](**func_args)
                    tool_outputs.append(result)

                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": result
                    })

            second_response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=self.messages
            )
            return second_response.choices[0].message.content or "\n".join(tool_outputs)

        reply = response_message.content or "Done."
        self.messages.append({"role": "assistant", "content": reply})
        return reply