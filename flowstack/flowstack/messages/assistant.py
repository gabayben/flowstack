from typing import Any, Literal

from flowstack.messages import BaseMessage, MessageValues, MessageType

class AssistantMessage(BaseMessage):
    message_type: Literal[MessageType.Assistant]

    def __init__(
        self,
        content: MessageValues,
        metadata: dict[str, Any] = {},
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.Assistant,
            content=content,
            metadata=metadata,
            **kwargs
        )