import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if os.path.abspath(os.getcwd()) != project_root:
    print(
        "Error: run this app from the project root (genai-project).\n"
        f"  cd {project_root}\n"
        "  streamlit run app.py",
        file=sys.stderr,
    )
    sys.exit(1)

from dotenv import load_dotenv
from src.shared import ConversationManager

load_dotenv(".env")

import streamlit as st

st.set_page_config(page_title="Recruiting Chatbot PoC", layout="wide")
st.title("Python Developer Recruiting Chat PoC")

if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "manager" not in st.session_state:
    st.session_state.manager = ConversationManager()


def default_user_name():
    return f"User {len(st.session_state.sessions) + 1}"


def add_user(name):
    name = name.strip() or default_user_name()
    if name in st.session_state.sessions:
        suffix = 2
        base = name
        while name in st.session_state.sessions:
            name = f"{base} ({suffix})"
            suffix += 1
    st.session_state.sessions[name] = {
        "session_id": st.session_state.manager.create_session_id(),
        "messages": [],
    }


with st.sidebar:
    with st.form("add_user"):
        user_name = st.text_input("User name", value=default_user_name())
        if st.form_submit_button("Add user"):
            add_user(user_name)
            st.rerun()

if not st.session_state.sessions:
    st.info("Add a user from the sidebar to start.")
else:
    tabs = st.tabs(list(st.session_state.sessions.keys()))
    for label, tab in zip(st.session_state.sessions, tabs):
        with tab:
            user = st.session_state.sessions[label]
            for message in user["messages"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            if prompt := st.chat_input("Message", key=f"chat_{label}"):
                user["messages"].append({"role": "user", "content": prompt})

                with st.spinner("Thinking..."):
                    response = st.session_state.manager.run_turn(prompt, user["session_id"])

                user["messages"].append({"role": "assistant", "content": response["message"]})
