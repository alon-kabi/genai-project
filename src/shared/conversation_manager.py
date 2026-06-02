from .main_agent import MainAgent

class ConversationManager:
    def __init__(self):
        self.main_agent = MainAgent()
        self.history = []

    def run_turn(self, user_input):
        """
        One turn in the conversation.
        Stores normalized conversation events in a single history list.
        """
        self.history.append({
            "role": "user",
            "event": "message",
            "content": user_input
        })

        response = self.main_agent.process_input(user_input, self.history)

        advisor_message = response["message"]
        self.history.append({
            "role": "assistant",
            "event": "message",
            "content": advisor_message
        })

        return response

    def reset(self):
        """
        Clear in-memory state and prepare for a new conversation.
        """
        self.history = []