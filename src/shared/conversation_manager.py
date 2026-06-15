from .main_agent import MainAgent


class ConversationManager:
    def __init__(self):
        self.main_agent = MainAgent()

    def run_turn(self, user_input):
        """
        One turn in the conversation.
        Delegates to MainAgent; LangChain manages history via RunnableWithMessageHistory.
        """
        return self.main_agent.handle_turn(user_input)

    def reset(self):
        """
        Clear in-memory state and prepare for a new conversation.
        """
        self.main_agent.reset()
