from abc import ABC, abstractmethod
from typing import Any, NamedTuple, Optional, final

from flowstack.artifacts import Text, TextLike
from flowstack.core.utils.threading import run_async

class TextClassification(NamedTuple):
    text: str
    score: Optional[float] = None
    metadata: dict[str, Any] = {}

class TextClassifier(ABC):
    @abstractmethod
    def classify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[list[TextClassification]]:
        pass

    @abstractmethod
    async def aclassify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[list[TextClassification]]:
        pass

class BaseTextClassifier(TextClassifier, ABC):
    @final
    def classify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[list[TextClassification]]:
        return self._classify(
            [Text.from_text(input) for input in inputs],
            labels=labels,
            **kwargs
        )

    @abstractmethod
    def _classify(
        self,
        texts: list[Text],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[list[TextClassification]]:
        pass

    @final
    async def aclassify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[list[TextClassification]]:
        return await self._aclassify(
            [Text.from_text(input) for input in inputs],
            labels=labels,
            **kwargs
        )

    async def _aclassify(
        self,
        texts: list[Text],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[list[TextClassification]]:
        return await run_async(
            self._classify,
            texts,
            labels=labels,
            **kwargs
        )