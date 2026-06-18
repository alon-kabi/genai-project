from datetime import datetime, timedelta

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool


@tool
def get_next_three_dates(start_date):
    """Receive a date and return 3 optional dates. start_date format: YYYY-MM-DD."""
    date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    return [
        (date_obj + timedelta(days=3)).strftime("%Y-%m-%d"),
        (date_obj + timedelta(days=6)).strftime("%Y-%m-%d"),
        (date_obj + timedelta(days=9)).strftime("%Y-%m-%d"),
    ]


class ScheduleAdvisor:
    def __init__(self, llm):
        self.llm = llm
        self.tools = [get_next_three_dates]
        self.executor = self.build_executor()

    def load_system_prompt(self):
        with open("prompts/schedule_prompt.txt") as f:
            return f.read()

    def build_executor(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_system_prompt()),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", "{input}"),
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)

    def _parse_output(self, output):
        if output.strip() == "FALSE_HANDOVER":
            return {"status": "false_handover"}
        return {"status": "answered", "message": output}

    def invoke(self, conversation):
        output = self.executor.invoke({"input": conversation})["output"]
        return self._parse_output(output)
