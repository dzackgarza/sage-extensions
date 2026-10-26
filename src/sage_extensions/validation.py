r"""The session-wide strict-checking flag and the validator protocol (``OWN-22``).

Construction stores the defining datum and fixes the category; it does not
check that the datum satisfies the category's laws.  A law that can be checked
is a *validator*: a method of the object, decorated with :func:`validator`,
that raises ``ValueError`` when the object fails it.  Construction calls the
object's validators once, after the object exists, passing its own ``check``
argument (default ``False``); each validator then returns at once unless the
caller asked (``check=True``) or the flag :data:`strict_checking` is on.  A
validator called by hand runs.

The flag is one setting for the whole session, off by default::

    sage: strict_checking()
    False
    sage: strict_checking(True)
    True

Its spelling follows Sage's proof preferences (``proof.arithmetic()`` reads,
``proof.arithmetic(False)`` sets; ``sage/structure/proof/proof.py``).
"""

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, TypeVar

_Owner = TypeVar("_Owner")


class _StrictChecking:
    r"""The strict-checking flag: ``strict_checking()`` reads it, ``strict_checking(True)`` sets it."""

    def __init__(self) -> None:
        self._on = False

    def __call__(self, on: bool | None = None) -> bool:
        match on:
            case None:
                pass
            case _:
                self._on = bool(on)
        return self._on

    def __repr__(self) -> str:
        return f"strict checking of constructions is {'on' if self._on else 'off'}"


strict_checking = _StrictChecking()


def validator(law: Callable[[_Owner], None]) -> Callable[Concatenate[_Owner, ...], None]:
    r"""Make ``law`` a validator: it runs when called with ``check=True`` (the default) or under strict checking.

    ``law`` takes only the object and raises ``ValueError`` when the object
    fails the law.  Construction calls the validator with its own ``check``
    argument, so an unchecked construction returns at once.
    """

    @wraps(law)
    def run(owner: _Owner, /, *, check: bool = True) -> None:
        if check or strict_checking():
            law(owner)

    return run
