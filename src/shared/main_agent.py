from dotenv import load_dotenv
import uuid
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from .info_advisor import InfoAdvisor
from .schedule_advisor import ScheduleAdvisor
from .session_logger import SessionLogger

load_dotenv("../../.env")


class MainAgent:
    def __init__(self):
        self.store = {}
        self.session_id = str(uuid.uuid4())
        self.session_logger = SessionLogger(self.session_id)
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.info_advisor = InfoAdvisor(self.llm)
        self.schedule_advisor = ScheduleAdvisor(self.llm)
        self.main_agent_with_memory = self.build_main_agent_with_memory()

    def get_history(self, session_id):
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def load_system_prompt(self):
        with open("prompts/main_prompt.txt") as f:
            return f.read()

    def build_main_agent_with_memory(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_system_prompt()),
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", "{input}"),
        ])
        agent = create_openai_tools_agent(self.llm, tools=[], prompt=prompt)
        executor = AgentExecutor(agent=agent, tools=[], verbose=False)
        return RunnableWithMessageHistory(
            executor,
            get_session_history=self.get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def load_clarification_prompt(self):
        with open("prompts/clarification_prompt.txt") as f:
            return f.read()

    def _replace_last_assistant_message(self, content):
        history = self.get_history(self.session_id)
        if history.messages and history.messages[-1].type == "ai":
            history.messages[-1] = AIMessage(content=content)

    def _format_messages(self, messages):
        return [{"role": message.type, "content": message.content} for message in messages]

    def _ask_for_clarification(self, conversation):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_clarification_prompt()),
            ("user", "{conversation}"),
        ])
        return (prompt | self.llm).invoke({
            "conversation": conversation,
        }).content.strip()

    def _handle_advisor_result(self, result, conversation):
        if result["status"] == "false_handover":
            message = self._ask_for_clarification(conversation)
        else:
            message = result["message"]

        self._replace_last_assistant_message(message)
        return message

    def handle_turn(self, user_input):
        """
        One turn of orchestration:
        main agent with memory, then advisor if scheduling or info is detected.
        """
        history = self.get_history(self.session_id)
        conversation_before = self._format_messages(history.messages)

        main_output = self.main_agent_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": self.session_id}},
        )["output"]

        message = main_output
        advisor = None
        advisor_status = None

        if (
            "I will check available slots for you." in main_output
            or "Let me find that information for you." in main_output
        ):
            full_history = self.get_history(self.session_id).messages
            conversation = "\n".join([f"{m.type.capitalize()}: {m.content}" for m in full_history])
            if "I will check available slots for you" in main_output:
                advisor = "schedule"
                result = self.schedule_advisor.invoke(conversation)
            else:
                advisor = "info"
                result = self.info_advisor.invoke(conversation)
            advisor_status = result["status"]
            message = self._handle_advisor_result(result, conversation)

        self.session_logger.record_turn({
            "turn": len(self.session_logger.turns) + 1,
            "user_input": user_input,
            "conversation_before": conversation_before,
            "main_output": main_output,
            "advisor": advisor,
            "advisor_status": advisor_status,
            "user_message": message,
            "conversation": self._format_messages(self.get_history(self.session_id).messages),
        })

        return {
            "message": message,
            "end_conversation": False,
        }

    def dump_session(self, directory="logs/sessions"):
        return self.session_logger.dump(directory)

    def reset(self):
        self.store.pop(self.session_id, None)
        self.session_id = str(uuid.uuid4())
        self.session_logger = SessionLogger(self.session_id)
