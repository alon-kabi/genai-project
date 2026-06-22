import uuid

from .main_agent import MainAgent


class ConversationManager:
    def __init__(self):
        self.main_agent = MainAgent()

    def create_session_id(self):
        return str(uuid.uuid4())

    def run_turn(self, user_input, session_id):
        """
        One turn in a conversation identified by session_id.
        Delegates to MainAgent; LangChain manages history via RunnableWithMessageHistory.
        """
        return self.main_agent.handle_turn(user_input, session_id)

    def reset(self, session_id):
        """
        Clear in-memory state for one conversation.
        """
        self.main_agent.reset(session_id)

    def dump_session(self, session_id, directory="logs/sessions", error=None):
        return str(self.main_agent.dump_session(session_id, directory, error=error))
