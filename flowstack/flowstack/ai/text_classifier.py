from abc import ABC, abstractmethod
import asyncio
from typing import Any, NamedTuple, Optional, TYPE_CHECKING, final, override

from flowstack.artifacts import Text, TextLike
from flowstack.core.utils.threading import run_async
from flowstack.prompts import PromptLike, PromptStack

if TYPE_CHECKING:
    from flowstack.ai import LLM

class TextClassification(NamedTuple):
    text: str
    score: Optional[float] = None
    metadata: dict[str, Any] = {}

class TextClassifier(ABC):
    @classmethod
    def from_llm(cls, llm: LLM, prompt: PromptLike) -> 'TextClassifier':
        return LLMTextClassifier(llm, prompt)

    @abstractmethod
    def classify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[TextClassification]:
        pass

    @abstractmethod
    async def aclassify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[TextClassification]:
        pass

class BaseTextClassifier(TextClassifier, ABC):
    @final
    def classify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[TextClassification]:
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
    ) -> list[TextClassification]:
        pass

    @final
    async def aclassify(
        self,
        inputs: list[TextLike],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[TextClassification]:
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
    ) -> list[TextClassification]:
        return await run_async(
            self._classify,
            texts,
            labels=labels,
            **kwargs
        )

class LLMTextClassifier(BaseTextClassifier):
    def __init__(self, llm: LLM, prompt: PromptLike):
        self._llm = llm
        self._stack = PromptStack(prompt)

    def _classify(
        self,
        texts: list[Text],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[TextClassification]:
        results = []
        for text in texts:
            stack = self._stack.model_copy(deep=True)
            stack.add_user_message(text)
            message = self._llm.generate(stack, **kwargs)
            results.append(TextClassification(str(message)))
        return results

    @override
    async def _aclassify(
        self,
        texts: list[Text],
        labels: Optional[list[str]] = None,
        **kwargs
    ) -> list[TextClassification]:
        tasks = []
        for text in texts:
            stack = self._stack.model_copy(deep=True)
            stack.add_user_message(text)
            tasks.append(self._llm.agenerate(stack, **kwargs))
        messages = await asyncio.gather(*tasks)
        return [TextClassification(str(message)) for message in messages]