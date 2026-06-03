class ExitAdvisor:
    def process(self):
        """
        Processes the complete conversation.
        Decides whether to end the conversation.
        """

        should_exit = self.should_end_conversation()

        if should_exit:
            return {
                "end_conversation": True,
                "message": "Conversation ended."
            }

        return {
            "end_conversation": False,
            "message": "Continue conversation."
        }

    def should_end_conversation(self):
        """
        Decide whether the conversation should end.
        """
        # TODO: Replace with fine-tuned model
        return False