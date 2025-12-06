# utils/memory.py
import json
import uuid
from datetime import datetime
from pathlib import Path

MEM_FILE = Path("data/memory.json")

def _load_raw_data():
    if MEM_FILE.exists():
        try:
            return json.loads(MEM_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def _save_raw_data(data):
    MEM_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEM_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_all_sessions():
    """Returns list of sessions sorted by last_updated (desc)"""
    data = _load_raw_data()
    sessions = data.get("sessions", {})
    # Sort by timestamp desc
    sorted_sessions = sorted(
        sessions.values(), 
        key=lambda x: x.get("last_updated", ""), 
        reverse=True
    )
    return sorted_sessions

def get_session(session_id):
    data = _load_raw_data()
    return data.get("sessions", {}).get(session_id, None)

def create_session():
    session_id = str(uuid.uuid4())
    new_session = {
        "id": session_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "messages": []
    }
    data = _load_raw_data()
    if "sessions" not in data:
        data["sessions"] = {}
    data["sessions"][session_id] = new_session
    _save_raw_data(data)
    return session_id

def update_session(session_id, messages, title=None):
    data = _load_raw_data()
    if "sessions" not in data:
        data["sessions"] = {}
    
    if session_id not in data["sessions"]:
        # fallback create
        data["sessions"][session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }

    data["sessions"][session_id]["messages"] = messages
    data["sessions"][session_id]["last_updated"] = datetime.now().isoformat()
    
    # Auto-update title from first message if not set or "New Chat"
    if title:
        data["sessions"][session_id]["title"] = title
    elif len(messages) > 0 and (data["sessions"][session_id]["title"] == "New Chat"):
        # Find first user message for title
        for m in messages:
            if m["role"] == "user":
                data["sessions"][session_id]["title"] = m["content"][:30] + "..."
                break
                
    _save_raw_data(data)

def delete_session(session_id):
    data = _load_raw_data()
    if "sessions" in data and session_id in data["sessions"]:
        del data["sessions"][session_id]
        _save_raw_data(data)


SETTINGS_FILE = Path("data/settings.json")

def load_user_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def save_user_settings(api_key, model, rag_enabled):
    data = {
        "user_api_key": api_key,
        "selected_model": model,
        "rag_enabled": rag_enabled
    }
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
