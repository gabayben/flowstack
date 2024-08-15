import wikipedia

from flowstack.artifacts import Artifact, ArtifactLike
from flowstack.retrievers.base import BaseRetriever
from flowstack.wikipedia import WikipediaLoader

class WikipediaRetriever(BaseRetriever):
    results: int
    replace_failed: bool

    def __init__(
        self,
        results: int = 5,
        replace_failed: bool = True,
        **kwargs
    ):
        super().__init__(
            results=results,
            replace_failed=replace_failed,
            **kwargs
        )

    def _retrieve(self, query: Artifact, **kwargs) -> list[ArtifactLike]:
        titles = wikipedia.search(
            str(query),
            self.results if not self.replace_failed else self.results + 5
        )
        return WikipediaLoader(
            titles,
            results=self.results,
            replace_failed=self.replace_failed
        ).load(**kwargs)