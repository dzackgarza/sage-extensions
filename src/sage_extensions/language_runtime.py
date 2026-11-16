"""Owned runtime names emitted by the research Sage dialect.

The parser may run on top of Sage, but lowered public preamble source resolves
these names into preamble objects.  Backend constructors are used only inside
the functions below and every backend value is crossed back before return.
"""

from __future__ import annotations

from functools import cache
from importlib import import_module
from typing import cast

from sage.structure.element import parent as element_parent
from sageparse import Context, Node, splice
from sageparse.extensions.research import EXTENSION as _RESEARCH_EXTENSION
from sageparse.preparser import register_extension

from sage_extensions.categories.rings.ring_foundation import (
    OwnedRings,
    _owned_engine_element,
    _owned_integers,
    _OwnedIntegerElement,
)
from sage_extensions.categories.sets.set_categories import (
    Set as owned_set,
)
from sage_extensions.rings.real import (
    RR,
    ExactRealNumber,
)
from sage_extensions.rings.real import (
    RealApproximation as owned,
)


def Integer(value: int | str | _OwnedIntegerElement = 0) -> _OwnedIntegerElement:

    # The ZZ parent selects _OwnedIntegerElement as its Element class.
    return cast(_OwnedIntegerElement, _owned_integers()(value))


def RealNumber(
    value: int | str | _OwnedIntegerElement | ExactRealNumber,
) -> ExactRealNumber:

    return cast(ExactRealNumber, RR(value))


def RealApproximation(value):

    return owned(value)


def ComplexNumber(real, imag=None):
    from sage.rings.complex_mpfr import create_ComplexNumber

    backend = (
        create_ComplexNumber(real) if imag is None else create_ComplexNumber(real, imag)
    )
    # create_ComplexNumber selects the native complex field precision; raise
    # that datum through the owned field constructor, not generic engine ingress.
    from sage_extensions.categories.rings.ring_foundation import (
        _owned_complex_field_of_precision,
    )

    parent = _owned_complex_field_of_precision(int(backend.parent().precision()))
    return _owned_engine_element(parent, backend)


def matrix(rows):
    r"""Construct the owned matrix-Mor represented by a rectangular row family."""
    rows = tuple(tuple(row) for row in rows)
    if rows:
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError(
                f"a matrix needs rows of one common length, but the given rows have "
                f"lengths {tuple(len(row) for row in rows)}"
            )
    else:
        width = 0

    ring = None
    for row in rows:
        for entry in row:
            parent = element_parent(entry)
            if parent in OwnedRings():
                ring = parent
                break
        if ring is not None:
            break
    if ring is None:
        ring = _owned_integers()
    matrix_space = ring.matrix_space(len(rows), width)
    return matrix_space.from_rows(rows)


def Set(iterable):

    return owned_set(iterable)


def factorial(value: int | str | _OwnedIntegerElement) -> _OwnedIntegerElement:
    r"""The factorial \(n!\) of the integer ``value``, read from the integer's own method."""
    return Integer(value).factorial()


def ellipsis_range(*args):
    from sage.arith.srange import ellipsis_range as backend_ellipsis_range

    converted = [
        int(Integer(value)) if value is not Ellipsis else value for value in args
    ]
    return [Integer(value) for value in backend_ellipsis_range(*converted)]


def ellipsis_iter(*args):
    return iter(ellipsis_range(*args))


_RUNTIME = {
    "Integer": Integer,
    "RealNumber": RealNumber,
    "ComplexNumber": ComplexNumber,
    "RealApproximation": RealApproximation,
    "ellipsis_range": ellipsis_range,
    "ellipsis_iter": ellipsis_iter,
    "factorial": factorial,
    "matrix": matrix,
    "Set": Set,
}
_IMPORTS = {
    name: f"from sage_extensions.language_runtime import {name}" for name in _RUNTIME
}
# The modules whose star import is the complete session.  A file that writes
# ``from <module> import *`` binds the names that module publishes, and the
# lowering below keeps a subscript ordinary when its index is one of them.
_SESSION_MODULES: frozenset[str] = frozenset({"sage_extensions.all"})
_RESEARCH_ASSIGNMENT = _RESEARCH_EXTENSION["assignment"]


def _root(node: Node) -> Node:
    while node.parent is not None:
        node = node.parent
    return node


def _session_star_import(node: Node, context: Context) -> str | None:
    r"""The session module whose ``import *`` the file holding ``node`` writes."""
    stack = [_root(node)]
    expected = {f"from{module}import*": module for module in _SESSION_MODULES}
    while stack:
        current = stack.pop()
        if current.type == "import_from_statement":
            written = "".join(context.text(current).split())
            if written in expected:
                return expected[written]
        stack.extend(current.children)
    return None


@cache
def _session_names(module: str) -> frozenset[str]:
    r"""The names ``from <module> import *`` binds: that module's public namespace.

    The statement's own definition: ``import *`` binds the module's ``__all__``
    when it declares one and every name not starting with an underscore when it
    does not, which is the same set a reader of the module resolves.  The
    session's names are therefore read from the session module, never handed to
    this one to hold: a caller that passed its ``globals()`` here would put the
    names of a module into a table this module owns, and the module's namespace
    would then depend on when it imported.

    A module's public namespace is fixed once its import returns, and
    ``import_module`` returns only a module whose body has finished, so the set
    is read once per module and every later assignment in every file that
    star-imports it compares against the same frozen set.
    """
    return frozenset(
        name
        for name in vars(import_module(module))
        if not name.startswith("_")
    )


def _assignment_uses_session_name(node: Node, context: Context, module: str) -> bool:
    right = node.child_by_field_name("right")
    if right is None or right.type != "subscript":
        return False
    names = _session_names(module)
    return any(
        child.type == "identifier" and context.text(child) in names
        for child in right.children_by_field_name("subscript")
    )


def _lower_session_assignment(node: Node, context: Context) -> str | None:
    """Keep a subscript ordinary when its index comes from the session star import.

    The upstream research dialect interprets R = A[x] as a generator
    declaration when x is unbound in the file. A star import binds names at
    runtime but contributes no identifier nodes to that static bound-name
    scan. The session module owns exactly which names its star import supplies,
    so it resolves that one missing binding fact here. Every other assignment is
    delegated unchanged to the upstream research lowering.
    """
    module = _session_star_import(node, context)
    if module is not None and _assignment_uses_session_name(node, context, module):
        return splice(node, context)
    return _RESEARCH_ASSIGNMENT(node, context)


_EXTENSION = {"assignment": _lower_session_assignment}

# Importing this module installs it, as importing ``sageparse.preparser.research``
# installs the dialect it extends: the rules, the names they emit and the imports
# that bind them are the module's declarations, so registering them is what the
# module does, not a step a caller performs on it.
register_extension(_EXTENSION, runtime=_RUNTIME, imports=_IMPORTS)

__all__ = tuple(_RUNTIME)
