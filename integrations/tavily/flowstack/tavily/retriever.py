from flowstack.artifacts import Artifact, ArtifactLike
from flowstack.retrievers.base import BaseRetriever

class TavilyApiRetriever(BaseRetriever):
    def _retrieve(self, query: Artifact, **kwargs) -> list[ArtifactLike]:
        pass