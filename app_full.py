# app_full.py - EduBuddy AI (Native Streamlit Version)
import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Local Imports
from utils.llm_api import call_llm_chat
from utils.memory import (
    get_all_sessions, 
    create_session, 
    update_session, 
    get_session, 
    delete_session,
    load_user_settings,
    save_user_settings
)
from utils.styles import get_main_css

# RAG Imports
try:
    from utils.rag import process_and_add_document, query_rag, clear_vector_store
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Load environment variables
load_dotenv()

# Constants
AVAILABLE_MODELS = [
    "gemini-2.0-flash-exp",
    "gemini-2.0-pro-exp",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-flash-latest",
]

def init_session_state():
    """Initialize Streamlit session state variables."""
    # Load persistent settings first
    saved_settings = load_user_settings()
    
    if "active_session_id" not in st.session_state:
        sessions = get_all_sessions()
        st.session_state.active_session_id = sessions[0]["id"] if sessions else create_session()

    if "user_api_key" not in st.session_state:
        # Priority: Saved Setting > Env Var
        st.session_state.user_api_key = saved_settings.get("user_api_key", os.getenv("GOOGLE_API_KEY", ""))

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = saved_settings.get("selected_model", "gemini-2.0-flash-exp")

    if "rag_enabled" not in st.session_state:
        st.session_state.rag_enabled = saved_settings.get("rag_enabled", False)

@st.dialog("Settings")
def show_settings_dialog():
    api_key_input = st.text_input("Google API Key", value=st.session_state.user_api_key, type="password")
    
    # Safe index search
    current_idx = 0
    if st.session_state.selected_model in AVAILABLE_MODELS:
        current_idx = AVAILABLE_MODELS.index(st.session_state.selected_model)
        
    model_input = st.selectbox(
        "Model", 
        AVAILABLE_MODELS, 
        index=current_idx
    )
    rag_input = st.toggle("Use RAG Context", value=st.session_state.rag_enabled)
    
    if st.button("Save & Close", type="primary"):
        st.session_state.user_api_key = api_key_input
        st.session_state.selected_model = model_input
        st.session_state.rag_enabled = rag_input
        save_user_settings(api_key_input, model_input, rag_input)
        st.rerun()

@st.dialog("Delete Chat?")
def confirm_delete_session(session_id):
    st.write("Are you sure you want to delete this chat?")
    # Centered buttons with spacing
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1: pass
    with col4: pass
    
    if col2.button("Cancel", use_container_width=True):
        st.rerun()
    if col3.button("Delete", type="primary", use_container_width=True):
        delete_session(session_id)
        # If deleted active session, reset
        if st.session_state.active_session_id == session_id:
            st.session_state.active_session_id = get_all_sessions()[0]["id"] if get_all_sessions() else create_session()
        st.rerun()

def render_sidebar():
    """Render the sidebar using native Streamlit components."""
    with st.sidebar:
        # Custom Header to ensure Logo and Text are side-by-side
        st.markdown("""
            <div style="display: flex; flex-direction: row; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 2.5rem;">🎓</span>
                <h1 style="margin: 0; padding: 0; font-size: 2.2rem; display: inline-block;">EduBuddy</h1>
            </div>
            """, unsafe_allow_html=True)
        st.caption("AI Data Science Tutor")
        
        if st.button(":material/add: New Chat", type="primary", use_container_width=True):
            st.session_state.active_session_id = create_session()
            st.rerun()
        
        # Recent Chats Container (Fixed Height)
        # We need to explicitly allow the active session to be visible even if empty
        with st.container(height=300):
            st.caption("Recent Chats")
            sessions = get_all_sessions()[:15]
            
            # Filter: Only show sessions that actually have messages (history)
            visible_sessions = [
                s for s in sessions 
                if len(s["messages"]) > 0
            ]
            
            for session in visible_sessions:
                title = session.get("title", "New Chat")
                
                # Layout: Title (85%) | Delete (15%)
                c1, c2 = st.columns([0.85, 0.15])
                
                with c1:
                    # Active session styling
                    kind = "primary" if session["id"] == st.session_state.active_session_id else "tertiary"
                    if st.button(title, key=f"sel_{session['id']}", type=kind, use_container_width=True):
                        st.session_state.active_session_id = session["id"]
                        st.rerun()
                
                with c2:
                    # Simple Trash Icon which triggers the dialog
                    # We use a unique key but minimal width
                    if st.button(":material/delete:", key=f"del_{session['id']}", type="tertiary"):
                        confirm_delete_session(session["id"])
                        
        st.divider()
        
        # Knowledge Base "Card"
        if RAG_AVAILABLE:
            with st.container(border=True): # Card-like container
                st.subheader("📚 Knowledge Base")
                uploaded_file = st.file_uploader("Upload Data (PDF, TXT, CSV, Excel)", type=['pdf', 'txt', 'csv', 'xlsx'], label_visibility="collapsed")
                
                col1, col2 = st.columns(2)
                with col1:
                    if uploaded_file and st.button("Process", use_container_width=True):
                        if not st.session_state.user_api_key:
                            st.warning("Needs API Key")
                        else:
                            with st.spinner("Indexing..."):
                                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                    tmp_file.write(uploaded_file.getvalue())
                                    tmp_path = tmp_file.name
                                try:
                                    num_chunks = process_and_add_document(tmp_path)
                                    st.success(f"Added {num_chunks} chunks")
                                    st.session_state.rag_enabled = True
                                except Exception as e:
                                    st.error(str(e))
                                finally:
                                    os.remove(tmp_path)
                with col2:
                    if st.button("Clear DB", use_container_width=True):
                        clear_vector_store()
                        st.session_state.rag_enabled = False
                        st.info("Cleared")

        # Settings Button with tertiary style (looks like link)
        if st.button(":material/settings: Settings", use_container_width=True, type="tertiary"):
            show_settings_dialog()
# -----------------------------------------------------------------------------
# MAIN APPLICATION
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="EduBuddy", page_icon="🎓", layout="centered")
    st.markdown(get_main_css(), unsafe_allow_html=True)
    
    # Init
    init_session_state()
    render_sidebar()
    
    # Active Session logic...
    session_data = get_session(st.session_state.active_session_id)
    if not session_data:
        st.session_state.active_session_id = create_session()
        session_data = get_session(st.session_state.active_session_id)
    
    messages = session_data.get("messages", [])
    
    selection = None
    
    # HERO SECTION: Centered & Elegant
    if not messages:
        # Dynamic Greeting
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Good Morning"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True) # Spacer
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 0;'>{greeting}, Learner.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>How can I assist your data science journey today?</p>", unsafe_allow_html=True)
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True) # Spacer
        
        # Interactive suggestions (Only show when chat is empty)
        # Embed icons directly in strings since 'icons' arg is not supported by st.pills
        suggestions = [
            ":material/analytics: Analyze Data", 
            ":material/code: Python Help", 
            ":material/short_text: Summarize", 
            ":material/bug_report: Debug Code"
        ]
        
        if hasattr(st, "pills"):
            # Centering st.pills via CSS + Balanced Columns
            # We use a 1:10:1 ratio to keep it centered but wide enough for 1 line
            _, c_pills, _ = st.columns([1, 10, 1])
            with c_pills:
                selection = st.pills("Suggestions", suggestions, selection_mode="single", label_visibility="collapsed")
        else:
            # Fallback
            cols = st.columns(len(suggestions))
            for i, sugg in enumerate(suggestions):
                if cols[i].button(sugg, use_container_width=True):
                    selection = sugg

    else:
        st.title("EduBuddy") # Smaller title when chat is active

    # Map selection to prompt text
    prompt_map = {
        ":material/analytics: Analyze Data": "Help me analyze a dataset.",
        ":material/code: Python Help": "Explain this Python code snippet.",
        ":material/short_text: Summarize": "Summarize the key points.",
        ":material/bug_report: Debug Code": "Help me find bugs in my code."
    }

    # Chat Area
    for msg in messages:
        if msg["role"] == "system": continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # SECTION: Conditional Upload Dialog (Triggered by Chips)
    @st.dialog("Upload Context Data")
    def show_upload_dialog():
        st.caption("To perform this action, please attach a relevant file.")
        chat_file = st.file_uploader("Upload PDF, TXT, CSV, or Excel", type=['pdf', 'txt', 'csv', 'xlsx'], key="modal_attach")
        
        if chat_file:
            if st.button("Process & Attach", key="btn_attach_modal", use_container_width=True):
                with st.spinner("Processing..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{chat_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(chat_file.getvalue())
                        tmp_path = tmp_file.name
                    try:
                        if RAG_AVAILABLE:
                            num = process_and_add_document(tmp_path)
                            st.session_state.rag_enabled = True
                            st.toast(f"Attached {chat_file.name} successfully!", icon="✅")
                            st.rerun()
                        else:
                            st.error("RAG modules not available.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

    # Input
    user_input = st.chat_input("Message EduBuddy...")
    
    # Handle suggestion click overriding
    if selection and selection in prompt_map:
        # Context Check
        if not st.session_state.rag_enabled:
            # Trigger the Modal Dialog
            show_upload_dialog()
            user_input = None
        else:
            # RAG is enabled, notify user we are using it
            st.toast("Using existing Knowledge Base context.", icon="📚")
            user_input = prompt_map[selection]
        
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        messages.append({"role": "user", "content": user_input})
        update_session(st.session_state.active_session_id, messages)
        
        # Generate Response
        if not st.session_state.user_api_key:
            with st.chat_message("assistant"):
                st.warning("Please enter your Google API Key in the sidebar.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # RAG Logic
                        context_text = ""
                        if st.session_state.rag_enabled and RAG_AVAILABLE:
                            results = query_rag(user_input)
                            if results:
                                context_text = "\n\n**Context:**\n"
                                for doc, score in results:
                                    context_text += f"> {doc.page_content[:200]}...\n\n"
                        
                        system_prompt = "You are EduBuddy, a helpful AI tutor."
                        if context_text:
                            system_prompt += f"\n\nReference:\n{context_text}"
                            
                        payload = [{"role": "system", "content": system_prompt}] + [m for m in messages if m["role"] != "system"]
                        
                        response = call_llm_chat(
                            payload,
                            api_key=st.session_state.user_api_key,
                            model=st.session_state.selected_model
                        )
                        st.markdown(response)
                        messages.append({"role": "assistant", "content": response})
                        update_session(st.session_state.active_session_id, messages)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                        


if __name__ == "__main__":
    main()
