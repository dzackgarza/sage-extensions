"""Small reusable helpers shared by the active preamble."""

import weakref
from collections.abc import Callable, Iterable
from functools import reduce, wraps
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


def _recoverable(argument):
    r"""Return how to recover ``argument``: weakly if it can die, else itself.

    An object that cannot be weakly referenced cannot be collected, so its
    address cannot be reused and holding it directly loses nothing.
    """
    try:
        return True, weakref.ref(argument)
    except TypeError:
        return False, argument


def _address_registry(function):
    r"""Memoize ``function`` by the addresses of its arguments, while they hold them.

    The key is the ``id`` of every argument, which is not a name: two different
    objects share an address exactly when one of them has died.  A memo that
    answers by address alone therefore returns the answer computed for a
    different object once its key object is gone -- the arguments the answer was
    computed for are not the arguments of the question asked.  So each entry
    keeps a recoverable reference to the arguments it was computed for, and an
    entry whose argument is no longer the object at its address answers nothing:
    the function is computed again for the question actually put to it.

    No argument that can die is held strongly, so the registry does not keep
    alive what it answers about: a caller that drops the last other reference to
    an argument leaves an entry that the next sweep removes.  A function whose
    arguments are all long-lived loses nothing by the check.

    Recomputing is the answer and not a fallback: the function's value for live
    arguments is a function of those arguments, so a question whose subject is
    gone is asked again, rather than answered from a smaller datum.
    """

    entries = {}
    unswept = [0]

    def recover(entry):
        return tuple(
            reference() if weak else reference for weak, reference in entry
        )

    def arguments_of(args, kwargs):
        return (*args, *(kwargs[name] for name in sorted(kwargs)))

    def swept_out(entry):
        return any(weak and reference() is None for weak, reference in entry)

    @wraps(function)
    def call(*args, **kwargs):
        key = (
            tuple(id(argument) for argument in args),
            tuple((name, id(value)) for name, value in sorted(kwargs.items())),
        )
        entry = entries.get(key)
        arguments = arguments_of(args, kwargs)
        if entry is not None and all(
            recovered is argument
            for recovered, argument in zip(recover(entry[0]), arguments, strict=True)
        ):
            return entry[1]
        result = function(*args, **kwargs)
        entries[key] = (
            tuple(_recoverable(argument) for argument in arguments),
            result,
        )
        unswept[0] += 1
        if unswept[0] >= 256:
            unswept[0] = 0
            for stale in tuple(entries):
                if swept_out(entries[stale][0]):
                    del entries[stale]
        return result

    call.clear = entries.clear
    return call
