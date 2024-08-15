from abc import ABC, abstractmethod
from typing import Optional, Union, final, override

from pydantic import Field

from flowstack.artifact_parsers.utils import build_artifacts_from_splits
from flowstack.artifacts import Artifact, ArtifactLike, ArtifactMetadata, GetArtifactId, Text, TextLike
from flowstack.core.utils.threading import run_async
from flowstack.typing import Serializable

class ArtifactParser(ABC):
    @property
    @abstractmethod
    def is_text(self) -> bool:
        pass

    @abstractmethod
    def parse(self, inputs: list[ArtifactLike], **kwargs) -> list[Artifact]:
        pass

    @abstractmethod
    async def aparse(self, inputs: list[ArtifactLike], **kwargs) -> list[Artifact]:
        pass

class BaseArtifactParser(Serializable, ArtifactParser, ABC):
    id_func: Optional[GetArtifactId] = Field(default=None, exclude=True)
    include_prev_next: bool = True
    include_metadata: bool = True

    def __init__(
        self,
        id_func: Optional[GetArtifactId] = None,
        include_prev_next: bool = True,
        include_metadata: bool = True,
        **kwargs
    ):
        super().__init__(
            id_func=id_func,
            include_prev_next=include_prev_next,
            include_metadata=include_metadata,
            **kwargs
        )

    @final
    def parse(self, inputs: list[ArtifactLike], **kwargs) -> list[Artifact]:
        artifacts = [Artifact.from_input(input) for input in inputs]
        ref_map = {artifact.id: artifact for artifact in artifacts}
        artifacts = self._parse(artifacts, **kwargs)
        return self._postprocess_artifacts(artifacts, ref_map)

    @abstractmethod
    def _parse(self, artifacts: list[Artifact], **kwargs) -> list[ArtifactLike]:
        pass

    @final
    async def aparse(self, inputs: list[ArtifactLike], **kwargs) -> list[Artifact]:
        artifacts = [Artifact.from_input(input) for input in inputs]
        ref_map = {artifact.id: artifact for artifact in artifacts}
        artifacts = await self._aparse(artifacts, **kwargs)
        return self._postprocess_artifacts(artifacts, ref_map)

    async def _aparse(self, artifacts: list[Artifact], **kwargs) -> list[ArtifactLike]:
        return await run_async(self._parse, artifacts, **kwargs)

    def _postprocess_artifacts(
        self,
        artifacts: list[Artifact],
        ref_map: dict[str, Artifact]
    ) -> list[Artifact]:
        num_artifacts = len(artifacts)

        for i, artifact in enumerate(artifacts):
            ref = ref_map.get(artifact.ref_id)
            if ref:
                if ref.ref is not None:
                    artifact.ref = ref.ref

                # update start/end char idx
                if self.is_text:
                    artifact_text = str(artifact)
                    start_char_idx = str(ref).find(artifact_text)
                    if start_char_idx >= 0:
                        artifact.metadata.start_char_idx = start_char_idx
                        artifact.metadata.end_char_idx = start_char_idx + len(artifact_text)

                # update metadata
                if self.include_metadata:
                    artifact.metadata.update(ref.metadata.relational_copy())

            # establish previous/next relationships if artifacts share the same parent
            if self.include_prev_next:
                if (
                    i > 0 and
                    artifacts[i - 1].ref and
                    artifacts[i - 1].ref_id == artifact.ref_id
                ):
                    artifact.previous = artifacts[i - 1].as_info()
                if (
                    i < num_artifacts - 1 and
                    artifacts[i + 1].ref and
                    artifacts[i + 1].ref_id == artifact.ref_id
                ):
                    artifact.next = artifacts[i + 1].as_info()

        return artifacts

SplitText = Union[str, tuple[str, ArtifactMetadata]]

class BaseTextSplitter(BaseArtifactParser, ABC):
    @property
    def is_text(self) -> bool:
        return True

    @final
    def _parse(self, artifacts: list[Artifact], **kwargs) -> list[ArtifactLike]:
        chunks: list[Artifact] = []
        for artifact in artifacts:
            chunks.extend(
                build_artifacts_from_splits(
                    self._split_text(Text.from_text(artifact), **kwargs),
                    artifact,
                    id_func=self.id_func
                )
            )
        return chunks

    @abstractmethod
    def _split_text(self, text: Text, **kwargs) -> list[TextLike]:
        pass

    @final
    @override
    async def _aparse(self, artifacts: list[Artifact], **kwargs) -> list[ArtifactLike]:
        chunks: list[Artifact] = []
        for artifact in artifacts:
            chunks.extend(
                build_artifacts_from_splits(
                    await self._asplit_text(Text.from_text(artifact), **kwargs),
                    artifact,
                    id_func=self.id_func
                )
            )
        return chunks

    async def _asplit_text(self, text: Text, **kwargs) -> list[TextLike]:
        return await run_async(self._split_text, text, **kwargs)