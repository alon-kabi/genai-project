from .info_advisor import InfoAdvisor
from .schedule_advisor import ScheduleAdvisor
from .exit_advisor import ExitAdvisor

class MainAgent:
    def process_input(self,user_input):
        """
        Receives and processes user input.
        Decides which advisor to route to.
        """

        # TODO: Decision logic
        decision = self.decide_route()

        if decision == "info":
            advisor = InfoAdvisor()
            return advisor.process()

        elif decision == "schedule":
            advisor = ScheduleAdvisor()
            return advisor.process()

        elif decision == "exit":
            advisor = ExitAdvisor()
            return advisor.process()

        else:
            raise ValueError("Unknown routing decision")

    def decide_route():
        """
        Decide between:
        - info
        - schedule
        - exit
        """
        # TODO: Implement routing logic
        pass