r"""The real interval [0,1] and the actual domain of Young degree composition.

The pair domain is D={(s,t): s+t>=1}; (s,t)->s+t-1 is a set map D->[0,1].
This is not a monoid on [0,1], since the pair (0,0) has no image there.
"""

from sage.rings.rational_field import QQ
from sage.structure.element import Element
from sage.structure.element import parent as sage_parent
from sage.structure.parent import Parent
from sage.structure.richcmp import richcmp

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.sets.cardinals import continuum
from sage_extensions.categories.sets.set_categories import Sets
from sage.misc.cachefunc import cached_method
from sage_extensions.owned_category import _object_of
from sage_extensions.logic import ask
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.rings.nonnegative_reals import NonNegativeReal
from sage_extensions.rings.real import RR


class _UnitIntervalElement:
    r"""An element of \(([0,1],\oplus)\)."""

    def __init__(self, parent, value) -> None:
        self._value = value
        super().__init__(parent)

    def _repr_(self) -> str:
        return repr(self._value)

    def _latex_(self) -> str:
        return self._value._latex_()

    def as_extended_real(self):
        r"""This element as a real in \([0,1]\)."""
        return self._value

    def __hash__(self):
        # A constant hash respects every equality that the exact-real owner
        # can establish, including different equal symbolic expressions.
        return hash(self.parent())

    def _richcmp_(self, other, op):
        return richcmp(self._value, other._value, op)


class _UnitInterval:
    r"""The interval as a set, with endpoints zero and one."""

    @cached_method
    def degree_pairs(self):
        return Sets().product(indexed_family(Sets.Δ[1], lambda _: self))

    @cached_method
    def young_pairs(self):
        def admissible(pair):
            value = pair.component(0).as_extended_real() + pair.component(1).as_extended_real()
            decision = ask(value >= RR.one())
            assert decision is True or decision is False, (
                f"cannot decide whether {pair} is a Young pair (p, q) with 1/p + 1/q >= 1: "
                f"it is undecided whether {value} >= 1"
            )
            return decision

        return Sets().condition_set(self.degree_pairs(), admissible)

    @cached_method
    def young_degree_map(self):
        return Sets().Mor(self.young_pairs(), self)(lambda pair:
            self(pair.component(0).as_extended_real() + pair.component(1).as_extended_real() - RR.one()))

    def _repr_(self) -> str:
        return "Unit interval [0, 1]"

    def _latex_(self) -> str:
        return r"[0,1]"

    def _element_constructor_(self, value):
        if sage_parent(value) is self:
            return value
        if isinstance(value, NonNegativeReal):
            value = value.as_extended_real()
        real = RR(value)
        nonnegative = ask(real >= RR.zero())
        at_most_one = ask(real <= RR.one())
        if nonnegative is False or at_most_one is False:
            raise ValueError(f"{value} is not in [0, 1]")
        if nonnegative is True and at_most_one is True:
            return self.element_class(self, real)
        raise AssertionError(
            f"membership of {value} in [0, 1] is undecided; "
            f"use ask(0 <= {real} <= 1)"
        )

    def __contains__(self, value) -> bool:
        try:
            self(value)
        except (TypeError, ValueError):
            return False
        return True

    def one(self):
        r"""The right endpoint, not a unit of an asserted multiplication."""
        return self(RR.one())

    def zero(self):
        r"""The degree of \(L^\infty\), not the monoid identity."""
        return self(RR.zero())

    def _an_element_(self):
        return self.one()

    def cardinality(self):

        return continuum


def UnitIntervalElement(parent, value):
    return parent(value)


UnitInterval = _object_of(Sets().Infinite(), _engine=(Sets(), _UnitInterval, _UnitIntervalElement))
