from abc import ABC
from typing import Self, Union, override

from flowstack.artifacts import ArtifactMetadata, Modality, TextLike, Utf8Artifact

class TextBase(Utf8Artifact, ABC):
    content: str

    @property
    @override
    def modality(self) -> Modality:
        return Modality.TEXT

    def __init__(
        self,
        content: str,
        metadata: ArtifactMetadata = ArtifactMetadata(),
        **kwargs
    ):
        super().__init__(
            content=content,
            metadata=metadata,
            **kwargs
        )

    @classmethod
    def from_text(cls, input: TextLike) -> Self:
        return input if isinstance(input, cls) else cls.__class__(str(input))

    @classmethod
    def content_fields(cls) -> set[str]:
        return {'text'}

    @classmethod
    def from_bytes(cls, data: bytes, **kwargs) -> Self:
        return cls(data.decode('utf-8'))

    def to_utf8(self) -> str:
        return self.content

    def set_content(self, content: Union[str, bytes]) -> None:
        if isinstance(content, str):
            self.content = content
        else:
            self.content = content.decode('utf-8')

class Text(TextBase):
    """Artifact for capturing free text from within document."""