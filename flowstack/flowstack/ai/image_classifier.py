from abc import ABC, abstractmethod
from typing import Any, NamedTuple, Optional, final

from flowstack.artifacts import BlobLike, Image
from flowstack.core.utils.threading import run_async

class ImageClassification(NamedTuple):
    text: str
    score: Optional[float] = None
    metadata: dict[str, Any] = {}

class ImageClassifier(ABC):
    @abstractmethod
    def classify(
        self,
        inputs: list[BlobLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[ImageClassification]:
        pass

    @abstractmethod
    async def aclassify(
        self,
        inputs: list[BlobLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[ImageClassification]:
        pass

class BaseImageClassifer(ImageClassifier, ABC):
    @final
    def classify(
        self,
        inputs: list[BlobLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[ImageClassification]:
        return self._classify(
            [Image.from_blob(input) for input in inputs],
            labels=labels,
            **kwargs
        )

    @abstractmethod
    def _classify(
        self,
        images: list[Image],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[ImageClassification]:
        pass

    @final
    async def aclassify(
        self,
        inputs: list[BlobLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[ImageClassification]:
        return await self._aclassify(
            [Image.from_blob(input) for input in inputs],
            labels=labels,
            **kwargs
        )

    async def _aclassify(
        self,
        images: list[Image],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[ImageClassification]:
        return await run_async(
            self._classify,
            images,
            labels=labels,
            **kwargs
        )