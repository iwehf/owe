import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .custom_llm import CustomLLMMistral
from .stable_diffusion_tool import StableDiffusionTool
from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class OweAgent:

    model_name = "mistralai/Mistral-7B-Instruct-v0.3"

    system_prompt="""
    You are designed to solve tasks. Each task requires multiple steps that are represented by a markdown code snippet of a json blob.
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

    def __init__(self) -> None:
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            cache_dir="models/huggingface").to("cuda")

        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        llm = CustomLLMMistral(model=model, tokenizer=tokenizer)
        tools = [StableDiffusionTool()]

        prompt_template = self._build_prompt_template()

        agent = create_json_chat_agent(
            tools=tools,
            llm = llm,
            prompt = prompt_template,
            stop_sequence=["STOP"],
            template_tool_response="{observation}"
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def _build_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", self.human_prompt),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

    def get_response(self, input: str) -> dict:
        resp = self.agent_executor.invoke({"input": input})
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
