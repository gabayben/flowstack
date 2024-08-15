from typing import Any, Literal

from flowstack.messages import BaseMessage, MessageValues, MessageType

class ToolMessage(BaseMessage):
    message_type: Literal[MessageType.TOOL]

    def __init__(
        self,
        content: MessageValues,
        metadata: dict[str, Any] = {},
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.TOOL,
            content=content,
            metadata=metadata,
            **kwargs
        )