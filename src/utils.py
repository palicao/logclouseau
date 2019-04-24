import re


def assert_dict_contains_keys(d: dict, keys: set) -> bool:
    assert keys.issubset(d.keys()), f"dictionary {d} doesn't contain the mandatory keys {keys}"


def tokens_to_pattern(tokens: str) -> re.Pattern:
    regex = re.sub(r'{(\w+)}', r'(?P<\1>.+)', tokens)
    return re.compile(regex)
