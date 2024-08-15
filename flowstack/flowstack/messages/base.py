from abc import ABC
from enum import StrEnum
from typing import Any, Union

from pydantic import Field

from flowstack.artifacts import Artifact, Text, TextLike
from flowstack.typing import Serializable

MessageValues = Union[TextLike, list[TextLike]]

class MessageType(StrEnum):
    USER = 'human'
    SYSTEM = 'system'
    Assistant = 'assistant'
    TOOL = 'tool'

class BaseMessage(Serializable, ABC):
    message_type: str
    content: list[Artifact]
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __init__(
        self,
        message_type: str,
        content: MessageValues,
        metadata: dict[str, Any] = {},
        **kwargs
    ):
        super().__init__(
            message_type=message_type,
            content=_to_artifacts(content),
            metadata=metadata,
            **kwargs
        )

    def __str__(self) -> str:
        return '\n\n'.join(str(artifact) for artifact in self.content)

MessageLike = Union[TextLike, tuple[str, TextLike], BaseMessage]

def _to_artifacts(content: MessageValues) -> list[Artifact]:
    content = [content] if not isinstance(content, list) else content
    return [Text.from_input(value) for value in content]