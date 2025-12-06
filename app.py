# app.py
import streamlit as st

st.set_page_config(page_title="EduBuddy - Data Science Tutor", layout="centered")

st.title("EduBuddy — Data Science Tutor (SKELETON)")
st.write("Ini skeleton: pilih `app_full.py` untuk versi runnable dengan integrasi LLM.")

# Simple UI layout
with st.sidebar:
    st.header("Settings")
    persona = st.selectbox("Persona", ["Friendly tutor", "Concise tutor", "Exam coach"])
    clear = st.button("Clear chat")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are EduBuddy, a friendly data science tutor."}
    ]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    else:
        pass

user_input = st.chat_input("Tanya sesuatu tentang Data Science...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    # PSEUDOCODE: call LLM here
    # reply = llm_call(prompt=..., messages=st.session_state.messages)
    reply = ">> jawaban placeholder. Integrasikan LLM di utils/llm_api.py"
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.rerun()
