import re
import typing


def assert_dict_contains_keys(d: dict, keys: set) -> None:
    assert keys.issubset(d.keys()),\
        f"dictionary {d} doesn't contain the mandatory keys {keys}"


def tokens_to_pattern(tokens: str) -> typing.Pattern:
    regex = re.sub(r'{(\w+)}', r'(?P<\1>.+)', tokens)
    return re.compile(regex)
