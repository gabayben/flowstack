import inspect
from typing import Any, Callable, Optional, Type, TypeVar, Generic, Union, Unpack

from pydantic import BaseModel, ConfigDict
from transitions import Machine

from flowstack.core import (
    Action,
    Actions,
    AfterTransition,
    Container,
    ServiceType,
    StateOptions,
    TransitionOptions,
    TransitionProps,
    MachineContext
)
from flowstack.core.actions import next_state, trigger_transition
from flowstack.core.utils.threading import run_async, run_sync

_Data = TypeVar('_Data')
_MachineActions = Union[Callable, list[Callable]]
_MachineGuards = Union[Callable[..., bool], list[Callable[..., bool]]]

class _Model:
    pass

class _ContextImpl(MachineContext[_Data]):
    @property
    def data(self) -> _Data:
        return self._machine.data

    def __init__(self, machine: 'StateMachine[_Data]'):
        self._machine = machine

    def get_service[T](self, identifier: ServiceType[T]) -> T:
        return self._machine.get_service(identifier)

    def change_state(self, state: str, **kwargs) -> None:
        self._machine.change_state(state, **kwargs)

    async def achange_state(self, state: str, **kwargs) -> None:
        await self._machine.achange_state(state, **kwargs)

    def next_state(self, **kwargs) -> None:
        self._machine.next_state(**kwargs)

    async def anext_state(self, **kwargs) -> None:
        await self._machine.anext_state(**kwargs)

    def trigger(self, event: str, **kwargs) -> None:
        self._machine.trigger(event, **kwargs)

    async def atrigger(self, event: str, **kwargs) -> None:
        await self._machine.atrigger(event, **kwargs)

    def update_data(self, data: _Data) -> None:
        self._machine.update_data(data)

class StateMachine(BaseModel, Generic[_Data]):
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )

    @property
    def SchemaType(self) -> Type[_Data]:
        return self._schema

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def data(self) -> Optional[_Data]:
        return self._data

    @property
    def _context(self) -> MachineContext[_Data]:
        return _ContextImpl(self)

    def __init__(
        self,
        schema: Type[_Data],
        initial_state: Optional[str] = None,
        initial_data: Optional[_Data] = None,
        states: dict[str, StateOptions[_Data]] = {},
        transitions: dict[str, TransitionOptions[_Data]] = {}
    ):
        self._container = Container()
        self._model = _Model()
        self._machine = Machine(model=self._model, queued=True)
        self._schema = schema
        self._state = initial_state
        self._data = initial_data
        self._states: dict[str, StateOptions] = {}
        self.add_states(states)
        self._transitions: dict[str, TransitionProps[_Data]] = {}
        self.add_transitions(transitions)

    # Services

    def add_service[T](self, identifier: ServiceType[T], service: Any) -> None:
        self._container.add_service(identifier, service)

    def get_service[T](self, identifier: ServiceType[T]) -> T:
        return self._container.get_service(identifier)

    # Definitions

    def add_states(self, states: dict[str, StateOptions[_Data]]) -> None:
        for options in states.values():
            self.add_state(**options)

    def add_state(self, **kwargs: Unpack[StateOptions[_Data]]) -> None:
        if kwargs['auto_exit']:
            kwargs['enter'] = kwargs.get('enter', None) or []
            kwargs['enter'].append(next_state) # type: ignore
        self._states[kwargs['name']] = kwargs
        self._machine.add_state(
            kwargs['name'],
            on_enter=self._on_enter_actions(kwargs['name']),
            on_exit=self._on_exit_actions(kwargs['name'])
        )

    def _on_enter_actions(self, state: str) -> Optional[_MachineActions]:
        options = self._get_state(state)
        if options.get('enter', None) is None:
            return None
        return self._create_actions(options.get('enter', None))

    def _on_exit_actions(self, state: str) -> Optional[_MachineActions]:
        options = self._get_state(state)
        if options.get('exit', None) is None:
            return None
        return self._create_actions(options.get('exit', None))

    def _get_state(self, state: str) -> StateOptions[_Data]:
        try:
            return self._states[state]
        except KeyError:
            raise ValueError(f'Unable to find state {state}.')

    def add_transitions(self, transitions: dict[str, TransitionOptions[_Data]]) -> None:
        for trigger, options in transitions.items():
            self.add_transition(**options)

    def add_transition(self, **kwargs: Unpack[TransitionOptions[_Data]]) -> None:
        trigger = kwargs['trigger']
        source = kwargs['source']
        target = kwargs.get('target', None)
        self._transitions[trigger] = TransitionProps(
            trigger,
            source,
            target,
            before=kwargs.get('before', None),
            after=self._after_transition(kwargs.get('after', None)),
            prepare=kwargs.get('prepare', None),
            guards=kwargs.get('guards', None)
        )
        self._machine.add_transition(
            trigger,
            source,
            target,
            before=self._before_transition_actions(trigger),
            after=self._after_transition_actions(trigger),
            prepare=self._get_prepare_actions(trigger),
            conditions=self._transition_guards(trigger)
        )

    def _before_transition_actions(self, trigger: str) -> Optional[_MachineActions]:
        transition = self._get_transition(trigger)
        if transition.before is None:
            return None
        return self._create_actions(transition.before)

    def _after_transition_actions(self, trigger: str) -> Optional[_MachineActions]:
        transition = self._get_transition(trigger)
        if transition.after is None:
            return None
        return self._create_actions(transition.after)

    def _get_prepare_actions(self, trigger: str) -> Optional[_MachineActions]:
        transition = self._get_transition(trigger)
        if transition.prepare is None:
            return None
        return self._create_actions(transition.prepare)

    def _transition_guards(self, trigger: str) -> Optional[_MachineGuards]:
        transition = self._get_transition(trigger)
        if transition.guards is None:
            return None
        if isinstance(transition.guards, list):
            return [lambda **kwargs: guard(self._context, **kwargs) for guard in transition.guards]
        return lambda **kwargs: transition.guards(self._context, **kwargs)

    def _after_transition(self, after: Optional[AfterTransition[_Data]]) -> Optional[Actions[_Data]]:
        if after is None:
            return None
        elif callable(after):
            return after
        elif after is True:
            return next_state # type: ignore
        elif isinstance(after, str):
            return trigger_transition(after)
        elif isinstance(after, list):
            if len(after) == 0:
                return None
            actions: list[Action[_Data]] = []
            for action in after:
                if callable(action):
                    actions.append(action)
                elif isinstance(action, str):
                    actions.append(trigger_transition(action))
            return actions
        raise TypeError(f'Invalid type for AfterTransition, got {type(after)}.')

    def _get_transition(self, trigger: str) -> TransitionProps:
        try:
            return self._transitions[trigger]
        except KeyError:
            raise ValueError(f'Transition with trigger {trigger} not found.')

    def _create_actions(self, actions: Actions[_Data]) -> _MachineActions:
        if isinstance(actions, list):
            return [self._create_action(action) for action in actions]
        return self._create_action(actions)

    def _create_action(self, action: Action[_Data]) -> Callable:
        def function(**kwargs) -> None:
            if inspect.iscoroutinefunction(action):
                return run_sync(action(self._context, **kwargs))
            return action(self._context, **kwargs)
        return function

    # Interactions

    def change_state(self, state: str, **kwargs) -> None:
        pass

    async def achange_state(self, state: str, **kwargs) -> None:
        pass

    def next_state(self, **kwargs) -> None:
        pass

    async def anext_state(self, **kwargs) -> None:
        pass

    def trigger(self, event: str, **kwargs) -> None:
        self._machine.trigger(event, **kwargs)

    async def atrigger(self, event: str, **kwargs) -> None:
        await run_async(self._machine.trigger, event, **kwargs)

    def update_data(self, data: _Data) -> None:
        pass