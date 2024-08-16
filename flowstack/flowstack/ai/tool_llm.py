from abc import ABC, abstractmethod
from typing import final

from flowstack.core.utils.threading import run_async
from flowstack.prompts import PromptLike, PromptStack
from flowstack.typing import ToolCall

class ToolLLM(ABC):
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