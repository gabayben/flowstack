from typing import AsyncIterator, Iterator, override

from flowstack.ai.llm import BaseLLM, BaseStructuredLLM, BaseToolLLM
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptStack

class LiteLLM(BaseLLM, BaseStructuredLLM, BaseToolLLM):
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