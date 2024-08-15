from flowstack.core import SyncAction, WorkflowContext

def trigger_transition[D](event: str) -> SyncAction[D]:
    def inner(context: WorkflowContext[D], **kwargs) -> None:
        context.trigger(event, **kwargs)
    return inner # type: ignore

def next_state[D](context: WorkflowContext[D], **kwargs) -> None:
    context.next_state(**kwargs)