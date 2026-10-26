"""Foundational mathematical nouns."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, NewType

from sage.rings.integer import Integer
from sage.rings.rational import Rational
from sage.structure.element import Matrix
from sage.symbolic.expression import Expression as SymbolicExpression

if TYPE_CHECKING:
    from sage_extensions.categories.sets.finite_ordered_sets import OrderedEnumeratedSets


type SignaturePair = tuple[Integer, Integer]
type CartanType = tuple[Literal["A", "D", "E"], Integer]
type LatticeName = str | CartanType
type OrderedSet[E] = OrderedEnumeratedSets().ObjectType
type MatrixData = Sequence[Sequence[Rational]]

GramMatrix = NewType("GramMatrix", Matrix)

__all__ = [
    "CartanType",
    "GramMatrix",
    "Integer",
    "LatticeName",
    "MatrixData",
    "OrderedSet",
    "Rational",
    "SignaturePair",
    "SymbolicExpression",
]
