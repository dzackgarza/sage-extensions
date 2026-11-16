"""Owned runtime names emitted by the research Sage dialect.

The parser may run on top of Sage, but lowered public preamble source resolves
these names into preamble objects.  Backend constructors are used only inside
the functions below and every backend value is crossed back before return.
"""

from __future__ import annotations

from collections.abc import Iterable
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
# The modules whose star import is the complete session, and the names such an
# import binds.  A file that writes ``from <module> import *`` binds names the
# parse cannot see, so the lowering below separates the two readings of
# ``R = A[x]`` by whether ``x`` is one of them.  The module that publishes the
# names declares them in its own body and registers that declaration here; this
# module reads no namespace and imports no sibling to recover one.
_SESSION_MODULES: set[str] = {"sage_extensions.all"}
_SESSION_NAMES: frozenset[str] = frozenset()
_RESEARCH_ASSIGNMENT = _RESEARCH_EXTENSION["assignment"]


def _root(node: Node) -> Node:
    while node.parent is not None:
        node = node.parent
    return node


def _has_session_star_import(node: Node, context: Context) -> bool:
    r"""Whether this source imports the complete session."""
    stack = [_root(node)]
    expected = {f"from{module}import*" for module in _SESSION_MODULES}
    while stack:
        current = stack.pop()
        if current.type == "import_from_statement":
            written = "".join(context.text(current).split())
            if written in expected:
                return True
        stack.extend(current.children)
    return False


def _assignment_uses_session_name(node: Node, context: Context) -> bool:
    r"""Whether this assignment's subscript is indexed by a name the session binds."""
    right = node.child_by_field_name("right")
    if right is None or right.type != "subscript":
        return False
    return any(
        child.type == "identifier" and context.text(child) in _SESSION_NAMES
        for child in right.children_by_field_name("subscript")
    )


def _lower_session_assignment(node: Node, context: Context) -> str | None:
    r"""Keep a subscript ordinary when its index is a name the session supplies.

    The upstream research dialect reads ``R = A[x]`` as a generator declaration
    when the file binds ``x`` nowhere.  A star import binds names at runtime and
    contributes no identifier node to that static bound-name scan, so a file that
    writes ``from sage_extensions.all import *`` cannot establish the premise by
    itself.  The session states which names its star import binds, and this rule
    reads that one fact.

    An index the session supplies keeps the assignment the subscript it is
    written as: ``Sets.Δ[aleph0]`` is the set of cardinality ``aleph0``.  Every
    other assignment is delegated unchanged to the upstream research lowering,
    which declares the generators of an index no statement of the file binds:
    ``QQ[t]`` there is the polynomial ring over ``QQ`` in ``t``, and ``t`` is
    bound to its generator.  A generator a file declares is unaffected --
    ``R.<x> = A[x]`` is a ``sage_generator_assignment``, not an assignment, so
    this rule does not reach it.
    """
    if _has_session_star_import(node, context) and _assignment_uses_session_name(
        node, context
    ):
        return splice(node, context)
    return _RESEARCH_ASSIGNMENT(node, context)


_EXTENSION = {"assignment": _lower_session_assignment}

# Importing this module installs it, as importing ``sageparse.preparser.research``
# installs the dialect it extends: the rules, the names they emit and the imports
# that bind them are the module's declarations, so registering them is what the
# module does, not a step a caller performs on it.
register_extension(_EXTENSION, runtime=_RUNTIME, imports=_IMPORTS)


def register_session_module(module: str) -> None:
    r"""Treat ``from <module> import *`` as importing the complete session.

    A package that re-exports the session under another name says so once, here,
    and the files that star-import it are read the way a file that star-imports
    ``sage_extensions.all`` is: the names it binds are the session's, and no
    subscript index in one of its files is taken for a name it does not bind.
    """
    _SESSION_MODULES.add(module)


def register_session_names(names: Iterable[str]) -> None:
    r"""Declare the names a star import of the session binds.

    ``sage_extensions.all`` states its export list in its own body and registers
    that statement here, so the vocabulary the lowering reads is the session's
    declaration about itself rather than a reading of its namespace taken at
    some moment of its import.  Until a session declares, the upstream research
    reading stands unchanged.
    """
    global _SESSION_NAMES
    _SESSION_NAMES = frozenset(names)


__all__ = tuple(_RUNTIME) + ("register_session_module", "register_session_names")
