from enum import StrEnum
from typing import Union

from pydantic import StrictFloat, StrictInt, StrictStr

from flowstack.typing import Serializable

class FilterOperator(StrEnum):
    EQ = '=='
    NE = '!='
    GT = '>'
    GTE = '>='
    LT = '<'
    LTE = '<='
    IN = 'in'
    NIN = 'nin'
    ANY = 'any'
    ALL = 'all'
    CONTAINS = 'contains'
    TEXT_MATCH = 'text_match'

class FilterCondition(StrEnum):
    AND = 'and'
    OR = 'or'

class MetadataFilter(Serializable):
    key: str
    value: Union[StrictInt, StrictFloat, StrictStr, list[StrictStr]]
    operator: FilterOperator = FilterOperator.EQ

    def __init__(
        self,
        key: str,
        value: Union[StrictInt, StrictFloat, StrictStr, list[StrictStr]],
        operator: FilterOperator = FilterOperator.EQ
    ):
        super().__init__(
            key=key,
            value=value,
            operator=operator
        )

class MetadataFilters(Serializable):
    filters: list[Union[MetadataFilter, 'MetadataFilters']]
    condition: FilterCondition = FilterCondition.AND

    def __init__(
        self,
        filters: list[Union[MetadataFilter, 'MetadataFilters']],
        condition: FilterCondition = FilterCondition.AND
    ):
        super().__init__(filters=filters, condition=condition)

    def append(self, filters: Union[MetadataFilter, 'MetadataFilters']) -> None:
        self.filters.append(filters)

class MetadataFilterInfo(Serializable):
    name: str
    type: str
    description: str