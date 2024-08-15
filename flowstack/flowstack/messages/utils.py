from typing import Union

from flowstack.messages import BaseMessage, UserMessage, MessageValues

def coerce_to_messages(content: Union[MessageValues, list[BaseMessage]]) -> list[BaseMessage]:
    if isinstance(content, list) and isinstance(content[0], BaseMessage):
        return content
    return [UserMessage(content)]