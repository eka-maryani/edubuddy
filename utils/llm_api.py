# utils/llm_api.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def call_llm_chat(messages, api_key=None, model="gemini-2.0-flash-exp", temperature=0.2, max_tokens=512):
    """
    messages: list of {"role": "...", "content": "..."}
    Wrapper for Google GenAI SDK to match the chat interface.
    """
    # Use passed api_key, otherwise fallback to env
    final_api_key = api_key or GOOGLE_API_KEY
    if not final_api_key:
        raise ValueError("Google API Key is missing. Please set it in sidebar or .env")

    client = genai.Client(api_key=final_api_key)

    # Gemini History Construction
    
    gemini_history = []
    system_instruction = None

    for msg in messages:
        content = msg.get("content", "")
        if not content or not isinstance(content, str) or not content.strip():
            continue  # Skip empty or invalid messages to prevent 400 errors

        if msg["role"] == "system":
            system_instruction = content
        elif msg["role"] == "user":
            gemini_history.append(types.Content(role="user", parts=[types.Part(text=content)]))
        elif msg["role"] == "assistant":
            gemini_history.append(types.Content(role="model", parts=[types.Part(text=content)]))
    

    
    if not gemini_history:
        return "I received an empty request. Please type a message or select a suggestion."

    # Generate content (stateless call for this wrapper, but passing full history)
    # Generate content configuration
    
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        system_instruction=system_instruction
    )
    
    response = client.models.generate_content(
        model=model,
        contents=gemini_history,
        config=config
    )
    
    return response.text
