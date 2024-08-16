from flowstack.core import SyncAction, MachineContext

def trigger_transition[D](event: str) -> SyncAction[D]:
    def inner(context: MachineContext[D], **kwargs) -> None:
        context.trigger(event, **kwargs)
    return inner # type: ignore

def next_state[D](context: MachineContext[D], **kwargs) -> None:
    context.next_state(**kwargs)