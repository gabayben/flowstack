from abc import ABC, abstractmethod
from typing import final

from flowstack.artifacts import Artifact, ArtifactLike
from flowstack.core.utils.threading import run_async
from flowstack.typing import Serializable

class ArtifactLoader(ABC):
    @abstractmethod
    def load(self, **kwargs) -> list[Artifact]:
        pass

    @abstractmethod
    async def aload(self, **kwargs) -> list[Artifact]:
        pass

class BaseArtifactLoader(Serializable, ArtifactLoader, ABC):
    @final
    def load(self, **kwargs) -> list[Artifact]:
        results = self._load(**kwargs)
        return [Artifact.from_input(result) for result in results]

    @abstractmethod
    def _load(self, **kwargs) -> list[ArtifactLike]:
        pass

    @final
    async def aload(self, **kwargs) -> list[Artifact]:
        results = await self._aload(**kwargs)
        return [Artifact.from_input(result) for result in results]

    async def _aload(self, **kwargs) -> list[ArtifactLike]:
        return await run_async(self._load, **kwargs)