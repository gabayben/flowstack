from typing import AsyncIterator, Iterator, Optional, override

from openai import AsyncOpenAI, OpenAI

from flowstack.ai.llm import BaseLLM, BaseStructuredLLM, BaseToolLLM
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptStack

class OpenAILLM(BaseLLM, BaseStructuredLLM, BaseToolLLM):
    _client: OpenAI
    _async_client: AsyncOpenAI

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        async_client: Optional[AsyncOpenAI] = None
    ):
        self._client = client or OpenAI()
        self._async_client = async_client or AsyncOpenAI()

    def _generate(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass

    @override
    async def _agenerate(self, stack: PromptStack, **kwargs) -> BaseMessage:
        pass

    @override
    def _stream(self, stack: PromptStack, **kwargs) -> Iterator[BaseMessage]:
        pass

    @override
    async def _astream(self, stack: PromptStack, **kwargs) -> AsyncIterator[BaseMessage]:
        pass