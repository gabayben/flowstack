from typing import Any, Literal

from flowstack.messages import BaseMessage, MessageValues, MessageType

class UserMessage(BaseMessage):
    message_type: Literal[MessageType.USER]

    def __init__(
        self,
        content: MessageValues,
        metadata: dict[str, Any] = {},
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.USER,
            content=content,
            metadata=metadata,
            **kwargs
        )