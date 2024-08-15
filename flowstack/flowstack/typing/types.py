from typing import Any, Callable, Union

from numpy import ndarray
import tenacity

MetadataType = Union[dict[str, Any], list[dict[str, Any]]]
Embedding = ndarray

RetryStrategy = tenacity.retry_base | Callable[[tenacity.RetryCallState], bool]
StopStrategy = tenacity.stop.stop_base | Callable[[tenacity.RetryCallState], bool]
WaitStrategy = tenacity.wait.wait_base | Callable[[tenacity.RetryCallState], int | float]
AfterRetryFailure = Callable[[tenacity.RetryCallState], None]