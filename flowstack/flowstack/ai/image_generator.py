from abc import ABC, abstractmethod
from typing import final

from flowstack.artifacts import Image
from flowstack.core.utils.threading import run_async
from flowstack.prompts import ImagePrompt, ImagePromptLike

class ImageGenerator(ABC):
    @abstractmethod
    def generate(self, prompts: list[ImagePromptLike], **kwargs) -> list[Image]:
        pass

    @abstractmethod
    async def agenerate(self, prompts: list[ImagePromptLike], **kwargs) -> list[Image]:
        pass

class BaseImageGenerator(ImageGenerator, ABC):
    @final
    def generate(self, prompts: list[ImagePromptLike], **kwargs) -> list[Image]:
        return self._generate([ImagePrompt(prompt) for prompt in prompts], **kwargs)

    @abstractmethod
    def _generate(self, prompts: list[ImagePrompt], **kwargs) -> list[Image]:
        pass

    @final
    async def agenerate(self, prompts: list[ImagePromptLike], **kwargs) -> list[Image]:
        return await self._agenerate([ImagePrompt(prompt) for prompt in prompts], **kwargs)

    async def _agenerate(self, prompts: list[ImagePrompt], **kwargs) -> list[Image]:
        return await run_async(self._generate, prompts, **kwargs)