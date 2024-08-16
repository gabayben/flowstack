from typing import override

from flowstack.ai.embedder import BaseEmbedder
from flowstack.artifacts import Artifact

class CohereEmbedder(BaseEmbedder):
    def _embed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        pass

    @override
    async def _aembed(self, artifacts: list[Artifact], **kwargs) -> list[Artifact]:
        pass