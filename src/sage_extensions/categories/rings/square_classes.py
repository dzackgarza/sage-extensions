r"""The square-class group \(M^\times/(M^\times)^2\) of a commutative monoid.

For a commutative monoid \(M\) the squaring map \(u\mapsto u^2\) is an
endomorphism of the abelian group \(M^\times\), and its cokernel is the
square-class group \(M^\times/(M^\times)^2\). Every element has order
dividing two, since \([u]^2=[u^2]\) is trivial.  A class \([u]\) is named by
any representative unit, and \([u]=[v]\) exactly when \(uv\) is a square:
\(uv=(u/v)\,v^2\), so \(uv\) is a square iff \(u/v\) is.  Deciding equality
is therefore deciding squareness in the selected monoid. A square root of a
unit is itself a unit. If squareness is undecided, equality remains an owned
proposition.

It is the codomain of the spinor norm
\(\mathrm{sn}_K\colon O(L\otimes K)\to K^\times/(K^\times)^2\)
[GHS08, §1], and a monoid morphism \(\varphi\colon M\to N\) induces
\([u]\mapsto[\varphi(u)]\): it sends units to units and squares to squares.
"""

from sage.misc.latex import latex
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import MultiplicativeGroupElement, parent

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.groups import AbelianGroups, OwnedGroups
from sage_extensions.categories.group.magmas import Monoids
from sage_extensions.logic import AtomicProposition, negation
from sage_extensions.owned_category import _object_of


class SquareClass(MultiplicativeGroupElement):
    r"""The class \([u]\in M^\times/(M^\times)^2\) of a unit of the selected monoid."""

    def __init__(self, parent, representative) -> None:
        MultiplicativeGroupElement.__init__(self, parent)
        self._representative = representative

    def representative(self):
        r"""Return the unit this class was named by; any other representative differs by a square."""
        return self._representative

    def _mul_(self, other):
        r"""\([u][v]=[uv]\)."""
        return self.parent()._class_of_unit(
            self._representative * other._representative
        )

    def __invert__(self):
        r"""\([u]^{-1}=[u^{-1}]=[u\cdot u^{-2}]=[u]\): every class is its own inverse."""
        return self

    def is_one(self):
        r"""Whether \([u]\) is trivial, that is whether \(u\) is a square."""
        return self.parent()._unit_is_square(self._representative)

    def order(self):
        r"""The order of \([u]\): one when \(u\) is a square, two otherwise."""
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        integers = _owned_integers()
        decision = self.is_one()
        if decision is True:
            return integers.one()
        if decision is False:
            return integers(2)
        assert False, (
            f"the order of {self} is one or two, but whether its representative "
            f"is a square in {self.parent().monoid()} is undecided"
        )

    multiplicative_order = order

    def __eq__(self, other):
        r"""\([u]=[v]\) exactly when \(uv\) is a square."""
        if not isinstance(other, SquareClass) or other.parent() is not self.parent():
            return False
        if self is other or (self._representative == other._representative) is True:
            return True
        return self.parent()._unit_is_square(
            self._representative * other._representative
        )

    def __ne__(self, other):
        return negation(self == other)

    def __hash__(self):
        r"""Constant on the group: no canonical representative is selected."""
        return hash(id(self.parent()))

    def _repr_(self):
        return f"[{self._representative}]"

    def _latex_(self):
        return rf"\left[{latex(self._representative)}\right]"


class _SquareClassGroup:
    r"""The cokernel of squaring on the selected unit group, at ``AbelianGroups()``.

    The monoid is the defining datum; the group law is its
    multiplication on representatives.
    """

    def __init__(self, monoid, **rest) -> None:
        self._monoid = monoid
        super().__init__(**rest)

    def monoid(self):
        r"""Return the literal ambient monoid defining this square-class group."""
        return self._monoid

    def ring(self):
        r"""Return the retained ring for the existing ring-case spelling."""
        from sage_extensions.categories.rings.ring_foundation import OwnedRings

        assert self._monoid in OwnedRings(), (
            f"{self} has the selected ambient monoid {self._monoid}, without "
            "an owned ring structure for this accessor"
        )
        return self._monoid

    def projection(self):
        r"""Return the group quotient map \(u\mapsto[u]\)."""
        units = self.monoid().unit_group()
        return OwnedGroups().Mor(units, self)(self._class_of_unit)

    def _class_of_unit(self, unit):
        r"""Construct the class of an established unit of the literal ambient monoid.

        Protected constructor under OWN-05. The public element constructor
        supplies a proved unit; ``one`` supplies the identity; multiplication
        supplies a product of its retained unit representatives; ``projection``
        supplies an element of the actual unit group; and the square-class
        functor supplies its image under the actual monoid map. These callers
        establish the unit premise without another target-unit decision.
        No ambient datum or representative is replaced.
        """
        return self.element_class(self, unit)

    def _unit_is_square(self, unit):
        r"""Return squareness of a unit in this exact selected monoid.

        ``SquareClass.is_one`` and ``SquareClass.__eq__`` are the callers;
        they supply a retained unit or a product of retained units. Only an
        element whose literal parent is this monoid can supply its square
        predicate here. A facade's larger ambient parent cannot answer this
        relative question, so that case retains its own proposition.
        """
        monoid = self._monoid
        if (unit == monoid.one()) is True:
            return True
        if parent(unit) is monoid:
            return unit.is_square()
        return AtomicProposition("is_square", monoid, unit)

    def sign_isomorphism(self):
        r"""``RR^x/(RR^x)^2 -> C_2``, the class of a unit to its sign.

        Every positive real is a square, so the classes of the real field are
        those of ``1`` and ``-1``; the sign of a representative is the class.
        """
        from sage_extensions.rings.real import RR

        assert self._monoid is RR, (
            f"the sign identifies the square classes of the real field, but {self} is the square-class group of {self._monoid}"
        )
        signs = OwnedGroups().C(2)
        (negative,) = tuple(element for element in signs if not element.is_one())
        return OwnedGroups().Mor(self, signs)(
            lambda square_class: signs.one() if square_class.representative() > 0 else negative
        )

    def __call__(self, datum):
        return self._element_constructor_(datum)

    def _element_constructor_(self, datum):
        r"""Return a class of this group, or the class of an established ambient unit."""
        if datum in self:
            return datum
        unit = self._monoid(datum)
        decision = self.monoid().unit_group().is_parent_of(unit)
        if decision is False:
            raise ValueError(
                f"{datum} has no class in {self}: it is not a unit of {self._monoid}"
            )
        assert decision is True, (
            f"cannot admit {datum} into {self}: whether it is a unit of "
            f"{self._monoid} is undecided"
        )
        return self._class_of_unit(unit)

    def __contains__(self, datum) -> bool:
        return isinstance(datum, SquareClass) and datum.parent() is self

    def one(self):
        return self._class_of_unit(self._monoid.one())

    def _repr_(self):
        return f"{self._monoid}^× / ({self._monoid}^×)^2"

    def _latex_(self):
        monoid = latex(self._monoid)
        return rf"{monoid}^\times/({monoid}^\times)^2"


def _square_class_group(monoid):
    r"""Return the square-class group of the owned commutative ``monoid``.

    ``Monoids.Commutative.ParentMethods.square_class_group`` is the one
    protected-constructor caller. The exact source monoid is retained, and
    its commutativity proves that the squares of units form a subgroup.
    """
    assert monoid in Monoids().Commutative(), (
        f"the square-class group needs a commutative monoid, but {monoid} "
        "is not supplied in that category"
    )
    return _object_of(
        AbelianGroups(),
        _engine=(OwnedGroups(), _SquareClassGroup, SquareClass),
        monoid=monoid,
    )


class SquareClassGroupFunctor(Functor):
    r"""\(M\mapsto M^\times/(M^\times)^2\) and \(\varphi\mapsto([u]\mapsto[\varphi(u)])\).

    A monoid morphism sends a unit to a unit and a square to a square, so the
    induced map on classes is well defined, and it is multiplicative because
    \(\varphi\) is.  The images are abelian groups of exponent dividing two.
    """

    def __init__(self) -> None:
        super().__init__(Monoids().Commutative(), OwnedGroups())

    def _apply_object(self, monoid):
        return monoid.square_class_group()

    def _apply_morphism(self, morphism):
        source = self.object_image(morphism.domain())
        target = self.object_image(morphism.codomain())
        return OwnedGroups().Mor(source, target)(
            lambda square_class: target._class_of_unit(
                morphism(square_class.representative())
            ),
        )

    def _repr_(self):
        return "Square-class group functor CMon -> Grp"


__all__ = ["SquareClass", "SquareClassGroupFunctor"]
