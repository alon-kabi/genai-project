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

import streamlit as st

st.set_page_config(page_title="Recruiting Chatbot PoC", layout="wide")
st.title("Python Developer Recruiting Chat PoC")

if "sessions" not in st.session_state:
    st.session_state.sessions = {}


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
    st.session_state.sessions[name] = []


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
            for message in st.session_state.sessions[label]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            st.chat_input("Message", key=f"chat_{label}", disabled=True)
