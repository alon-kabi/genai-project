import os
import sys
import traceback

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

if "manager" not in st.session_state:
    st.session_state.manager = ConversationManager()

if "conversation" not in st.session_state:
    st.session_state.conversation = {
        "session_id": st.session_state.manager.create_session_id(),
        "messages": [],
        "pending_prompt": None,
    }


def process_pending_prompt():
    conversation = st.session_state.conversation
    pending = conversation.get("pending_prompt")
    if not pending:
        return

    conversation["pending_prompt"] = None
    conversation["messages"].append({"role": "user", "content": pending})

    try:
        with st.spinner("Thinking..."):
            response = st.session_state.manager.run_turn(pending, conversation["session_id"])
        conversation["messages"].append({"role": "assistant", "content": response["message"]})
    except Exception as exc:
        st.error(str(exc))
        dump_path = st.session_state.manager.dump_session(conversation["session_id"], error={
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        })
        st.caption(f"Session dump written to: {dump_path}")
    finally:
        st.session_state.conversation = conversation


process_pending_prompt()

conversation = st.session_state.conversation
if not conversation["messages"]:
    st.info("To begin a conversation, type your message below.")

for message in conversation["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message"):
    conversation["pending_prompt"] = prompt
    st.session_state.conversation = conversation
    st.rerun()
