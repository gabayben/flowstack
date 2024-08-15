from abc import ABC, abstractmethod
from typing import Any, NamedTuple, final

from flowstack.artifacts import Audio, BlobLike
from flowstack.core.utils.threading import run_async

class AudioTranscription(NamedTuple):
    text: str
    metadata: dict[str, Any] = {}

class AudioTranscriber(ABC):
    @abstractmethod
    def transcribe(self, inputs: list[BlobLike], **kwargs) -> list[AudioTranscription]:
        pass

    @abstractmethod
    async def atranscribe(self, inputs: list[BlobLike], **kwargs) -> list[AudioTranscription]:
        pass

class BaseAudioTranscriber(AudioTranscriber, ABC):
    @final
    def transcribe(self, inputs: list[BlobLike], **kwargs) -> list[AudioTranscription]:
        return self._transcribe([Audio.from_blob(input) for input in inputs], **kwargs)

    @abstractmethod
    def _transcribe(self, audios: list[Audio], **kwargs) -> list[AudioTranscription]:
        pass

    @final
    async def atranscribe(self, inputs: list[BlobLike], **kwargs) -> list[AudioTranscription]:
        return await self._atranscribe([Audio.from_blob(input) for input in inputs], **kwargs)

    async def _atranscribe(self, audios: list[Audio], **kwargs) -> list[AudioTranscription]:
        return await run_async(self._transcribe, audios, **kwargs)