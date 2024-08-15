from typing import Any, Union

from pydantic import BaseModel

from flowstack.artifacts import TextLike

class ImagePrompt(BaseModel):
    content: str
    metadata: dict[str, Any]

    def __init__(
        self,
        input: 'ImagePromptLike',
        metadata: dict[str, Any] = {}
    ):
        pass

ImagePromptLike = Union[TextLike, ImagePrompt]