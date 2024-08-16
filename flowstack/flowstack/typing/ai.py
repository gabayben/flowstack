from typing import Any, NotRequired, Optional, TypedDict, Union

class ValidToolCall(TypedDict):
    name: str
    args: dict[str, Any]
    id: NotRequired[Optional[str]]

class InvalidToolCall(TypedDict):
    name: NotRequired[Optional[str]]
    args: NotRequired[Optional[str]]
    id: NotRequired[Optional[str]]
    error: NotRequired[Optional[str]]

ToolCall = Union[ValidToolCall, InvalidToolCall]

class UsageMetadata(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int