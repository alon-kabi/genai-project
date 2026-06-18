from dotenv import load_dotenv
import uuid
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from .info_advisor import InfoAdvisor
from .schedule_advisor import ScheduleAdvisor

load_dotenv("../../.env")


class MainAgent:
    def __init__(self):
        self.store = {}
        self.session_id = str(uuid.uuid4())
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

    def handle_turn(self, user_input):
        """
        One turn of orchestration:
        main agent with memory, then advisor if scheduling or info is detected.
        """
        main_output = self.main_agent_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": self.session_id}},
        )["output"]

        message = main_output

        if (
            "I will check available slots for you." in main_output
            or "Let me find that information for you." in main_output
        ):
            full_history = self.get_history(self.session_id).messages
            # full_history before:
            # [
            #     HumanMessage(content='I am interested in the Python role.'),
            #     AIMessage(content='Great. Would you like to schedule an interview?'),
            #     HumanMessage(content='Yes, next Friday morning works for me.'),
            #     AIMessage(content='I will check available slots for you.'),
            # ]
            conversation = "\n".join([f"{m.type.capitalize()}: {m.content}" for m in full_history])
            # conversation after:
            # Human: I am interested in the Python role.
            # Ai: Great. Would you like to schedule an interview?
            # Human: Yes, next Friday morning works for me.
            # Ai: I will check available slots for you.
            if "I will check available slots for you" in main_output:
                message = self.schedule_advisor.invoke(conversation)
            else:
                message = self.info_advisor.invoke(conversation)

        return {
            "message": message,
            "end_conversation": False,
        }

    def reset(self):
        self.store.pop(self.session_id, None)
        self.session_id = str(uuid.uuid4())
