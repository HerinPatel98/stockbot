import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load API Key from .env
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file.")
    exit(1)

client = Groq(api_key=api_key)

print(f"🔑 Key detected: {api_key[:8]}... (Length: {len(api_key)})")

# 2. List all accessible chat models for your account
print("\n🔍 Checking available text/chat models on your account:")
chat_models = []
try:
    for model in client.models.list().data:
        m_id = model.id.lower()
        if not any(skip in m_id for skip in ["whisper", "guard", "orpheus"]):
            chat_models.append(model.id)
            print(f"  • {model.id}")
except Exception as e:
    print(f"❌ Failed to list models: {e}")
    exit(1)

if not chat_models:
    print("❌ No chat models found. Please check your Groq tier.")
    exit(1)

# 3. Test text generation with the first available chat model
target_model = chat_models[0]
print(f"\n🚀 Testing chat completion using model: '{target_model}'...")

try:
    response = client.chat.completions.create(
        model=target_model,
        messages=[{"role": "user", "content": "Reply with 'API is working!'"}]
    )
    print("\n✅ Success! Response from Groq:")
    print(response.choices[0].message.content)
    print(f"\n👉 Use model='{target_model}' in your ai_service.py file.")
except Exception as e:
    print(f"❌ Chat completion test failed: {e}")