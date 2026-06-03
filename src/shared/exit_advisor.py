import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("../../.env")


class ExitAdvisor:
    def process(self, conversation=None):
        """
        Processes the complete conversation.
        Decides whether to end the conversation.
        """
        should_exit, message = self.should_end_conversation(conversation)

        if should_exit:
            return {
                "end_conversation": True,
                "message": message or "Conversation ended.",
            }

        return {
            "end_conversation": False,
        }

    def should_end_conversation(self, conversation=None):
        """
        Decide whether the conversation should end.
        Returns (should_exit, closing_message or None).
        """
        api_key = os.getenv("OPENAI_API_KEY")
        prompt = self._build_exit_prompt(conversation)

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=0,
        )
        return self._parse_exit_response(response.choices[0].message.content)

    def _build_exit_prompt(self, conversation):
        """
        Assemble messages for the exit advisor (system + conversation).
        """
        with open("prompts/exit_prompt.txt", "r", encoding="utf-8") as f:
            instructions = f.read()
        return [
            {"role": "system", "content": instructions},
            *conversation,
        ]

    def _parse_exit_response(self, content):
        """
        Example (ending):
            end_conversation: yes
            message: Understood — we will not contact you again. Best of luck!

        Example (not ending):
            end_conversation: no

        Converts the model's text reply (see exit_prompt.txt) into a bool (end or not)
        and an optional closing SMS message for the app to use.
        """
        should_exit = False
        message = None
        for line in (content or "").strip().splitlines():
            lower = line.lower()
            if lower.startswith("end_conversation:"):
                value = line.split(":", 1)[1].strip().lower()
                should_exit = value in ("yes", "true")
            elif lower.startswith("message:"):
                message = line.split(":", 1)[1].strip()
        return should_exit, message
