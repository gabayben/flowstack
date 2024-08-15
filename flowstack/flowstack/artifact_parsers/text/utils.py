import logging

import nltk

from flowstack.core.utils.string import SplitFunction

logger = logging.getLogger(__name__)

def split_by_sentence_tokenizer() -> SplitFunction:
    tokenizer = nltk.PunktSentenceTokenizer()
    return lambda text: _split_by_sentence_tokenizer(text, tokenizer)

def _split_by_sentence_tokenizer(text: str, tokenizer: nltk.PunktSentenceTokenizer) -> list[str]:
    sentences = []
    spans = list(tokenizer.span_tokenize(text))
    for i, span in enumerate(spans):
        start = span[0]
        if i < len(spans) - 1:
            end = spans[i + 1][0]
        else:
            end = len(text)
        sentences.append(text[start:end])
    return sentences

def split_by_sep_fn(seperator: str, keep_sep: bool = True) -> SplitFunction:
    if keep_sep:
        return lambda text: split_by_sep_keep(text, seperator)
    return lambda text: text.split(seperator)

def split_by_sep_keep(text: str, seperator: str) -> list[str]:
    parts = text.split(seperator)
    results = [part + seperator if i > 0 else part for i, part in enumerate(parts)]
    return [result for result in results if result]

def split_by_char_fn() -> SplitFunction:
    return lambda text: list(text)

def split_by_regex_fn(regex: str) -> SplitFunction:
    import re
    return lambda text: re.findall(regex, text)