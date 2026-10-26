"""Small reusable helpers shared by the active preamble."""

from collections.abc import Callable, Iterable
from functools import reduce
from operator import add, mul
from typing import cast

__all__ = ["lmap", "lzip", "to_var_names", "zipsum"]


def lmap[T, U](function: Callable[[T], U], values: Iterable[T]) -> list[U]:
    return list(map(function, values))


def lzip[T](*iterables: Iterable[T]) -> list[tuple[T, ...]]:
    return list(zip(*iterables))


def to_var_names(names: str) -> list[str]:
    return [name.replace(" ", "").strip() for name in names.split(",")]


def zipsum[C, G, T](
    coefficients: Iterable[C],
    elements: Iterable[G],
    zero: T,
    *,
    term: Callable[[C, G], T] | None = None,
) -> T:
    """Return the sum of pairwise terms from two equally sized iterables."""
    if term is None:
        term = cast(Callable[[C, G], T], mul)
    summands = (
        term(coefficient, element)
        for coefficient, element in zip(coefficients, elements, strict=True)
    )
    return reduce(cast(Callable[[T, T], T], add), summands, zero)
