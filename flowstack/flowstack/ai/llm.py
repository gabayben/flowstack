from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator, final

from flowstack.core.utils.threading import run_async, run_async_iter
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptLike, PromptStack

class LLM(ABC):
    @abstractmethod
    def generate(self, input: PromptLike, **kwargs) -> BaseMessage:
        pass

    @abstractmethod
    async def agenerate(self, input: PromptLike, **kwargs) -> BaseMessage:
        pass

    @abstractmethod
    def stream(self, input: PromptLike, **kwargs) -> Iterator[BaseMessage]:
        pass

    @abstractmethod
    async def astream(self, input: PromptLike, **kwargs) -> AsyncIterator[BaseMessage]:
        pass

class BaseLLM(LLM, ABC):
    @final
    def generate(self, input: PromptLike, **kwargs) -> BaseMessage:
        return self._generate(PromptStack(input), **kwargs)

    @abstractmethod
    def _generate(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass

    @final
    async def agenerate(self, input: PromptLike, **kwargs) -> BaseMessage:
        return await self._agenerate(PromptStack(input), **kwargs)

    async def _agenerate(self, stack: PromptStack, **kwargs) -> BaseMessage:
        return await run_async(self._generate, stack, **kwargs)
    
    @final
    def stream(self, input: PromptLike, **kwargs) -> Iterator[BaseMessage]:
        yield from self._stream(PromptStack(input), **kwargs)
    
    def _stream(self, stack: PromptStack, **kwargs) -> Iterator[BaseMessage]:
        yield self._generate(stack, **kwargs)
    
    @final
    async def astream(self, input: PromptLike, **kwargs) -> AsyncIterator[BaseMessage]:
        async for chunk in self._astream(PromptStack(input), **kwargs):
            yield chunk
    
    async def _astream(self, stack: PromptStack, **kwargs) -> AsyncIterator[BaseMessage]:
        async for chunk in run_async_iter(self._stream, stack, **kwargs):
            yield chunk