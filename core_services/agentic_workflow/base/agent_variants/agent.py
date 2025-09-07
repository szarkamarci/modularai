from uuid import uuid4

from model_config.agentic_config import AgentConfigType
from langgraph.graph.state import CompiledStateGraph
from mlflow.pyfunc.model import ChatAgent
from mlflow.types.agent import ChatAgentChunk, ChatAgentMessage, ChatAgentResponse

class Agent(ChatAgent):

    def _init__(self, agentic_config: AgentConfigType):


        self.agent_config = agent_config
        self.name = agent_config.name
        self.agent = self.create_agent_workflow()

    def load_context(self, context):
        pass

    def create_agent_workflow(self):
        pass
    
    def predict(
        self,
        messages: list = None,
        context=None,
        custom_inputs=None,
    ) -> ChatAgentResponse:
        request = self._prepare_input(messages)

        response = self.agent.invoke(request, stream_mode="values", debug=False)

        final_response = self._prepare_output(response)

        return final_response
    
    def _prepare_input(self, messages: list) -> dict:

        messages = self._filter_max_chat_history(messages, max_history=10)
        messages = self._filter_messages_by_role(messages=messages, role="tool")
        messages = self._add_missing_message_ids(messages)
        messages = self._convert_messages_to_dict(messages)

        return {"messages": messages}

    def _prepare_output(self, response: dict) -> ChatAgentResponse:
        # Convert all response messages to ChatAgentMessage objects
        messages_out = [self._convert_to_chat_agent_message(msg) for msg in response["messages"]]
        # Select relevant messages (assistant and tool) in reverse order
        selected = self._select_response_messages(messages_out)

        return ChatAgentResponse(messages=selected)
    
    def _convert_to_chat_agent_message(self, message) -> ChatAgentMessage:
        if isinstance(message, ChatAgentMessage) or hasattr(message, "role"):
            return ChatAgentMessage(
                role=message.role,
                content=message.content,
                id=str(uuid4()),
            )
        elif isinstance(message, dict):
            new_message = {**message, "id": str(uuid4())}
            return ChatAgentMessage(**new_message)
        else:
            raise TypeError(f"Unsupported message type: {type(message)}")

    def _select_response_messages(self, messages: list) -> list:
        response_messages = []
        tool_found = False
        assistant_found = False

        for msg in reversed(messages):
            if msg.role == "tool" and not tool_found:
                tool_found = True
                response_messages.append(msg)
            elif msg.role == "assistant" and not assistant_found:
                assistant_found = True
                response_messages.append(msg)
            if tool_found and assistant_found:
                break

        return list(reversed(response_messages))

    
    def predict_stream(
        self,
        messages: list = None,
        context=None,
        custom_inputs=None,
    ) -> Generator[ChatAgentChunk, None, None]:
        # Prepare input in the same way as predict()
        request = self._prepare_input(messages)
        stream_response = self.agent.invoke(request, stream_mode="values", debug=False)

        # For streaming, yield each chunk as it becomes available.
        for raw_chunk in stream_response["messages"]:
            # Convert the raw chunk to a ChatAgentMessage
            if isinstance(raw_chunk, ChatAgentMessage) or hasattr(raw_chunk, "role"):
                msg = ChatAgentMessage(
                    role=raw_chunk.role,
                    content=raw_chunk.content,
                    id=str(uuid4()),
                )
            elif isinstance(raw_chunk, dict):
                new_message = {**raw_chunk, "id": str(uuid4())}
                msg = ChatAgentMessage(**new_message)
            else:
                raise TypeError(f"Unsupported message type: {type(raw_chunk)}")
            yield ChatAgentChunk(delta=msg)

    
    def _convert_messages_to_dict(self, messages: list[ChatAgentMessage]) -> list[dict]:
        result = []
        for m in messages:

            def convert(m):
                if isinstance(m, dict):
                    return m
                for method, kwargs in (
                    ("model_dump_compat", {"exclude_none": True}),
                    ("model_dump", {}),
                    ("to_dict", {}),
                ):
                    if hasattr(m, method):
                        return getattr(m, method)(**kwargs)
                raise TypeError(f"Cannot convert message of type {type(m)} to dict")

            result = [convert(m) for m in messages]
        return result

    
        def _add_missing_message_ids(self, messages: list) -> list:
        messages_in = []
        for message in messages:
            if isinstance(message, dict):
                if not message.get("id"):
                    new_message = {**message, "id": str(uuid4())}
                else:
                    new_message = message
                    messages_in.append(ChatAgentMessage(**new_message))
            else:
                if not hasattr(message, "id") or not message.id:
                    message.id = str(uuid4())
                    messages_in.append(message)
        return messages_in

    def _filter_messages_by_role(self, messages: list, role: str) -> list:
        filtered = []
        for msg in messages:
            if isinstance(msg, dict):
                if msg.get("role") == role:
                    filtered.append(msg)
            elif hasattr(msg, "role") and getattr(msg, "role") == role:
                filtered.append(msg)

        return filtered

    def _filter_max_chat_history(self, messages: list, max_history: int) -> list:
        if not messages:
            return messages

        return messages[-max_history:]

