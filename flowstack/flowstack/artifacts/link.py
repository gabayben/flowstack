from typing import Any, Optional, override

from docarray.typing import TextUrl
from pydantic import Field

from flowstack.artifacts import ArtifactMetadata, Modality, Text, Utf8Artifact
from flowstack.utils.string import mapping_to_str

class LinkMetadata(ArtifactMetadata):
    title: str = ''
    position: Optional[int] = None
    text: Optional[str] = None

class Link(Utf8Artifact):
    link: TextUrl
    metadata: LinkMetadata = Field(default_factory=LinkMetadata)

    @property
    @override
    def modality(self) -> Modality:
        return Modality.TEXT

    @property
    def title(self) -> str:
        return self.metadata.get('title')

    @property
    def position(self) -> Optional[int]:
        return self.metadata.get('position')

    @property
    def text(self) -> str:
        return self.metadata.get('text')

    def __init__(
        self,
        link: str,
        title: str,
        position: int | None = None,
        text: str | None = None,
        metadata: dict[str, Any] = {},
        **kwargs
    ):
        super().__init__(
            link=TextUrl(link),
            metadata=LinkMetadata(
                **metadata,
                title=title,
                position=position,
                text=text
            ),
            **kwargs
        )

    @classmethod
    def content_fields(cls) -> set[str]:
        return {'link', 'title', 'position', 'text'}

    def to_bytes(self, **kwargs) -> bytes:
        return self.link.load_bytes()

    def to_utf8(self) -> str:
        return mapping_to_str(dict(self))

    def to_text_artifact(self) -> Text:
        return Text(
            self.link.load(),
            **self.model_dump(exclude={'link', 'metadata'}),
            metadata=ArtifactMetadata(link=str(self.link), **self.metadata)
        )

    def set_content(self, link: str, *args) -> None:
        self.link = TextUrl(link)