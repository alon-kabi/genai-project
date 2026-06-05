class ScheduleAdvisor:
    def process(self, conversation=None):
        """
        Processes the complete conversation.
        Decides whether scheduling is needed.

        Example conversation expected here:
        [
            {"role": "user", "content": "I am interested in the Python role."},
            {"role": "assistant", "content": "Great. Would you like to schedule an interview?"},
            {"role": "user", "content": "Yes, next Friday morning works for me."}
        ]

        Example response (still scheduling — message to user):
        {
            "done": False,
            "message": "Great — here are 3 available slots: Fri 10:00, Fri 11:30, Mon 09:00."
        }

        Example response (scheduling finished):
        {
            "done": True,
            "message": "All done — your interview is confirmed for Fri 10:00."
        }
        """

        if self.should_schedule():
            options = self.retrieve_schedule_options()
            return self.send_output(options)

        return self.send_output("Scheduling not required")

    def should_schedule(self):
        """
        Decide whether scheduling flow is needed.
        """
        # TODO: Replace with LLM + conversation context
        return False

    def retrieve_schedule_options(self):
        """
        Retrieve scheduling options from SQL/database.
        """
        # TODO: Implement SQL retrieval (db_Tech.sql)
        return ["Slot placeholder 1", "Slot placeholder 2", "Slot placeholder 3"]

    def send_output(self, result):
        """
        Sends output back to MainAgent.
        """
        return result