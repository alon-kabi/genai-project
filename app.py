import os
import sys
import traceback
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SHARED = SRC / "shared"

sys.path.insert(0, str(SRC))
os.chdir(SHARED)
load_dotenv(ROOT / ".env")

from shared import ConversationManager


def init_session_state():
    if "manager" not in st.session_state:
        st.session_state.manager = ConversationManager()
    if "messages" not in st.session_state:
        st.session_state.messages = []


def dump_session_error(exc):
    return st.session_state.manager.dump_session(error={
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    })


st.set_page_config(page_title="Recruiting Chatbot", page_icon="💬")
st.title("Python Developer Recruiting Chat")
st.caption("Streamlit PoC — replaces SMS for demo and Community Cloud deployment.")

init_session_state()

with st.sidebar:
    st.header("Session")
    if st.button("New conversation"):
        st.session_state.manager.reset()
        st.session_state.messages = []
        st.rerun()
    if st.button("Dump session"):
        dump_path = st.session_state.manager.dump_session()
        st.success(f"Session dump written to:\n{dump_path}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = st.session_state.manager.run_turn(prompt)
        assistant_message = response.get("message", str(response))
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})

        if response.get("end_conversation") is True:
            st.session_state.manager.reset()
            st.session_state.messages = []
            st.info("Conversation ended. Starting a new conversation.")
        st.rerun()
    except Exception as exc:
        dump_path = dump_session_error(exc)
        st.error(str(exc))
        with st.expander("Traceback"):
            st.code(traceback.format_exc())
        st.warning(f"Session dump written to: {dump_path}")
