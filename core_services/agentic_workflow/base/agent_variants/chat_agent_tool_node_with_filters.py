import json
from json import JSONDecodeError
from typing import Any, Dict, Optional
from uuid import uuid4

from langchain_core.messages import convert_to_messages
from langchain_core.messages.ai import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import Input
from mlflow.langchain.chat_agent_langgraph import (
    ChatAgentToolNode,
    parse_message,
)


def safe_json_loads(content: str) -> Optional[Any]:
    try:
        return json.loads(content)
    except JSONDecodeError:
        return None

    
class ChatAgentToolNodeWithFilters(ChatAgentToolNode):

    def get_query_message(self, input: Input, have_filters=True):
        last_message = input["messages"][-1]

        if last_message.get("tool_calls", None):
            for tool_call in last_message["tool_calls"]:
                if tool_call.get("function", None):
                    # Parse the function's arguments once
                    tool_args = safe_json_loads(tool_call["function"]["arguments"]) or {}

                    filters: Dict = {}

                    if have_filters and "filters" in tool_args:
                        if isinstance(tool_args["filters"], dict):
                            filters = tool_args["filters"]
                        elif isinstance(tool_args["filters"], list):
                            for tool_arg in tool_args["filters"]:
                                if (
                                    isinstance(tool_arg, dict)
                                    and "key" in tool_arg
                                    and "value" in tool_arg
                                ):
                                    filters[tool_arg["key"]] = tool_arg["value"]
                                    # input format:
                                    #   ["key":"locations LIKE", "value":"Rohweder"]
                                    # output format:
                                    #   {"locations LIKE": "Rohweder", "key2": "value2"}    

                    tool_name = tool_call["function"].get("name")
                    if (
                        have_filters
                        and tool_name
                        and hasattr(self.tools_by_name.get(tool_name), "filters")
                    ):
                        self.tools_by_name[tool_name].filters = filters
                    elif (
                        not have_filters
                        and tool_name
                        and hasattr(self.tools_by_name.get(tool_name), "filters")
                    ):
                        self.tools_by_name[tool_name].filters = None
    
     
    def format_messages(self, input: Input):
        messages = input["messages"]

        for msg in messages:
            for tool_call in msg.get("tool_calls", []):
                tool_call["name"] = tool_call["function"].get("name")
                parsed_args = safe_json_loads(tool_call["function"].get("arguments", ""))
                tool_call["args"] = parsed_args if parsed_args is not None else {}

    def get_new_messages(self, chat_result):
        new_messages = []
        custom_outputs = None

        for m in chat_result.get("messages", []):
            if isinstance(m.content, list) and not m.content:
                m.content = "Empty query result, no document has been returned"

            parsed_content = safe_json_loads(m.content)

            if parsed_content is not None:
                if all(key in parsed_content for key in ("format", "value", "truncated")):
                    nested_parsed = safe_json_loads(parsed_content.get("value", ""))

                    if nested_parsed is not None:
                        parsed_content = nested_parsed

                if "custom_outputs" in parsed_content:
                    custom_outputs = parsed_content["custom_outputs"]

                if m.id is None:
                    m.id = str(uuid4())
                new_messages.append(parse_message(m, attachments=parsed_content.get("attachments")))
            else:
                new_messages.append(parse_message(m))

        return new_messages, custom_outputs
    
    def invoke(self, input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:

        input_1 = dict(input)

        #######
        # self.get_query_message(input, have_filters = True)
        # self.format_messages(input)
        # Set a flag to skip argument parsing in convert_to_messages
        input["messages"] = convert_to_messages(input["messages"])
        chat_result = super(ChatAgentToolNode, self).invoke(input, config, **kwargs)

        new_messages, custom_outputs = self.get_new_messages(chat_result)
        #######

        if new_messages[0]["content"] == "Empty query result, no document has been returned":
            self.get_query_message(input_1, have_filters=False)
            self.format_messages(input_1)
            # input_1["__skip_args_parsing__"] = True
            # input_1["messages"] = convert_to_messages(input_1["messages"])

            last_message = input_1["messages"][-1]
            last_message["tool_calls"][0].pop("function", None)
            last_message["tool_calls"][0]["args"].pop("filters", None)

            input_1["messages"][-1] = AIMessage(**last_message)

            chat_result = super(ChatAgentToolNode, self).invoke(input_1, config, **kwargs)

            new_messages, custom_outputs = self.get_new_messages(chat_result)

        return {"messages": new_messages, "custom_outputs": custom_outputs}