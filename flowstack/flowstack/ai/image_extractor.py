from abc import ABC, abstractmethod
from typing import Any, NamedTuple, final

from flowstack.artifacts import BlobLike, Image
from flowstack.core.utils.threading import run_async

class ImageExtraction(NamedTuple):
    text: str
    metadata: dict[str, Any] = {}

class ImageExtractor(ABC):
    @abstractmethod
    def extract(self, inputs: list[BlobLike], **kwargs) -> list[ImageExtraction]:
        pass

    @abstractmethod
    async def aextract(self, inputs: list[BlobLike], **kwargs) -> list[ImageExtraction]:
        pass

class BaseImageExtractor(ImageExtractor, ABC):
    @final
    def extract(self, inputs: list[BlobLike], **kwargs) -> list[ImageExtraction]:
        return self._extract([Image.from_blob(input) for input in inputs], **kwargs)

    @abstractmethod
    def _extract(self, images: list[Image], **kwargs) -> list[ImageExtraction]:
        pass

    @final
    async def aextract(self, inputs: list[BlobLike], **kwargs) -> list[ImageExtraction]:
        return await self._aextract([Image.from_blob(input) for input in inputs], **kwargs)

    async def _aextract(self, images: list[Image], **kwargs) -> list[ImageExtraction]:
        return await run_async(self._extract, images, **kwargs)