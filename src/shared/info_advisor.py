from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


class InfoAdvisor:
    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = []
        self.executor = self.build_executor()

    def load_system_prompt(self):
        with open("prompts/info_prompt.txt") as f:
            return f.read()

    def build_executor(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_system_prompt()),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("user", "{input}"),
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)

    def invoke(self, conversation):
        return self.executor.invoke({"input": conversation})["output"]
