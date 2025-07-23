import os
import time
import google.generativeai as genai
import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key

# Load environment variables
load_dotenv()

# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# DynamoDB table setup
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
table = dynamodb.Table("segunai")

# FastAPI app setup
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ UTILS ============

def get_chat_history(chat_id):
    response = table.query(
        KeyConditionExpression=Key('chat_id').eq(str(chat_id)),
        ScanIndexForward=True  # Ascending order (older to newer)
    )
    return sorted(response.get("Items", []), key=lambda x: x['timestamp'])

def build_prompt(mode, user_text, history):
    instructions = {
        "Simplifier": "Simplify this for a beginner. Use simple language and avoid technical terms unless necessary.",
        "Summarizer": "Summarize this content clearly. Include the main points only.",
        "Step-by-Step": "Explain this step by step like I'm new. Use everyday examples.",
        "Glossary": "Break down the key terms. Format: Term > Definition > Example. Keep it conversational.",
        "Tutor Mode": "Act as my tutor. Explain the topic, then ask a follow-up question.",
        "Quiz Generator": (
            "Create a quiz with different question types. Each question must be numbered and clearly formatted.\n"
            "Use plain text. Example:\n"
            "1. What is AI?\nA) Answer1\nB) Answer2\n\n2. Explain AI in 1 line.\n[Short answer]"
        )
    }

    system_instruction = instructions.get(mode, "")
    
    conversation = ""
    for msg in history:
        role = "User" if msg["sender"] == "user" else "Assistant"
        conversation += f"{role}: {msg['text']}\n"

    # Append the new message from user at the end
    conversation += f"User: {user_text}\n"

    prompt = f"""{conversation}
Instruction: {system_instruction}
Respond in plain text, no markdown or formatting."""
    return prompt

def generate_gemini_response(mode, text, chat_id):
    try:
        history = get_chat_history(chat_id)
        prompt = build_prompt(mode, text, history)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error getting AI response: {str(e)}"

# ============ ROUTES ============

@app.post("/chat")
async def chat(data: dict):
    mode = data.get("mode")
    text = data.get("text")
    chat_id = data.get("chat_id") or str(int(time.time()))
    timestamp = int(time.time())

    # Save user message
    table.put_item(Item={
        'chat_id': str(chat_id),
        'timestamp': timestamp,
        'sender': 'user',
        'text': text,
        'mode': mode
    })

    # Generate bot reply
    reply = generate_gemini_response(mode, text, chat_id)

    # Save bot reply
    table.put_item(Item={
        'chat_id': str(chat_id),
        'timestamp': timestamp + 1,
        'sender': 'bot',
        'text': reply,
        'mode': mode
    })

    return {
        "reply": reply,
        "chat_id": chat_id
    }

@app.get("/history")
async def get_history():
    response = table.scan()
    items = response.get("Items", [])

    # Group by chat_id and get only first message of each (latest chats first)
    unique_chats = {}
    for item in sorted(items, key=lambda x: x.get('timestamp', 0), reverse=True):
        cid = item.get("chat_id")
        if cid not in unique_chats and item.get("sender") == "user":
            unique_chats[cid] = item

    return {"history": list(unique_chats.values())}

# ✅ NEW ENDPOINT: Get full chat by ID
@app.get("/history/{chat_id}")
async def get_chat_by_id(chat_id: str):
    try:
        messages = get_chat_history(chat_id)
        return {"messages": messages}
    except Exception as e:
        return {"error": str(e)}
