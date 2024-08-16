from abc import ABC, abstractmethod
from typing import final, override

from flowstack.ai import LLM
from flowstack.core.utils.threading import run_async
from flowstack.prompts import PromptLike, PromptStack
from flowstack.typing import ToolCall

class ToolLLM(ABC):
    @classmethod
    def from_llm(cls, llm: LLM) -> 'ToolLLM':
        if isinstance(llm, ToolLLM):
            return llm
        return _DelegateToolLLM(llm)

    @abstractmethod
    def get_tool_calls(self, input: PromptLike, **kwargs) -> list[ToolCall]:
        pass

    @abstractmethod
    async def aget_tool_calls(self, input: PromptLike, **kwargs) -> list[ToolCall]:
        pass

class BaseToolLLM(ToolLLM, ABC):
    @final
    def get_tool_calls(self, input: PromptLike, **kwargs) -> list[ToolCall]:
        return self._get_tool_calls(PromptStack(input), **kwargs)

    @abstractmethod
    def _get_tool_calls(self, stack: PromptStack, **kwargs) -> list[ToolCall]:
        pass

    @final
    async def aget_tool_calls(self, input: PromptLike, **kwargs) -> list[ToolCall]:
        return await self._aget_tool_calls(PromptStack(input), **kwargs)

    async def _aget_tool_calls(self, stack: PromptStack, **kwargs) -> list[ToolCall]:
        return await run_async(self._get_tool_calls, stack, **kwargs)

class _DelegateToolLLM(BaseToolLLM):
    def __init__(self, llm: LLM):
        self._llm = llm

    def _get_tool_calls(self, stack: PromptStack, **kwargs) -> list[ToolCall]:
        pass

    @override
    async def _aget_tool_calls(self, stack: PromptStack, **kwargs) -> list[ToolCall]:
        pass