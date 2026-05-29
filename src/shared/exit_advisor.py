class ExitAdvisor:
    def process(self, chat_history):
        """
        Processes the complete chat history.
        Decides whether to end the conversation.
        """

        should_exit = self.should_end_conversation(chat_history)

        if should_exit:
            return {
                "end_conversation": True,
                "message": "Conversation ended."
            }

        return {
            "end_conversation": False,
            "message": "Continue conversation."
        }

    def should_end_conversation(self, chat_history):
        """
        Decide whether the conversation should end.
        """
        # TODO: Implement exit logic
        pass