from .info_advisor import InfoAdvisor
from .schedule_advisor import ScheduleAdvisor
from .exit_advisor import ExitAdvisor

class MainAgent:
    def process_input(self, user_input, conversation=None):
        """
        Receives and processes user input.
        Decides which advisor to route to.
        """
        while True:
            decision = self.decide_route(user_input, conversation)

            if decision == "exit":
                advisor = ExitAdvisor()
                advisor_output = advisor.process()
                response = {
                    "decision": decision,
                    "advisor_output": advisor_output,
                    "end_conversation": bool(advisor_output.get("end_conversation", False)),
                    "message": advisor_output.get("message", "Conversation ended.")
                }
                if response["end_conversation"]:
                    return response

            elif decision == "info":
                advisor = InfoAdvisor()
                advisor_output = advisor.process()
                continue

            elif decision == "schedule":
                advisor = ScheduleAdvisor()
                advisor_output = advisor.process()
                continue

    def decide_route(self, user_input, conversation=None):
        """
        Decide between:
        - info
        - schedule
        - exit
        """
        conversation = conversation or []
        # TODO: Classify conversation (AI prompt messages) -> info | schedule | exit
        pass
