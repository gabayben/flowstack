import logging
from typing import Optional

from wikipedia import wikipedia

from flowstack.artifacts import ArtifactMetadata, Text
from flowstack.loaders.base import BaseArtifactLoader

logger = logging.getLogger(__name__)

class WikipediaLoader(BaseArtifactLoader):
    titles: list[str]
    results: int
    replace_failed: bool

    def __init__(
        self,
        titles: list[str],
        results: Optional[int] = None,
        replace_failed: Optional[bool] = None
    ):
        super().__init__(
            titles=titles,
            results=results or 5,
            replace_failed=replace_failed if replace_failed is not None else True
        )

    def _load(self, **kwargs) -> list[Text]:
        artifacts = []
        for title in self.titles:
            try:
                page = wikipedia.page(title=title)
                artifacts.append(
                    Text(
                        page.content,
                        metadata=ArtifactMetadata(
                            page_id=page.pageid,
                            parent_page_id=page.parent_id,
                            title=page.title,
                            url=page.url
                        )
                    )
                )
                if self.replace_failed and len(artifacts) == self.results:
                    break
            except:
                logger.debug(f"Failed to retrieve page '{title}'.")
        return artifacts