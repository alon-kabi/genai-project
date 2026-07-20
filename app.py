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
    }

conversation = st.session_state.conversation

if not conversation["messages"]:
    st.info("To begin a conversation, type your message below.")

for message in conversation["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message"):
    conversation["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.spinner("Thinking..."):
            response = st.session_state.manager.run_turn(prompt, conversation["session_id"])
        assistant_message = response["message"]
        conversation["messages"].append({"role": "assistant", "content": assistant_message})
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
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
