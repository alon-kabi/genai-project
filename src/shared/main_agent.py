import os

from dotenv import load_dotenv
from openai import OpenAI

from .info_advisor import InfoAdvisor
from .schedule_advisor import ScheduleAdvisor
from .exit_advisor import ExitAdvisor

load_dotenv("../../.env")

class MainAgent:
    def process_input(self, user_input, conversation=None):
        """
        Receives and processes user input.
        Decides which advisor to route to.
        """
        exit_declined = False
        while True:
            decision = self.decide_route(user_input, conversation, exit_declined=exit_declined)
            exit_declined = False

            if decision == "exit":
                advisor = ExitAdvisor()
                advisor_output = advisor.process(conversation)
                response = {
                    "decision": decision,
                    "advisor_output": advisor_output,
                    "end_conversation": bool(advisor_output.get("end_conversation", False)),
                    "message": advisor_output.get("message", "Conversation ended.")
                }
                if response["end_conversation"]:
                    return response
                exit_declined = True
                continue

            elif decision == "info":
                advisor = InfoAdvisor()
                advisor_output = advisor.process()
                continue

            elif decision == "schedule":
                advisor = ScheduleAdvisor()
                advisor_output = advisor.process()
                continue

    def decide_route(self, user_input, conversation=None, exit_declined=False):
        """
        Decide between:
        - info
        - schedule
        - exit
        """
        api_key = os.getenv("OPENAI_API_KEY")
        prompt = self._build_routing_prompt(conversation, exit_declined=exit_declined)

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=0,
        )
        return response.choices[0].message.content.strip().lower()

    def _build_routing_prompt(self, conversation, exit_declined=False):
        """
        Assemble messages for the routing classifier (system + conversation).
        conversation is assumed to be in AI chat format (role + content).
        """
        with open("prompts/routing_prompt.txt", "r", encoding="utf-8") as f:
            instructions = f.read()
        if exit_declined:
            instructions += (
                "\n\n# Context\n\n"
                "The exit advisor reviewed this conversation and determined it is NOT time to end. "
                "Do not classify as exit. Choose info or schedule."
            )
        return [
            {"role": "system", "content": instructions},
            *conversation,
        ]
