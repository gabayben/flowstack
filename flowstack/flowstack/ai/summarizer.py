from abc import ABC, abstractmethod
import asyncio
from typing import TYPE_CHECKING, final, override

from flowstack.artifacts import Text, TextLike
from flowstack.core.utils.threading import run_async
from flowstack.prompts import PromptLike, PromptStack

if TYPE_CHECKING:
    from flowstack.ai import LLM

class Summarizer(ABC):
    @classmethod
    def from_llm(cls, llm: LLM, prompt: PromptLike) -> 'Summarizer':
        return LLMSummarizer(llm, prompt)

    @abstractmethod
    def summarize(self, inputs: list[TextLike], **kwargs) -> list[str]:
        pass

    @abstractmethod
    def asummarize(self, inputs: list[TextLike], **kwargs) -> list[str]:
        pass

class BaseSummarizer(Summarizer, ABC):
    @final
    def summarize(self, inputs: list[TextLike], **kwargs) -> list[str]:
        return self._summarize([Text.from_text(input) for input in inputs], **kwargs)

    @abstractmethod
    def _summarize(self, texts: list[Text], **kwargs) -> list[str]:
        pass

    @final
    async def asummarize(self, inputs: list[TextLike], **kwargs) -> list[str]:
        return await self._asummarize([Text.from_text(input) for input in inputs], **kwargs)

    async def _asummarize(self, texts: list[Text], **kwargs) -> list[str]:
        return await run_async(self._summarize, texts, **kwargs)

class LLMSummarizer(BaseSummarizer):
    def __init__(self, llm: LLM, prompt: PromptLike):
        self._llm = llm
        self._stack = PromptStack(prompt)

    def _summarize(self, texts: list[Text], **kwargs) -> list[str]:
        summaries = []
        for text in texts:
            stack_copy = self._stack.model_copy(deep=True)
            stack_copy.add_user_message(text)
            summaries.append(str(self._llm.generate(stack_copy, **kwargs)))
        return summaries


    @override
    async def _asummarize(self, texts: list[Text], **kwargs) -> list[str]:
        tasks = []
        for text in texts:
            stack_copy = self._stack.model_copy(deep=True)
            stack_copy.add_user_message(text)
            tasks.append(self._llm.agenerate(stack_copy, **kwargs))
        messages = await asyncio.gather(*tasks)
        return [str(message) for message in messages]