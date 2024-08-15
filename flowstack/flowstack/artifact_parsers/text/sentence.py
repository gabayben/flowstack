from dataclasses import dataclass
from typing import Callable, Optional

from pydantic import Field, PrivateAttr

from flowstack.artifact_parsers.base import BaseTextSplitter
from flowstack.artifact_parsers.text.utils import (
    split_by_char_fn,
    split_by_regex_fn,
    split_by_sentence_tokenizer,
    split_by_sep_fn
)
from flowstack.artifact_parsers.utils import default_id_func
from flowstack.artifacts import GetArtifactId, Text, TextLike
from flowstack.core.utils.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from flowstack.core.utils.string import SplitFunction, get_tokenizer

SENTENCE_CHUNK_OVERLAP = 200
CHUNKING_REGEX = "[^,.;。？！]+[,.;。？！]?"
DEFAULT_PARAGRAPH_SEP = "\n\n\n"

@dataclass
class _Split:
    text: str
    token_size: int
    is_sentence: bool

class SentenceSplitter(BaseTextSplitter):
    seperator: str = Field(default=' ')
    chunk_size: int = Field(default=DEFAULT_CHUNK_SIZE, gt=0)
    chunk_overlap: int = Field(default=DEFAULT_CHUNK_OVERLAP, gt=0)
    paragraph_seperator: str = Field(default=DEFAULT_PARAGRAPH_SEP)
    secondary_chunking_regex: str = Field(default=CHUNKING_REGEX)

    _tokenizer: Callable[[str], list[int]] = PrivateAttr()
    _chunking_tokenizer_fn: SplitFunction = PrivateAttr()
    _split_fns: list[SplitFunction] = PrivateAttr()
    _sub_sentence_split_fns: list[SplitFunction] = PrivateAttr()

    def __init__(
        self,
        seperator: str = ' ',
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        paragraph_seperator: str = DEFAULT_PARAGRAPH_SEP,
        secondary_chunking_regex=CHUNKING_REGEX,
        tokenizer: Optional[Callable[[str], list[int]]] = None,
        chunking_tokenizer_fn: Optional[SplitFunction] = None,
        split_fns: Optional[list[SplitFunction]] = None,
        sub_sentence_split_fns: Optional[list[SplitFunction]] = None,
        id_func: Optional[GetArtifactId] = None,
        include_prev_next_rel: bool = True,
        include_metadata: bool = True
    ):
        super().__init__(
            seperator=seperator,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_seperator=paragraph_seperator,
            secondary_chunking_regex=secondary_chunking_regex,
            id_func=id_func or default_id_func,
            include_prev_next_rel=include_prev_next_rel,
            include_metadata=include_metadata
        )
        self._tokenizer = tokenizer or get_tokenizer()
        self._chunking_tokenizer_fn = chunking_tokenizer_fn or split_by_sentence_tokenizer()
        self._split_fns = split_fns or [
            split_by_sep_fn(paragraph_seperator),
            self._chunking_tokenizer_fn
        ]
        self._sub_sentence_split_fns = sub_sentence_split_fns or [
            split_by_regex_fn(secondary_chunking_regex),
            split_by_sep_fn(seperator),
            split_by_char_fn()
        ]

    def _split_text(self, text: Text, **kwargs) -> list[TextLike]:
        splits = self._split(text, self.chunk_size)
        return self._merge(splits, self.chunk_size)

    def _merge(self, splits: list[_Split], chunk_size: int) -> list[str]:
        chunks: list[str] = []
        current_chunk: list[tuple[str, int]] = []
        last_chunk: list[tuple[str, int]] = []
        current_chunk_length = 0
        new_chunk = True

        def close_chunk() -> None:
            nonlocal chunks, current_chunk, last_chunk, current_chunk_length, new_chunk
            chunks.append(''.join(text for text, _ in current_chunk))
            last_chunk = current_chunk
            current_chunk = []
            current_chunk_length = 0
            new_chunk = True
            if len(last_chunk) > 0:
                last_index = len(last_chunk) - 1
                while (
                    last_index >= 0 and
                    current_chunk_length + last_chunk[last_index][1] <= self.chunk_overlap
                ):
                    text, length = last_chunk[last_index]
                    current_chunk_length += length
                    current_chunk.insert(0, (text, length))
                    last_index -= 1

        while len(splits) > 0:
            current_split = splits[0]
            if current_split.token_size > chunk_size:
                raise ValueError(f'Current split exceeded chunk size.')
            if current_split.token_size + current_chunk_length > chunk_size and not new_chunk:
                # if adding split to current chunk exceeds chunk size: close out chunk
                close_chunk()
            else:
                if (
                    current_split.is_sentence or
                    current_split.token_size + current_chunk_length <= chunk_size or
                    new_chunk  # new chunk, always add at least one split
                ):
                    # add split to chunk
                    current_chunk_length += current_split.token_size
                    current_chunk.append((current_split.text, current_split.token_size))
                    splits.pop(0)
                    new_chunk = False
                else:
                    # close out chunk
                    close_chunk()

        # handle the last chunk
        if not new_chunk:
            chunks.append(''.join(text for text, _ in current_chunk))

        return self._postprocess_chunks(chunks)

    def _get_splits(self, text: str) -> tuple[list[str], bool]:
        for split_fn in self._split_fns:
            splits = split_fn(text)
            if len(splits) > 1:
                return splits, True
        for split_fn in self._sub_sentence_split_fns:
            splits = split_fn(text)
            if len(splits) > 1:
                break
        return splits, False

    def _postprocess_chunks(self, chunks: list[str]) -> list[str]:
        new_chunks = []
        for chunk in chunks:
            new_chunk = chunk.strip()
            if new_chunk != '':
                new_chunks.append(new_chunk)
        return new_chunks

    def _token_size(self, text: str) -> int:
        return len(self._tokenizer(text))