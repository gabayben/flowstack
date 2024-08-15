from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator, Literal, Optional, Type, Union, final, overload

from pydantic import BaseModel

from flowstack.core.utils.threading import run_async, run_async_iter
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptLike, PromptStack

class ChatGenerator(ABC):
    @overload
    def chat(
        self,
        input: PromptLike,
        output_type: Literal[None] = None,
        **kwargs
    ) -> BaseMessage:
        ...

    @overload
    def chat[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        ...

    @abstractmethod
    def chat[T: BaseModel](
        self,
        input: PromptLike,
        *,
        output_type: Optional[Type[T]] = None,
        **kwargs
    ) -> Union[BaseMessage, T]:
        pass

    @overload
    async def achat(
        self,
        input: PromptLike,
        output_type: Literal[None] = None,
        **kwargs
    ) -> BaseMessage:
        ...

    @overload
    async def achat[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        ...

    @abstractmethod
    async def achat[T: BaseModel](
        self,
        input: PromptLike,
        *,
        output_type: Optional[Type[T]] = None,
        **kwargs
    ) -> Union[BaseMessage, T]:
        pass

    @abstractmethod
    def stream(self, input: PromptLike, **kwargs) -> Iterator[BaseMessage]:
        pass

    @abstractmethod
    async def astream(self, input: PromptLike, **kwargs) -> AsyncIterator[BaseMessage]:
        pass

class BaseChatGenerator(ChatGenerator, ABC):
    # noinspection PyMethodOverriding
    @overload
    def chat(
        self,
        input: PromptLike,
        output_type: Literal[None] = None,
        **kwargs
    ) -> BaseMessage:
        ...

    # noinspection PyMethodOverriding
    @overload
    def chat[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        ...

    @final
    def chat[T: BaseModel](
        self,
        input: PromptLike,
        *,
        output_type: Optional[Type[T]] = None,
        **kwargs
    ) -> Union[BaseMessage, T]:
        stack = PromptStack(input)
        if output_type is None:
            return self._chat(stack, **kwargs)
        return self._structured_chat(stack, output_type, **kwargs)

    @abstractmethod
    def _chat(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass

    def _structured_chat[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    # noinspection PyMethodOverriding
    @overload
    async def achat(
        self,
        input: PromptLike,
        output_type: Literal[None] = None,
        **kwargs
    ) -> BaseMessage:
        ...

    # noinspection PyMethodOverriding
    @overload
    async def achat[T: BaseModel](
        self,
        input: PromptLike,
        output_type: Type[T],
        **kwargs
    ) -> T:
        ...

    @final
    async def achat[T: BaseModel](
        self,
        input: PromptLike,
        *,
        output_type: Optional[Type[T]] = None,
        **kwargs
    ) -> Union[BaseMessage, T]:
        stack = PromptStack(input)
        if output_type is None:
            return await self._achat(stack, **kwargs)
        return await self._astructured_chat(stack, output_type, **kwargs)

    async def _achat(self, stack: PromptStack, **kwargs) -> BaseMessage:
        return await run_async(self._chat, stack, **kwargs)

    async def _astructured_chat[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        return await run_async(self._structured_chat, stack, output_type, **kwargs)
    
    @final
    def stream(self, input: PromptLike, **kwargs) -> Iterator[BaseMessage]:
        yield from self._stream(PromptStack(input), **kwargs)
    
    def _stream(self, stack: PromptStack, **kwargs) -> Iterator[BaseMessage]:
        yield self._chat(stack, **kwargs)
    
    @final
    async def astream(self, input: PromptLike, **kwargs) -> AsyncIterator[BaseMessage]:
        async for chunk in self._astream(PromptStack(input), **kwargs):
            yield chunk
    
    async def _astream(self, stack: PromptStack, **kwargs) -> AsyncIterator[BaseMessage]:
        async for chunk in run_async_iter(self._stream, stack, **kwargs):
            yield chunk