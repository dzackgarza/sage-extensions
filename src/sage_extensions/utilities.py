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


def _recover(recoverable):
    r"""Return the object a recorded reference names, or ``None`` if it is gone."""
    weak, reference = recoverable
    return reference() if weak else reference


def _still_holds(entry, arguments):
    r"""Whether every argument of the question is the object the entry recorded."""
    return all(
        _recover(recoverable) is argument
        for recoverable, argument in zip(entry, arguments, strict=True)
    )


def _swept_out(entry):
    r"""Whether a recorded argument of the entry is gone."""
    return any(weak and reference() is None for weak, reference in entry)


def _recorded_arguments(arguments):
    r"""Return the entry for ``arguments``: how to recover each of them."""
    return tuple(_recoverable(argument) for argument in arguments)


def _sweep(entries, unswept):
    r"""Drop the entries whose recorded argument is gone, once every 256 writes.

    An entry whose subject is gone holds an answer for an object nothing names;
    the answer is dropped with it rather than kept for whatever occupies the
    address next.
    """
    unswept[0] += 1
    if unswept[0] < 256:
        return
    unswept[0] = 0
    for stale in tuple(entries):
        if _swept_out(entries[stale][0]):
            del entries[stale]


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

    No argument that can die is held strongly: the registry keeps nothing of its
    own but the answer it computed.  So an answer that does not name its
    arguments outlives none of them, and the next sweep drops the entry; an
    answer that does name them keeps them, as the function's own value does, and
    the entry stays valid while they are alive.

    Recomputing is the answer and not a fallback: the function's value for live
    arguments is a function of those arguments, so a question whose subject is
    gone is asked again, rather than answered from a smaller datum.
    """

    entries = {}
    unswept = [0]

    def arguments_of(args, kwargs):
        return (*args, *(kwargs[name] for name in sorted(kwargs)))

    @wraps(function)
    def call(*args, **kwargs):
        key = (
            tuple(id(argument) for argument in args),
            tuple((name, id(value)) for name, value in sorted(kwargs.items())),
        )
        entry = entries.get(key)
        arguments = arguments_of(args, kwargs)
        if entry is not None and _still_holds(entry[0], arguments):
            return entry[1]
        result = function(*args, **kwargs)
        entries[key] = (_recorded_arguments(arguments), result)
        _sweep(entries, unswept)
        return result

    call.clear = entries.clear
    return call


def _instance_address_registry(function):
    r"""Memoize a method by the addresses of its arguments, on its own instance.

    The table of entries is the instance's, as ``cached_method``'s cache is: an
    entry lives exactly as long as the instance, so the swap changes what the key
    means and not what lives how long.  Inside the table the key is the ``id`` of
    every argument, and each entry keeps a recoverable reference to the arguments
    it was computed for, so an entry whose argument is no longer the object at its
    address answers nothing and the method is computed again.

    The first argument is the instance itself, whose entries are the table's
    subject: a table cannot outlive the instance that holds it.
    """

    attribute = "_address_registry_" + function.__qualname__.replace(".", "_")

    @wraps(function)
    def call(instance, *args, **kwargs):
        entries = _entries_on(instance, attribute)
        if entries is None:
            return function(instance, *args, **kwargs)
        arguments = (instance, *args, *(kwargs[name] for name in sorted(kwargs)))
        key = tuple(id(argument) for argument in arguments)
        entry = entries.get(key)
        if entry is not None and _still_holds(entry[0], arguments):
            return entry[1]
        result = function(instance, *args, **kwargs)
        entries[key] = (_recorded_arguments(arguments), result)
        _sweep(entries, entries.unswept)
        return result

    return call


class _UnpickledEntries(dict):
    r"""An entry table that is not part of the state of the object holding it.

    The table holds a reference to every argument an answer was computed for,
    which is not part of that object's value; an object pickled with such a table
    therefore pickles an empty one, as ``cached_method``'s cache does.
    """

    def __init__(self):
        super().__init__()
        self.unswept = [0]

    def __reduce__(self):
        return _UnpickledEntries, ()


def _entries_on(instance, attribute):
    r"""Return the entry table of ``instance``, made on first use.

    ``None`` when the instance cannot hold one: an instance of a type that stores
    no attributes has nowhere to keep an answer, as it has nowhere for
    ``cached_method``'s cache, and the method is then computed on every call.
    """
    try:
        mapping = instance.__dict__
    except AttributeError:
        mapping = getattr(instance, "_cached_methods", None)
        if mapping is None:
            return None
    entries = mapping.get(attribute)
    if entries is None:
        entries = mapping[attribute] = _UnpickledEntries()
    return entries


def _weak_address_registry(function):
    r"""Memoize ``function`` by the addresses of its arguments, holding the answer weakly.

    ``weak_cached_function``'s contract is that an entry adds nothing to what it
    answers about, and this keeps it: the arguments are recorded weakly and so is
    the answer, and an answer nothing else holds is computed again.  The key is
    still the ``id`` of every argument, which is not a name, so an entry whose
    argument is no longer the object at its address answers nothing even when the
    answer it holds is still alive.
    """

    entries = {}
    unswept = [0]

    @wraps(function)
    def call(*args, **kwargs):
        arguments = (*args, *(kwargs[name] for name in sorted(kwargs)))
        key = tuple(id(argument) for argument in arguments)
        entry = entries.get(key)
        if entry is not None and _still_holds(entry[0], arguments):
            answer = _answered(entry[1])
            if answer is not _NO_ANSWER:
                return answer
        result = function(*args, **kwargs)
        entries[key] = (_recorded_arguments(arguments), _recoverable(result))
        _sweep(entries, unswept)
        return result

    return call


def _answered(recoverable):
    r"""Return the answer a recorded reference names, or ``_NO_ANSWER`` if it is gone.

    A weakly held answer that has died and an answer that is legitimately ``None``
    are different facts: ``None`` cannot be weakly referenced, so it is held
    directly and is an answer.
    """
    weak, reference = recoverable
    if not weak:
        return reference
    answer = reference()
    return _NO_ANSWER if answer is None else answer


_NO_ANSWER = object()
