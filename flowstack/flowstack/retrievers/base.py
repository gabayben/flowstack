from abc import ABC, abstractmethod
from typing import final

from flowstack.artifacts import Artifact, ArtifactLike
from flowstack.core.utils.threading import run_async

class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: ArtifactLike, **kwargs) -> list[Artifact]:
        pass

    @abstractmethod
    async def aretrieve(self, query: ArtifactLike, **kwargs) -> list[Artifact]:
        pass

class BaseRetriever(Retriever, ABC):
    @final
    def retrieve(self, query: ArtifactLike, **kwargs) -> list[Artifact]:
        results = self._retrieve(Artifact.from_input(query), **kwargs)
        return [Artifact.from_input(result) for result in results]

    @abstractmethod
    def _retrieve(self, query: Artifact, **kwargs) -> list[ArtifactLike]:
        pass

    @final
    async def aretrieve(self, query: ArtifactLike, **kwargs) -> list[Artifact]:
        results = await self._aretrieve(Artifact.from_input(query), **kwargs)
        return [Artifact.from_input(result) for result in results]

    async def _aretrieve(self, query: Artifact, **kwargs) -> list[ArtifactLike]:
        return await run_async(self._retrieve, query, **kwargs)