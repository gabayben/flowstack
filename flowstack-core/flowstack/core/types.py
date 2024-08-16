from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Generic, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from flowstack.core import ServiceType

_Data = TypeVar('_Data')

class MachineContext(Generic[_Data], ABC):
    @property
    @abstractmethod
    def data(self) -> _Data:
        pass

    @abstractmethod
    def get_service[T](self, identifier: ServiceType[T]) -> T:
        pass

    @abstractmethod
    def change_state(self, state: str, **kwargs) -> None:
        pass

    @abstractmethod
    async def achange_state(self, state: str, **kwargs) -> None:
        pass

    @abstractmethod
    def next_state(self, **kwargs) -> None:
        pass

    @abstractmethod
    async def anext_state(self, **kwargs) -> None:
        pass

    @abstractmethod
    def trigger(self, event: str, **kwargs) -> None:
        pass

    @abstractmethod
    async def atrigger(self, event: str, **kwargs) -> None:
        pass

    @abstractmethod
    def update_data(self, data: _Data) -> None:
        pass

SyncAction = Callable[[MachineContext[_Data], ...], None]
AsyncAction = Callable[[MachineContext[_Data], ...], Awaitable[None]]
Action = Union[SyncAction[_Data], AsyncAction[_Data]]
Actions = Union[Action[_Data], list[Action[_Data]]]

_Guard = Callable[[_Data], bool]
Guards = Union[_Guard[_Data], list[_Guard[_Data]]]

type AfterTransition[D] = Union[
    str,
    Action[D],
    list[Union[str, Action[D]]],
    Literal[True]
]
AfterTransition = AfterTransition

class StateOptions(BaseModel, Generic[_Data]):
    name: str
    enter: Optional[Actions[_Data]] = Field(default=None)
    exit: Optional[Actions[_Data]] = Field(default=None)
    auto_exit: bool = False
    final: bool = False

    def __init__(
        self,
        name: str,
        enter: Optional[Action[_Data]] = None,
        exit: Optional[Action[_Data]] = None,
        final: bool = False,
        **kwargs
    ):
        super().__init__(
            name=name,
            enter=enter,
            exit=exit,
            final=final,
            **kwargs
        )

class TransitionOptions(BaseModel, Generic[_Data]):
    trigger: str
    source: Union[str, list[str]]
    target: Optional[str]
    before: Optional[Actions[_Data]] = Field(default=None)
    after: Optional[AfterTransition[_Data]] = Field(default=None)
    prepare: Optional[Actions[_Data]] = Field(default=None)
    guards: Optional[Guards[_Data]] = Field(default=None)

    def __init__(
        self,
        trigger: str,
        source: Union[str, list[str]],
        target: Optional[str],
        before: Optional[Action[_Data]] = None,
        after: Optional[AfterTransition[_Data]] = None,
        prepare: Optional[Actions[_Data]] = None,
        guards: Optional[Guards[_Data]] = None
    ):
        super().__init__(
            trigger=trigger,
            source=source,
            target=target,
            before=before,
            after=after,
            prepare=prepare,
            guards=guards
        )

class TransitionProps(BaseModel, Generic[_Data]):
    trigger: str
    source: Union[str, list[str]]
    target: Optional[str]
    before: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    after: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    prepare: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    guards: Optional[Guards[_Data]] = Field(default=None, exclude=True)

    def __init__(
        self,
        trigger: str,
        source: Union[str, list[str]],
        target: Optional[str],
        before: Optional[Actions[_Data]] = None,
        after: Optional[Actions[_Data]] = None,
        prepare: Optional[Actions[_Data]] = None,
        guards: Optional[Guards[_Data]] = None
    ):
        super().__init__(
            trigger=trigger,
            source=source,
            target=target,
            before=before,
            after=after,
            prepare=prepare,
            guards=guards
        )