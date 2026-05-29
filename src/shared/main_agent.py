from .front_desk import InfoAdvisor
from .front_desk import ScheduleAdvisor
from .front_desk import ExitAdvisor

class MainAgent:
    def process_input(self, user_input, chat_history):
        """
        Receives and processes user input.
        Decides which advisor to route to.
        """

        # TODO: Decision logic
        decision = self.decide_route(user_input, chat_history)

        if decision == "info":
            advisor = InfoAdvisor()
            return advisor.process(chat_history)

        elif decision == "schedule":
            advisor = ScheduleAdvisor()
            return advisor.process(chat_history)

        elif decision == "exit":
            advisor = ExitAdvisor()
            return advisor.process(chat_history)

        else:
            raise ValueError("Unknown routing decision")

    def decide_route(self, user_input, chat_history):
        """
        Decide between:
        - info
        - schedule
        - exit
        """
        # TODO: Implement routing logic
        pass