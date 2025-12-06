import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try to grab from session state file if possible, or just print error
    print("No API Key in env")
else:
    try:
        client = genai.Client(api_key=api_key)
        print("Listing models...")
        # New SDK listing
        # It seems the SDK might have different pager. 
        # Referencing typical usage
        for m in client.models.list():
            print(f"Model: {m.name}")
            try:
                print(f"Display Name: {getattr(m, 'display_name', 'N/A')}")
                print(f"Methods: {getattr(m, 'supported_generation_methods', 'Unknown')}")
            except:
                pass
            print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")
