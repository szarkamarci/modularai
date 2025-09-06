import os
from typing import Dict, List, Optional

import mlflow
from ai_platform.agentic_workflow.agent import Agent
from ai_platform.agentic_workflow.model_config import RetrieverToolConfig
from databricks_langchain import ChatDatabricks, VectorSearchRetrieverTool
from langchain_core.messages.utils import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from mlflow.langchain.chat_agent_langgraph import ChatAgentState, ChatAgentToolNode

# If you want to you filters in the vector search, use this one:
# from ai_platform.agentic_workflow.chat_agent_tool_node_with_filters import (
#     ChatAgentToolNodeWithFilters,
# )


class ToolAgent(Agent):

    def __init__(self, agent_config: dict):

        super().__init__(agent_config)
        self._init_workflow(agent_config)


    def _init_workflow(self, agent_config: dict) -> None:

        # Store configuration
        self.agent_config = agent_config
        self.name = self.agent_config.name
        self.tool_llm_config = self.agent_config.tool_llm
        self.tool_configs = self.agent_config.tools
        self.summary_llm_config = self.agent_config.summary_llm

        # Initialize tool LLM
        self.tool_llm = ChatDatabricks(
            model=self.tool_llm_config.llm.endpoint_name,
            max_tokens=int(self.tool_llm_config.llm.max_tokens),
        )

        # Initialize tools
        self.tools = self._create_tools()

        # Initialize summary LLM
        self.summary_llm = ChatDatabricks(
            model=self.summary_llm_config.llm.endpoint_name,
            max_completion_tokens=int(self.summary_llm_config.llm.max_tokens),
        )

    
    def _create_tools(self) -> List[BaseTool]:

        tools = []

        for tool_config in self.tool_configs:
            if tool_config.type == "retriever":
                tool = self._create_retriever_tool(tool_config)
                if tool:
                    tools.append(tool)

        return tools

    def _create_retriever_tool(
        self, tool_config: "RetrieverToolConfig"
    ) -> Optional["VectorSearchRetrieverTool"]:

        try:
            # Get authentication token
            client_args = {"token": os.environ["DATABRICKS_TOKEN"]}
        except KeyError:
            client_args = None

        # Construct index name
        vs_index = tool_config.embedding.vs_index

        try:
            tool = VectorSearchRetrieverTool(
                tool_name=tool_config.name,
                index_name=vs_index,
                tool_description=tool_config.description,
                query_type=tool_config.retrieval.similarity_search_query_type,
                num_results=tool_config.retrieval.retrieved_chunks,
                columns=tool_config.embedding.columns_to_sync,
                client_args=client_args,
            )
            return tool
        except (KeyError, OSError) as e:
            print(f"Warning: Failed to create retriever tool {tool_config.name}: {e}")
            return None

    def get_workflow(self) -> CompiledGraph:
        return self.agent

    def create_agent_workflow(self) -> CompiledGraph:

        self._init_workflow(self.agent_config)

        # Bind tools to LLM if supported
        # Tested for OpenAI
        if hasattr(self.tool_llm, "bind_tools"):
            self.tool_llm = self.tool_llm.bind_tools(self.tools)
        else:
            if len(self.tools) > 0:
                raise AttributeError(
                    "The provided tool_model does not support tools. "
                    f"Model: {self.tool_llm_config.llm.endpoint_name}, "
                    f"Tools configured: {len(self.tools)}"
                )

        # Create workflow graph
        workflow = StateGraph(ChatAgentState)

        # Set up nodes
        workflow.set_entry_point(self.name)
        workflow.add_node(self.name, self.call_tool_model)
        # If you don't use filters in the vector search you can use ChatAgentToolNode(self.tools)
        workflow.add_node(f"{self.name}_tools", ChatAgentToolNode(self.tools))
        workflow.add_node(f"{self.name}_summary_agent", self.call_summary_model)

        # Set up conditional routing
        workflow.add_conditional_edges(
            self.name,
            self.choose_node,
            {
                "continue": f"{self.name}_tools",
                "end": END,
            },
        )

        # Set up linear edges
        workflow.add_edge(f"{self.name}_tools", f"{self.name}_summary_agent")
        workflow.add_edge(f"{self.name}_summary_agent", END)

        return workflow.compile()


    
    def choose_node(self, state: ChatAgentState) -> str:

        messages = state["messages"]
        if not messages:
            return "end"

        last_message = messages[-1]

        # Check if the last message has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        elif isinstance(last_message, dict) and last_message.get("tool_calls"):
            return "continue"
        else:
            return "end"

    # Enable for evaluation during development
    # @mlflow.trace(name="call_tool_model", span_type=mlflow.entities.SpanType.AGENT)
    def call_tool_model(self, state: ChatAgentState, config: RunnableConfig) -> Dict[str, List]:

        # Extract messages and add system prompt
        messages = state.messages if hasattr(state, "messages") else state.get("messages", [])
        system_message = SystemMessage(content=self.tool_llm_config.llm.system_prompt)
        messages = messages + [system_message]

        # Invoke LLM
        response = self.tool_llm.invoke(messages, config)

        # Format response
        formatted_messages = self._format_tool_response(response)

        return {"messages": formatted_messages}

    
    def _format_tool_response(self, response) -> List:

        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
        elif isinstance(response, list) and response and isinstance(response[0], dict):
            messages = response
        else:
            messages = [response]

        # Limit tool calls to prevent excessive parallel execution
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                # Limit to first tool call to prevent overwhelming the system
                last_message.tool_calls = last_message.tool_calls[:1]
                messages[-1] = last_message

        return messages
    
   
    def call_summary_model(self, state: ChatAgentState, config: RunnableConfig) -> Dict[str, List]:

        # Extract messages and add summary system prompt
        messages = state.messages if hasattr(state, "messages") else state.get("messages", [])
        system_message = SystemMessage(content=self.summary_llm_config.llm.system_prompt)
        messages = messages + [system_message]

        # Invoke summary LLM
        response = self.summary_llm.invoke(messages, config)

        # Format response
        formatted_messages = self._format_summary_response(response)

        return {"messages": formatted_messages}
    

    def _format_summary_response(self, response) -> List:

        if isinstance(response, dict) and "messages" in response:
            return response["messages"]
        elif isinstance(response, list) and response and isinstance(response[0], dict):
            return response
        else:
            return [response]

