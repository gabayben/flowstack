from abc import ABC, abstractmethod
from typing import final

from flowstack.artifacts import Audio, Text, TextLike
from flowstack.core.utils.threading import run_async

class AudioGenerator(ABC):
    @abstractmethod
    def generate(self, inputs: list[TextLike], **kwargs) -> list[Audio]:
        pass

    @abstractmethod
    async def agenerate(self, inputs: list[TextLike], **kwargs) -> list[Audio]:
        pass

class BaseAudioGenerator(AudioGenerator, Audio):
    @final
    def generate(self, inputs: list[TextLike], **kwargs) -> list[Audio]:
        return self._generate([Text.from_text(input) for input in inputs], **kwargs)

    @abstractmethod
    def _generate(self, texts: list[Text], **kwargs) -> list[Audio]:
        pass

    @final
    async def agenerate(self, inputs: list[TextLike], **kwargs) -> list[Audio]:
        return await self._generate([Text.from_text(input) for input in inputs], **kwargs)

    async def _agenerate(self, texts: list[Text], **kwargs) -> list[Audio]:
        return await run_async(self._generate, texts, **kwargs)