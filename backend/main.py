import os
import time
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# Configure Gemini
genai.configure(api_key=os.getenv("AIzaSyA3hw7lDH0TPzXEMnA4D3mhPA7JYhLSLd4"))

app = FastAPI()

# Allow local frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_gemini_response(mode, text):
    prompt = ""

    if mode == "Simplifier":
        prompt = f"""
        Simplify this study material so a beginner can understand it.

        {text}

        Use simple language and avoid technical terms unless necessary.
        Return your response in plain text only — no markdown or formatting.
        """

    elif mode == "Summarizer":
        prompt = f"""
        Summarize this content clearly and concisely.

        {text}

        Make sure to include the main points and nothing extra.
        Return your response in plain text only — no markdown or formatting.
        """

    elif mode == "Step-by-Step":
        prompt = f"""
        Explain the following topic in simple, step-by-step terms:

        {text}

        Start from the basics and build up. Use everyday analogies where possible.
        Make sure each step is easy to follow and connects logically to the next.
        Return your response in plain text only — no markdown or formatting.
        """

    elif mode == "Glossary":
        prompt = f"""
        Break down the topic '{text}' into key subtopics as if you're explaining to a student.
        For each term:

        Term: [name]
        Definition: [simple explanation]
        Example: [real-life or analogy]

        Keep it conversational and avoid markdown.
        Return in plain text paragraphs only.
        """

    elif mode == "Tutor Mode":
        prompt = f"""
        Act like my private tutor.

        Teach me the topic below starting from the very beginning:
        "{text}"

        First, explain the basic idea in simple words.
        Then ask me a question to check my understanding.
        Based on my answer, decide whether to move forward or review.
       
        Speak in a friendly and encouraging tone.
        Don't give me the full answer right away — guide me to understand it myself.
       
        If I ask to solve something, show your thinking process step-by-step.
        At the end, ask a quick follow-up question to make sure I understood.

        Return your response in plain text only — no markdown or formatting.
        """

    elif mode == "Quiz Generator":
        prompt = f"""
    Generate a quiz based on the following content:

    {text}

    Follow these rules:
    - Write only plain text — no markdown or special symbols like #, -, or *
    - Each question should be clearly numbered and on its own line
    - Each answer option must appear on a new line directly below the question
    - Leave one blank line between questions for readability
    - Use normal punctuation and capitalization
    - Include different types of questions (e.g., multiple choice, true/false, short answer)
   
    Example format:
    1. What is the capital of France?
    A) Paris
    B) Berlin
    C) Madrid
    D) Rome

    2. Name one use of photosynthesis.
    [Short answer expected]

    Now generate your quiz:
    """

    # Send prompt to Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

@app.post("/chat")
async def chat(data: dict):
    mode = data.get("mode")
    text = data.get("text")
    chat_id = data.get("chat_id") or int(time.time())

    reply = generate_gemini_response(mode, text)
    return {"reply": reply, "chat_id": chat_id} 