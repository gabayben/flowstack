import logging
from typing import Optional, Union
import uuid

from flowstack.artifacts import Artifact, ArtifactMetadata, GetArtifactId, Text
from flowstack.core.utils.string import truncate_text

logger = logging.getLogger(__name__)

SplitText = Union[str, tuple[str, ArtifactMetadata]]

def default_id_func(idx: int, artifact: Artifact) -> str:
    return str(uuid.uuid4())

def build_artifacts_from_splits(
    splits: list[SplitText],
    artifact: Artifact,
    ref_artifact: Optional[Artifact] = None,
    id_func: Optional[GetArtifactId] = None
) -> list[Artifact]:
    ref_artifact = ref_artifact or artifact
    id_func = id_func or default_id_func
    artifacts: list[Artifact] = []
    for i, split in enumerate(splits):
        text = split if isinstance(split, str) else split[0]
        logger.debug(f'> Adding chunk: {truncate_text(text, 50)}')
        split_artifact = Text(text, metadata=artifact.metadata.relational_copy())
        split_artifact.ref = ref_artifact.as_info()
        artifacts.append(split_artifact)
    return artifacts