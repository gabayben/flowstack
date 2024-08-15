from functools import partial
import os
from typing import Any, Callable, Mapping, Optional, Type
import uuid

import tiktoken

SplitFunction = Callable[[str], list[str]]

def get_tokenizer() -> Callable[[str], list[int]]:
    should_revert = False
    if "TIKTOKEN_CACHE_DIR" not in os.environ:
        should_revert = True
        os.environ["TIKTOKEN_CACHE_DIR"] = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "_static/tiktoken_cache",
        )

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokenizer = partial(encoding.encode, allowed_special="all")

    if should_revert:
        del os.environ["TIKTOKEN_CACHE_DIR"]
    return tokenizer

def mapping_to_str(
    obj: Mapping[str, Any | None],
    exclude: list[str] = []
) -> str:
    text = ''
    for k, v in obj.items():
        if k not in exclude and v:
            text += f'\n{k}: {v}'
    return text.strip('\n')

def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

def type_name(type_: Type) -> str:
    return f'{type_.__module__}.{type_.__name__}'

def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."

def count_words[T](
    objs: list[T],
    key: Optional[Callable[[T], str]] = None
) -> int:
    return sum(
        len((key(obj) if key else str(obj)).split())
        for obj in objs
    )

def count_tokens[T](
    objs: list[T],
    key: Optional[Callable[[T], str]] = None
) -> int:
    return int(count_words(objs, key=key) * (4/3))

def cost_of_tokens[T](
    objs: list[T],
    price: float,
    units: int = 1_000_000,
    key: Optional[Callable[[T], str]] = None,
    ndigits: int = 4
) -> float:
    return round((count_tokens(objs, key=key) / units) * price, ndigits)