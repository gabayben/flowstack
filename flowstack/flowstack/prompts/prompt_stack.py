from typing import Optional, Type, Union

from pydantic import BaseModel

from flowstack.artifacts import TextLike
from flowstack.messages import (
    AnyMessage,
    AssistantMessage,
    BaseMessage,
    MessageLike,
    MessageType,
    SystemMessage,
    ToolMessage,
    UserMessage
)

class PromptStack(BaseModel):
    def __init__(self, input: Optional['PromptLike'] = None, message_type: Optional[str] = None):
        pass

    @property
    def messages(self) -> list[BaseMessage]:
        raise NotImplementedError()

    @property
    def system_messages(self) -> list[SystemMessage]:
        raise NotImplementedError()

    @property
    def user_messages(self) -> list[UserMessage]:
        raise NotImplementedError()

    @property
    def assistant_messages(self) -> list[AssistantMessage]:
        raise NotImplementedError()

    @property
    def tool_messages(self) -> list[ToolMessage]:
        raise NotImplementedError()

    def add_message(self, message: Union[TextLike, BaseMessage], message_type: str) -> BaseMessage:
        if message_type == MessageType.SYSTEM:
            self._check_message(message, SystemMessage, message_type)
            return self.add_system_message(message)
        elif message_type == MessageType.USER:
            self._check_message(message, UserMessage, message_type)
            return self.add_user_message(message)
        elif message_type == MessageType.Assistant:
            self._check_message(message, AssistantMessage, message_type)
            return AssistantMessage(message)
        elif message_type == MessageType.TOOL:
            self._check_message(message, ToolMessage, message_type)
            return ToolMessage(message)
        return AnyMessage(message_type, message)

    def add_system_message(self, message: Union[TextLike, SystemMessage]) -> SystemMessage:
        pass

    def add_user_message(self, message: Union[TextLike, UserMessage]) -> UserMessage:
        pass

    def add_assistant_message(self, message: Union[TextLike, AssistantMessage]) -> AssistantMessage:
        pass

    def add_tool_message(self, message: Union[TextLike, ToolMessage]) -> ToolMessage:
        pass

    def _check_message(
        self,
        message: Union[TextLike, BaseMessage],
        expected: Type[BaseMessage],
        message_type: str
    ):
        if isinstance(message, BaseMessage) and not isinstance(message, expected):
            raise ValueError(
                f'Expected {expected.__name__} for {message_type}, got {message.__class__.__name__}.'
            )

PromptLike = Union[MessageLike, list[MessageLike], PromptStack]