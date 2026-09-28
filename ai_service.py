import os
import json
from dotenv import load_dotenv
from groq import Groq
from services import add_stock, reduce_stock, query_stock, TOOL_REGISTRY
from database import record_zero_knowledge_billing, get_connection

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_stock",
            "description": "Add stock or register items into warehouse inventory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "unit_price": {"type": "number"}
                },
                "required": ["product_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reduce_stock",
            "description": "Log sale or dispatch of items from inventory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "integer"}
                },
                "required": ["product_name", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_stock",
            "description": "View current stock levels in the warehouse catalog. If product_name is omitted, null, or empty string, returns all items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": ["string", "null"],
                        "description": "Name of the specific product to search for, or null/empty string to view all products."
                    }
                }
            }
        }
    }
]

class InventoryAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=api_key)

    def send_user_message(self, user_text: str, client_id: int = 1, user_id: int = 1) -> dict:
        """
        Executes user prompt, scopes tool calling to tenant client_id,
        and logs zero-knowledge telemetry into the billing ledger.
        """
        # Pre-check: Ensure client has enough wallet balance
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT wallet_balance, rate_per_query FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Client #{client_id} does not exist.")

        wallet_bal, rate = row
        if wallet_bal < rate:
            raise ValueError(f"Insufficient funds (${wallet_bal:.2f}). Required rate: ${rate:.2f}/query. Please top up your wallet.")

        messages = [
            {"role": "system", "content": "You are an autonomous stock manager. Use tools to query or update warehouse stock accurately."},
            {"role": "user", "content": user_text}
        ]

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=GROQ_TOOLS,
            tool_choice="auto"
        )

        p_tokens = response.usage.prompt_tokens if response.usage else 0
        c_tokens = response.usage.completion_tokens if response.usage else 0
        response_msg = response.choices[0].message
        final_reply = ""

        if response_msg.tool_calls:
            messages.append(response_msg)
            tool_outputs = []

            for call in response_msg.tool_calls:
                func_name = call.function.name
                func_args = json.loads(call.function.arguments or "{}")

                # Sanitize nullable string fields
                if func_name == "query_stock":
                    if func_args.get("product_name") is None:
                        func_args["product_name"] = ""

                # Inject tenant scope
                func_args["client_id"] = client_id

                if func_name in TOOL_REGISTRY:
                    result = TOOL_REGISTRY[func_name](**func_args)
                    tool_outputs.append(result)
                    messages.append({
                        "tool_call_id": call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": result
                    })

            second_call = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            if second_call.usage:
                p_tokens += second_call.usage.prompt_tokens
                c_tokens += second_call.usage.completion_tokens

            final_reply = second_call.choices[0].message.content or "\n".join(tool_outputs)
        else:
            final_reply = response_msg.content or "Action completed."

        cost_charged, new_balance = record_zero_knowledge_billing(
            client_id=client_id,
            user_id=user_id,
            model=MODEL_NAME,
            p_tokens=p_tokens,
            c_tokens=c_tokens
        )

        return {
            "reply": final_reply,
            "cost_charged": cost_charged,
            "new_balance": new_balance,
            "tokens": p_tokens + c_tokens
        }
        