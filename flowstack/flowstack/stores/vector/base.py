from abc import ABC, abstractmethod
from typing import Optional, Unpack

from flowstack.artifacts import Artifact
from flowstack.stores import VectorStoreQuery, VectorStoreQueryResult
from flowstack.typing import MetadataFilters
from flowstack.utils.threading import run_async

class VectorStore(ABC):
    @abstractmethod
    def retrieve(self, **query: Unpack[VectorStoreQuery]) -> VectorStoreQueryResult:
        pass

    async def aretrieve(self, **query: Unpack[VectorStoreQuery]) -> VectorStoreQueryResult:
        return await run_async(self.retrieve, **query)

    @abstractmethod
    def insert(self, artifacts: list[Artifact], **kwargs) -> list[str]:
        pass

    async def ainsert(self, artifacts: list[Artifact], **kwargs) -> list[str]:
        return await run_async(self.insert, artifacts, **kwargs)

    @abstractmethod
    def delete(
        self,
        artifact_ids: Optional[list[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **kwargs
    ) -> None:
        pass

    async def adelete(
        self,
        artifact_ids: Optional[list[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **kwargs
    ) -> None:
        await run_async(
            self.delete,
            artifact_ids=artifact_ids,
            filters=filters,
            **kwargs
        )

    @abstractmethod
    def delete_refs(self, ref_ids: list[str], **kwargs) -> None:
        pass

    async def adelete_refs(self, ref_ids: list[str], **kwargs) -> None:
        await run_async(self.delete_refs, ref_ids, **kwargs)

    @abstractmethod
    def clear(self, **kwargs) -> None:
        pass

    async def aclear(self, **kwargs) -> None:
        await run_async(self.clear, **kwargs)