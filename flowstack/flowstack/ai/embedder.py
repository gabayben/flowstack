from abc import ABC, abstractmethod
from typing import final

from flowstack.artifacts import Artifact
from flowstack.core import TypedKey
from flowstack.core.utils.threading import run_async

class Embedder(ABC):
    @abstractmethod
    def embed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        pass

    @abstractmethod
    async def aembed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        pass

class BaseEmbedder(Embedder, ABC):
    @final
    def embed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        return self._embed(artifacts, **kwargs)

    @abstractmethod
    def _embed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        pass

    @final
    async def aembed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        return await self._aembed(artifacts, **kwargs)

    async def _aembed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        return await run_async(self._embed, artifacts, **kwargs)

TEXT_EMBEDDER = TypedKey[Embedder]('text_embedder')
IMAGE_EMBEDDER = TypedKey[Embedder]('image_embedder')