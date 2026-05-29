class ConversationManager:
    def __init__(self):
        self.chat_history = []
        self.main_agent = MainAgent()

    def fill_registration_form(self):
        """
        Initial registration flow.
        """
        # TODO: Implement registration form
        pass

    def run_turn(self, user_input):
        """
        One turn in the conversation.
        """

        self.chat_history.append({
            "role": "user",
            "content": user_input
        })

        response = self.main_agent.process_input(
            user_input,
            self.chat_history
        )

        self.chat_history.append({
            "role": "assistant",
            "content": response
        })

        return response