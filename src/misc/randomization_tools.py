import random
from typing import Any


def choose_by_weight(options: list[tuple[Any, int]]) -> Any:
    """
    get a list of (value, weight) tuples
    return one value, chosen randomly by weight
    """
    values = [value for value, _ in options]
    weights = [weight for _, weight in options]
    return random.choices(values, weights=weights)[0]
