import logging
import sys
from typing import Any, Optional

from flowstack.artifacts import Artifact
from flowstack.milvus import MilvusSparseEmbeddingFunction, ScalarMetadataFilters
from flowstack.typing import FilterOperator, MetadataFilters

logger = logging.getLogger(__name__)

class BGEM3SparseEmbeddingFunction(MilvusSparseEmbeddingFunction):
    def __init__(self):
        try:
            from FlagEmbedding import BGEM3FlagModel
            self._model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)
        except Exception as ImportError:
            error_info = (
                "Error occured while initializing the default sparse embedding function."
                "Cannot import BGEM3FlagModel from FlagEmbedding. It seems it is not installed. "
                "Please install it using:\n"
                "pip install FlagEmbedding\n"
            )
            logger.fatal(error_info)
            sys.exit(1)

    def encode_queries(self, queries: list[Artifact]) -> list[dict[int, float]]:
        return self._encode(queries)

    def encode_documents(self, documents: list[Artifact]) -> list[dict[int, float]]:
        return self._encode(documents)

    def _encode(self, artifacts: list[Artifact]) -> list[dict[int, float]]:
        outputs = self._model.encode(
            [str(artifact) for artifact in artifacts],
            return_dense=False,
            return_sparse=True,
            return_colbert_vecs=False
        )['lexical_weights']
        result = {}
        for key in outputs:
            result[int(key)] = outputs[key]
        return [result]

def get_default_sparse_embedding_function() -> MilvusSparseEmbeddingFunction:
    return BGEM3SparseEmbeddingFunction()

def to_milvus_filter(
    filters: MetadataFilters,
    scalar_filters: Optional[ScalarMetadataFilters] = None
) -> str:
    standard_filters_list, standard_filter = _parse_standard_filters(filters)
    scalar_filters_list, scalar_filter = _parse_scalar_filters(scalar_filters)
    parsed_filters = standard_filters_list + scalar_filters_list
    if len(standard_filters_list) > 0 and len(scalar_filters_list) > 0:
        joined_filter = f' {standard_filter} and {scalar_filter} '
        return f'({joined_filter})' if len(parsed_filters) > 1 else joined_filter
    elif len(standard_filters_list) > 0 and len(scalar_filters_list) == 0:
        return f'({standard_filter})' if len(standard_filters_list) > 1 else standard_filter
    elif len(standard_filters_list) == 0 and len(scalar_filters_list) > 0:
        return f'({scalar_filter})' if len(scalar_filters_list) > 1 else scalar_filter
    return ''

def _parse_standard_filters(filters: MetadataFilters) -> tuple[list[str], str]:
    parsed_filters = []
    if filters is None or filters.filters is None:
        return [], ''

    for filter in filters.filters:
        filter_value = _parse_filter_value(filter.value)
        if filter_value is None:
            continue

        if filter.operator == FilterOperator.NIN:
            parsed_filters.append(f'{filter.key!s} not in {filter_value}')
        elif filter.operator == FilterOperator.CONTAINS:
            parsed_filters.append(f'array_contains({filter.key!s}, {filter_value})')
        elif filter.operator == FilterOperator.ANY:
            parsed_filters.append(f'array_contains_any({filter.key!s}, {filter_value})')
        elif filter.operator == FilterOperator.ALL:
            parsed_filters.append(f'array_contains_all({filter.key!s}, {filter_value})')
        elif filter.operator == FilterOperator.TEXT_MATCH:
            parsed_filters.append(f'{filter.key!s} like {_parse_filter_value(filter.value, True)}')
        elif filter.operator in [
            FilterOperator.EQ,
            FilterOperator.NE,
            FilterOperator.GT,
            FilterOperator.GTE,
            FilterOperator.LT,
            FilterOperator.LTE,
            FilterOperator.IN
        ]:
            parsed_filters.append(f'{filter.key!s} {filter.operator.value} {filter_value}')
        else:
            raise ValueError(
                f'Filter operator {filter.operator} ("{filter.operator.value}") is not supported by Milvus.'
            )

        return parsed_filters, f' {filters.condition.value} '.join(parsed_filters)

def _parse_scalar_filters(filters: ScalarMetadataFilters) -> tuple[list[str], str]:
    parsed_filters = []
    if filters is None:
        return [], ''
    for filter in filters.filters:
        filter_value = _parse_filter_value(filter.value)
        if filter_value is None:
            continue
        parsed_filters.append(
            filter.operator.value.format(key=filter.key, value=filter_value)
        )
    return parsed_filters, f' {filters.condition.value} '.join(parsed_filters)

def _parse_filter_value(value: Optional[Any], is_text_match: bool = False) -> Optional[str]:
    if value is None:
        return None
    if is_text_match:
        return f"'{value!s}%'"
    return f"'{value!s}'" if isinstance(value, str) else str(value)