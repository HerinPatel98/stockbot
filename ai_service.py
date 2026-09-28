import os
import json
from dotenv import load_dotenv
from groq import Groq
from services import add_stock, reduce_stock, query_stock, delete_stock, TOOL_REGISTRY
from database import record_zero_knowledge_billing, get_connection

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_stock",
            "description": "Restock an existing product or register a new catalog SKU. Use this whenever adding or registering items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "The exact name of the product."},
                    "quantity": {"type": "integer", "description": "Number of units to add."},
                    "unit_price": {"type": "number", "description": "Optional unit price."},
                    "is_new_sku": {"type": "boolean", "description": "Set to true if user explicitly asks to register a new product or create a new SKU."}
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
            "description": "View current stock levels in the warehouse catalog.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "delete_stock",
            "description": "Purge an entire product SKU from catalog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "confirm": {"type": "boolean"}
                },
                "required": ["product_name"]
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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT wallet_balance, rate_per_query FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Client #{client_id} does not exist.")

        wallet_bal, rate = row
        if wallet_bal < rate:
            raise ValueError(f"Insufficient funds (${wallet_bal:.2f}). Required rate:${rate:.2f}/query. Please top up your wallet.")

        raw_has_new_intent = any(w in user_text.lower() for w in ["new sku", "new product", "new item", "register", "create"])

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an autonomous stock manager. Use ONLY the declared tools: "
                    "`add_stock`, `reduce_stock`, `query_stock`, `delete_stock`. "
                    "Do NOT invent other tool names like register_sku. "
                    "To create a new product or register a SKU, call `add_stock` with `is_new_sku: true`."
                )
            },
            {"role": "user", "content": user_text}
        ]

        # 1. First Call: Tool Decision
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

        # 2. Tool Execution
        if response_msg.tool_calls:
            messages.append(response_msg)
            tool_outputs = []

            for call in response_msg.tool_calls:
                func_name = call.function.name
                func_args = json.loads(call.function.arguments or "{}")

                # Map any hallucinated names to add_stock
                if func_name in ["register_sku", "create_sku", "create_product"]:
                    func_name = "add_stock"
                    func_args["is_new_sku"] = True
                    if "quantity" not in func_args:
                        func_args["quantity"] = 1

                if func_name == "query_stock" and func_args.get("product_name") is None:
                    func_args["product_name"] = ""

                if func_name == "add_stock" and raw_has_new_intent:
                    func_args["is_new_sku"] = True

                if func_name == "delete_stock":
                    if "confirm" in user_text.lower():
                        func_args["confirm"] = True

                func_args["client_id"] = client_id

                if func_name in TOOL_REGISTRY:
                    result = TOOL_REGISTRY[func_name](**func_args)
                else:
                    result = f"Error: Unknown action '{func_name}'."

                tool_outputs.append(result)
                messages.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": result
                })

            # 3. Follow-up synthesis call
            try:
                # Include tools parameter to prevent Groq 400 'tool choice is none' error
                second_call = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=GROQ_TOOLS
                )
                if second_call.usage:
                    p_tokens += second_call.usage.prompt_tokens
                    c_tokens += second_call.usage.completion_tokens

                # If the second call generated text, use it; otherwise use tool output
                second_msg = second_call.choices[0].message
                final_reply = second_msg.content or "\n".join(tool_outputs)
            except Exception:
                # Fallback directly to verified tool output if LLM attempts recursive tool calling
                final_reply = "\n".join(tool_outputs)
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