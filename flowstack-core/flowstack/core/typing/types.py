import enum
from typing import Literal, TypeVar

_T = TypeVar('_T')

class SchemaType(enum.StrEnum):
    PYDANTIC = 'pydantic'
    TYPED_DICT = 'typed_dict'
    NAMED_TUPLE = 'named_tuple'
    VALUE = 'value'

CallableType = Literal['sync', 'async']