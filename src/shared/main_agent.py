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
        prompt = self._build_routing_prompt(conversation)
        # TODO: Send prompt to model and return info | schedule | exit
        pass

    def _build_routing_prompt(self, conversation):
        """
        Assemble messages for the routing classifier (system + conversation).
        conversation is assumed to be in AI chat format (role + content).
        """
        with open("prompts/routing_prompt.txt", "r", encoding="utf-8") as f:
            instructions = f.read()
        return [
            {"role": "system", "content": instructions},
            *conversation,
        ]