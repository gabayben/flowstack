from typing import Any

from flowstack.core import ServiceType

class Container:
    def __init__(self):
        self._services: dict[str, Any] = {}

    def add_service[T](self, identifier: ServiceType[T], service: Any) -> None:
        pass

    def get_service[T](self, identifier: ServiceType[T]) -> T:
        pass