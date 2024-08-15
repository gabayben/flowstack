from dataclasses import dataclass
from typing import Type, Union

@dataclass
class TypedKey[T]:
    name: str

type ServiceType[T] = Union[Type[T], TypedKey[T]]
ServiceType = ServiceType