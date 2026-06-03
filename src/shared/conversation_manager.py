from .main_agent import MainAgent

class ConversationManager:
    def __init__(self):
        self.main_agent = MainAgent()
        self.conversation = []

    def run_turn(self, user_input):
        """
        One turn in the conversation.
        Stores messages in AI prompt format (role + content).
        """
        self.conversation.append({
            "role": "user",
            "content": user_input
        })

        response = self.main_agent.process_input(user_input, self.conversation)

        advisor_message = response["message"]
        self.conversation.append({
            "role": "assistant",
            "content": advisor_message
        })

        return response

    def reset(self):
        """
        Clear in-memory state and prepare for a new conversation.
        """
        self.conversation = []
