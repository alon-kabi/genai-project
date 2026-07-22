from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from .rag.chroma_client import VolatileChromaClient


class InfoAdvisor:
    def __init__(self, llm, chroma_client=None):
        self.chroma_client = chroma_client or VolatileChromaClient()
        self.llm = llm
        client = self.chroma_client

        @tool
        def get_job_info(query):
            """
            job description information relevant to the candidate's question.
            
            this tool at most once per user question.
            
            returned information is sufficient to answer the question.
            receiving the result, do not call this tool again.
            """
            return client.search(query)

        self.tools = [get_job_info]
        self.executor = self.build_executor()

    def load_system_prompt(self):
        with open("prompts/info_prompt.txt", encoding="utf-8") as f:
            return f.read()

    def build_executor(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.load_system_prompt()),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools)

    def _parse_output(self, output):
        if output.strip() == "FALSE_HANDOVER":
            return {"status": "false_handover"}
        return {"status": "answered", "message": output}

    def invoke(self, conversation):
        output = self.executor.invoke({"input": conversation})["output"]
        return self._parse_output(output)
