from abc import ABC, abstractmethod
from typing import Callable, Generic, Literal, Optional, Protocol, TypeVar, Union

from pydantic import BaseModel, Field

from flowstack.core import Action, ServiceType

_Data = TypeVar('_Data')

class WorkflowContext(Generic[_Data], ABC):
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

class SyncAction[D](Protocol):
    def __call__(self, context: WorkflowContext[D], **kwargs) -> None:
        pass

class AsyncAction[D](Protocol):
    async def __call__(self, context: WorkflowContext[D], **kwargs) -> None:
        pass

type Action[D] = Union[SyncAction[D], AsyncAction[D]]
Action = Action
type Actions[D] = Union[Action[D], list[Action[D]]]
Actions = Actions

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
    enter: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    exit: Optional[Actions[_Data]] = Field(default=None, exclude=True)
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
    source: str
    target: Union[str, list[str]]
    before: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    after: Optional[AfterTransition[_Data]] = Field(default=None, exclude=True)
    guards: Optional[Guards[_Data]] = Field(default=None, exclude=True)

    def __init__(
        self,
        trigger: str,
        source: str,
        target: str,
        before: Optional[Action[_Data]] = None,
        after: Optional[AfterTransition[_Data]] = None,
        guards: Optional[Guards[_Data]] = None
    ):
        super().__init__(
            trigger=trigger,
            source=source,
            target=target,
            before=before,
            after=after,
            guards=guards
        )

class TransitionProps(BaseModel, Generic[_Data]):
    trigger: str
    source: str
    target: Union[str, list[str]]
    before: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    after: Optional[Actions[_Data]] = Field(default=None, exclude=True)
    guards: Optional[Guards[_Data]] = Field(default=None, exclude=True)

    def __init__(
        self,
        trigger: str,
        source: str,
        target: Union[str, list[str]],
        before: Optional[Actions[_Data]] = None,
        after: Optional[Actions[_Data]] = None,
        guards: Optional[Guards[_Data]] = None
    ):
        super().__init__(
            trigger=trigger,
            source=source,
            target=target,
            before=before,
            after=after,
            guards=guards
        )