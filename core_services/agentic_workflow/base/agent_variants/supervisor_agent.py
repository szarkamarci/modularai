from typing import Dict, List

import mlflow
from databricks_langchain import ChatDatabricks
from langchain_core.messages.utils import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from mlflow.langchain.chat_agent_langgraph import ChatAgentState

from .agent import Agent


class SupervisorAgent(Agent):

    def __init__(self, agent_config: dict):

        self.agent_config = agent_config
        self.name = self.agent_config.name
        self.decision_options = self.agent_config.decision_options
        self.tool_llm = self.agent_config.tool_llm

        # Initialize LLM
        self.summary_max_tokens = int(self.tool_llm.llm.max_tokens)
        self.system_prompt = self.tool_llm.llm.system_prompt
        self.llm = ChatDatabricks(
            model=self.tool_llm.llm.endpoint_name,
            max_tokens=self.summary_max_tokens,
        )

        # Initialize sub-agents
        self.sub_agents_config = self.agent_config.sub_agents
        self.sub_agents = self._create_sub_agents()

        # Create the agent workflow
        self.agent = self.create_agent_workflow()

    
    def _create_sub_agents(self) -> List[Agent]:
    
        # Import here to avoid circular imports
        from .tool_agent import ToolAgent

        sub_agents = []
        for sub_agent_config in self.sub_agents_config:
            if sub_agent_config.agent_type == "supervisor":
                sub_agents.append(SupervisorAgent(sub_agent_config))
            elif sub_agent_config.agent_type == "tool":
                sub_agents.append(ToolAgent(sub_agent_config))
            # Note: Additional agent types can be added here as needed

        return sub_agents

    def get_workflow(self) -> CompiledGraph:

        return self.agent



    def create_agent_workflow(self) -> CompiledGraph:

        workflow = StateGraph(ChatAgentState)
        workflow.set_entry_point(self.name)
        workflow.add_node(self.name, self.call_supervisor_model)

        # Add nodes for each sub-agent
        conditional_edges = {}
        for sub_agent in self.sub_agents:
            workflow.add_node(sub_agent.name, sub_agent.agent)
            conditional_edges[sub_agent.name] = sub_agent.name

        # Add end condition
        conditional_edges["end"] = END

        # Set up conditional routing based on supervisor decision
        workflow.add_conditional_edges(
            self.name,
            self.choose_node,
            conditional_edges,
        )

        # Connect all sub-agents to end
        for sub_agent in self.sub_agents:
            workflow.add_edge(sub_agent.name, END)

        return workflow.compile()

    

    def choose_node(self, state: ChatAgentState) -> str:
    
        messages = state["messages"]
        if not messages:
            return "end"

        last_message = messages[-1]
        message_content = last_message.get("content", "").lower()

        # Check decision options for keyword matches
        for option in self.decision_options:
            keyword = option.get("keyword", "").lower()
            if keyword and keyword in message_content:
                return option.get("agent", "end")

        return "end"

    

@mlflow.trace(name="call_supervisor_model", span_type=mlflow.entities.SpanType.AGENT)
    def call_supervisor_model(
        self, state: ChatAgentState, config: RunnableConfig
    ) -> Dict[str, List]:

        # Extract messages from state
        messages = state.messages if hasattr(state, "messages") else state.get("messages", [])

        # Add system prompt
        supervisor_system_message = SystemMessage(content=self.system_prompt)
        messages = [supervisor_system_message] + messages

        # Invoke LLM
        response = self.llm.invoke(messages, config)

        # Format response
        formatted_messages = self._format_response(response)

        return {"messages": formatted_messages}

    def _format_response(self, response) -> List:

        if isinstance(response, dict) and "messages" in response:
            return response["messages"]
        elif isinstance(response, list) and response and isinstance(response[0], dict):
            return response
        else:
            return [response]