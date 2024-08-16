from abc import ABC, abstractmethod
from typing import Type, final

from pydantic import BaseModel

from flowstack.core.utils.threading import run_async
from flowstack.prompts import PromptLike, PromptStack

class StructuredLLM(ABC):
    @abstractmethod
    def structured[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    @abstractmethod
    async def astructured[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

class BaseStructuredLLM(StructuredLLM, ABC):
    @final
    def structured[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        return self._structured(PromptStack(input), output_type, **kwargs)

    @abstractmethod
    def _structured[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    @final
    async def astructured[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        return await self._astructured(PromptStack(input), output_type, **kwargs)

    async def _astructured[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        return await run_async(self._structured, stack, output_type, **kwargs)