from typing import AsyncIterator, Iterator, Optional, Type, override

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from flowstack.ai.llm import BaseLLM
from flowstack.ai.structured_llm import BaseStructuredLLM
from flowstack.ai.tool_llm import BaseToolLLM
from flowstack.messages import BaseMessage
from flowstack.prompts import PromptStack
from flowstack.typing import ToolCall

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

    def _structured[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    @override
    async def _astructured[T: BaseModel](
        self,
        stack: PromptStack,
        output_type: Type[T],
        **kwargs
    ) -> T:
        pass

    def _get_tool_calls(self, stack: PromptStack, **kwargs) -> list[ToolCall]:
        pass

    @override
    async def _aget_tool_calls(self, stack: PromptStack, **kwargs) -> list[ToolCall]:
        pass