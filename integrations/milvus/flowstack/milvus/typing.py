from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Union

from openai import BaseModel
from pydantic import StrictFloat, StrictInt, StrictStr

from flowstack.artifacts import Artifact
from flowstack.typing import FilterCondition

ScalarMetadataFilterValue = Union[
    StrictInt,
    list[StrictInt],
    StrictFloat,
    list[StrictFloat],
    StrictStr,
    list[StrictStr]
]

class MilvusFilterOperator(StrEnum):
    ARRAY_CONTAINS = "ARRAY_CONTAINS({key}, {value})"  # array contains single value
    NARRAY_CONTAINS = (
        "not ARRAY_CONTAINS({key}, {value})"  # array does not contain single value
    )
    ARRAY_CONTAINS_ANY = (
        "ARRAY_CONTAINS_ANY({key}, {value})"  # array contains any value in the list
    )
    NARRAY_CONTAINS_ANY = "not ARRAY_CONTAINS_ANY({key}, {value})"  # array does not contain any value in the list
    ARRAY_CONTAINS_ALL = (
        "ARRAY_CONTAINS_ALL({key}, {value})"  # array contains all values in the list
    )
    NARRAY_CONTAINS_ALL = "not ARRAY_CONTAINS_ALL({key}, {value})"  # array does not contain all values in the list
    # GT, GTE, LT, LTE not yet supported on ARRAY_LENGTH functions
    ARRAY_LENGTH = "ARRAY_LENGTH({key}) == {value}"  # array length equals value
    NARRAY_LENGTH = "ARRAY_LENGTH({key}) != {value}"  # array length not equals value

class ScalarMetadataFilter(BaseModel):
    key: str
    value: ScalarMetadataFilterValue
    operator: MilvusFilterOperator = MilvusFilterOperator.ARRAY_CONTAINS

    def __init__(
        self,
        key: str,
        value: ScalarMetadataFilterValue,
        operator: MilvusFilterOperator = MilvusFilterOperator.ARRAY_CONTAINS
    ):
        super().__init__(
            key=key,
            value=value,
            operator=operator
        )

class ScalarMetadataFilters(BaseModel):
    filters: list[ScalarMetadataFilter]
    condition: FilterCondition = FilterCondition.AND

    def __init__(
        self,
        filters: list[ScalarMetadataFilter],
        condition: FilterCondition = FilterCondition.AND
    ):
        super().__init__(filters=filters, condition=condition)

    def append(self, filter: ScalarMetadataFilter) -> None:
        self.filters.append(filter)

class MilvusSparseEmbeddingFunction(ABC):
    @abstractmethod
    def encode_queries(self, queries: list[Artifact]) -> list[dict[int, float]]:
        pass

    @abstractmethod
    def encode_documents(self, documents: list[Artifact]) -> list[dict[int, float]]:
        pass