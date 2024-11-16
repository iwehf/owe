from .remote_llm import RemoteLLM
from .remote_sd_tool import RemoteSDTool
from .agent_config import AgentConfig
from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

class OweAgent:

    system_prompt="""

    The process to generate answer to the user input requires multiple steps that are represented by a markdown code snippet of a json blob.
    The json structure should contain the following keys:
    thought -> your thoughts
    action -> name of a tool
    action_input -> parameters to send to the tool

    These are the tools you can use: {tool_names}.

    These are the tools descriptions:

    {tools}

    If no tools are required to answer the question, use the tool "Final Answer" to give the text answer directly. Its parameters is the solution.
    If there is not enough information, try to give the final answer at your best knowledge.
    """

    human_prompt="""
    Add the word "STOP" after each markdown snippet. Example:

    ```json
    {{"thought": "<your thoughts>",
    "action": "<tool name or Final Answer to give a final answer>",
    "action_input": "<tool parameters or the final output"}}
    ```
    STOP

    This is my query="{input}". Write only the next step needed to solve it.
    Your answer should be based in the previous tools executions, even if you think you know the answer.
    Remember to add STOP after each snippet.

    These were the previous steps given to solve this query and the information you already gathered:
    """

    def __init__(self, config: AgentConfig) -> None:

        llm = RemoteLLM(config.llm_config)
        sd_tool = RemoteSDTool(config.image_generation_args)
        tools = [sd_tool]

        self.config = config

        prompt_template = self._build_prompt_template(config.llm_config.prompt_preset)

        agent = create_json_chat_agent(
            tools=tools,
            llm = llm,
            prompt = prompt_template,
            stop_sequence=["STOP"],
            template_tool_response="{observation}"
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_execution_time=300,
            max_iterations=5
        )

        memory = ChatMessageHistory(session_id="test-session")

        self.executor = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: memory,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def _build_prompt_template(self, agent_preset_prompt: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                ("system", agent_preset_prompt + self.system_prompt),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", self.human_prompt),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

    async def get_response(self, input: str, user_id: str) -> dict:
        resp = await self.executor.ainvoke({"input": input}, config={"configurable": {"session_id": user_id}})
        output = resp["output"]
        resp_dict = {
            "text": None,
            "image": None
        }

        if output.startswith("[image]"):
            resp_dict["image"] = output[7:]
        else:
            resp_dict["text"] = output

        return resp_dict
