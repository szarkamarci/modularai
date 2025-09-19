import os
from typing import Annotated, Dict, List, Literal, Union

from pydantic import BaseModel, Field

class LlmConfig(BaseModel):
    endpoint_name: str
    max_tokens: int
    temperature: float
    system_prompt: str


# Wrapper to account for an extra nesting level in YAML.
class AgentWrapper(BaseModel):
    llm: LlmConfig


class EmbeddingConfig(BaseModel):
    source_table: str
    source_column: str
    source_primary_key: str
    vector_search_endpoint: str
    endpoint_name: str
    vs_index: str
    columns_to_sync: List[str]


class RetrievalConfig(BaseModel):
    retrieved_chunks: int
    similarity_search_query_type: str
    

class RetrieverToolConfig(BaseModel):
    type: str
    name: str
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    description: str


class SubAgentConfig(BaseModel):
    name: str
    tool_llm: AgentWrapper

AgentConfigType = Annotated[
    Union["SupervisorAgentConfig", "ToolAgentConfig", "TopicRetrieverAgentConfig"],
    Field(discriminator="agent_type"),
]


class SupervisorAgentConfig(SubAgentConfig):
    agent_type: Literal["supervisor"]
    decision_options: List[Dict[str, str]]
    # Each sub-agent is a dict with a dynamic key mapping to an AgentConfig.
    sub_agents: List[AgentConfigType]


class ToolAgentConfig(SubAgentConfig):
    agent_type: Literal["tool"]
    tools: List[RetrieverToolConfig]
    summary_llm: AgentWrapper
    
class TopicRetrieverAgentConfig(ToolAgentConfig):
    agent_type: Literal["topic_retriever"]
    topics: List[str]


MessageType = Dict[str, List[Dict[str, str]]]


class ExampleConfig(BaseModel):
    input_example: MessageType
    output_example: MessageType


class ModelConfig(BaseModel):
    # arhitecture: dict
    example_messages: ExampleConfig
    agent: SupervisorAgentConfig
    
