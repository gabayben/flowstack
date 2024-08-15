from typing import AsyncIterator, Iterator, Type, override

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from flowstack.ai.chat_generator import BaseChatGenerator
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptStack

class OpenAIChatGenerator(BaseChatGenerator):
    def __init__(self):
        self._client = OpenAI()
        self._async_client = AsyncOpenAI()

    def _chat(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass

    @override
    def _structured_chat[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    @override
    async def _achat(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass

    @override
    async def _astructured_chat[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    @override
    def _stream(self, stack: PromptStack, **kwargs) -> Iterator[BaseMessage]:
        pass

    @override
    async def _astream(self, stack: PromptStack, **kwargs) -> AsyncIterator[BaseMessage]:
        pass