r"""Cardinal and ordinal arithmetic in the owned set-theoretic number hierarchy.

A cardinal is an object of :class:`Cardinalities` whose defining datum is a
term of cardinal arithmetic.  An ordinal is an object of :class:`Ordinals`
whose datum is a canonical order type: finite and initial ordinals retain
distinguished constructors, while every other represented ordinal is stored
in Cantor normal form.  Ordinary and Hessenberg arithmetic normalize through
that one representation, so equality and comparison do not depend on the
expression that produced an ordinal.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import cmp_to_key
from typing import TYPE_CHECKING, SupportsInt, TypeVar

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.infinity import AnInfinity, Infinity
from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
)
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

if TYPE_CHECKING:
    from sage_extensions.logic import Predicate

IndexT = TypeVar("IndexT")


def _is_session_integer(value) -> bool:
    r"""Whether ``value`` is an exact integer: a Python ``int`` or an element of the owned ``ZZ``.

    The session's integer literals are owned integers, which Sage's ``ZZ``
    neither contains nor converts, so the owned ring is asked about them.  A
    Python ``int`` is answered first, without the owned ring, because this
    module names finite cardinals while the owned integers are still being
    built.
    """
    if value in ZZ:
        return True
    from sage_extensions.categories.rings.ring_foundation import (
        _own_ring,
        _owned_integers,
    )

    return value in _owned_integers()


class _CardinalExpression(ABC):
    r"""A term of cardinal arithmetic, the defining datum of a cardinal.

    The forms are a finite cardinal ``n``, an aleph ``aleph_alpha``, a power
    ``kappa^lambda`` with infinite exponent, a finite supremum of terms that
    are not otherwise compared, and an indexed sum or product over an infinite
    index set.  The last two are not normal forms: they are not evaluated to
    any of the others, so neither their finiteness nor their order is decided
    here.

    The defaults below are the answers of the forms that do not override
    them.
    """

    @abstractmethod
    def display(self) -> str:
        r"""The notation of this term."""
        ...

    @abstractmethod
    def sort_key(self) -> tuple[int, str]:
        r"""The key ordering terms by form, then by notation."""
        ...

    def is_normal_form(self) -> bool:
        r"""Whether this term has a known finite-or-infinite classification."""
        return True

    def is_finite(self) -> bool:
        return False

    def is_aleph(self) -> bool:
        return False

    def is_countably_infinite(self) -> bool:
        return False

    def is_continuum(self) -> bool:
        return False

    def supremum_terms(self, cardinal_number: Cardinal) -> tuple[Cardinal, ...]:
        r"""The terms whose supremum ``cardinal_number`` is: itself alone."""
        return (cardinal_number,)

    def power_with_this_exponent(
        self,
        base: Cardinal,
        exponent: Cardinal,
    ) -> Cardinal:
        r"""``base^exponent`` for this term as the infinite exponent: the base decides."""
        return base.expression().power_with_this_base(base, exponent)

    def power_with_this_base(
        self,
        base: Cardinal,
        exponent: Cardinal,
    ) -> Cardinal:
        r"""``base^exponent`` for this term as the base: no law reduces it."""
        return _cardinal_with_expression(_PowerCardinal(base, exponent))

    def bounds_above(self, cardinal_number: Cardinal) -> bool:
        r"""Whether a law of this term's form shows ``cardinal_number <= self``: none does."""
        return False

    def strictly_bounds_above(self, cardinal_number: Cardinal) -> bool:
        r"""Whether a law of this term's form shows ``cardinal_number < self``: none does."""
        return False

    def is_componentwise_below(self, power: _PowerCardinal) -> bool:
        r"""Whether this term is a power below ``power`` in base and exponent: it is not a power."""
        return False


@dataclass(frozen=True)
class _FiniteCardinal(_CardinalExpression):
    value: int

    def display(self) -> str:
        return repr(self.value)

    def sort_key(self) -> tuple[int, str]:
        return (0, str(self.value))

    def is_finite(self) -> bool:
        return True


@dataclass(frozen=True)
class _AlephCardinal(_CardinalExpression):
    index: Ordinal

    def display(self) -> str:
        return f"ℵ_{self.index}"

    def sort_key(self) -> tuple[int, str]:
        return (1, str(self.index))

    def is_aleph(self) -> bool:
        return True

    def is_countably_infinite(self) -> bool:
        return self.index == 0


@dataclass(frozen=True)
class _PowerCardinal(_CardinalExpression):
    r"""``base^exponent`` with an infinite exponent and a base of at least two."""

    base: Cardinal
    exponent: Cardinal

    def display(self) -> str:
        return f"({self.base})^({self.exponent})"

    def sort_key(self) -> tuple[int, str]:
        return (2, self.display())

    def is_continuum(self) -> bool:
        return self.base == 2 and self.exponent.is_countably_infinite()

    def power_with_this_base(
        self,
        base: Cardinal,
        exponent: Cardinal,
    ) -> Cardinal:
        r"""``(kappa^lambda)^mu = kappa^(lambda mu)``."""
        cardinalities = Cardinalities()
        return cardinalities.power(
            self.base,
            cardinalities.product(self.exponent, exponent),
        )

    def bounds_above(self, cardinal_number: Cardinal) -> bool:
        r"""Decide ``cardinal_number <= kappa^lambda`` by the laws of exponentiation.

        ``nu <= kappa`` gives ``nu <= kappa^lambda`` since ``lambda >= 1``;
        ``2 <= kappa`` and ``nu <= lambda`` give ``nu < 2^lambda <= kappa^lambda``;
        a power ``rho^sigma`` with ``rho <= kappa`` and ``sigma <= lambda`` is
        below ``kappa^lambda`` by monotonicity.
        """
        cardinalities = Cardinalities()
        if cardinalities._proves_le(cardinal_number, self.base):
            return True
        if cardinalities._proves_le(2, self.base) and cardinalities._proves_le(cardinal_number, self.exponent):
            return True
        return cardinal_number.expression().is_componentwise_below(self)

    def strictly_bounds_above(self, cardinal_number: Cardinal) -> bool:
        r"""Decide ``cardinal_number < kappa^lambda`` by Cantor's theorem: ``nu <= lambda < 2^lambda <= kappa^lambda``."""
        cardinalities = Cardinalities()
        return cardinalities._proves_le(2, self.base) and cardinalities._proves_le(cardinal_number, self.exponent)

    def is_componentwise_below(self, power: _PowerCardinal) -> bool:
        cardinalities = Cardinalities()
        return cardinalities._proves_le(self.base, power.base) and cardinalities._proves_le(
            self.exponent, power.exponent
        )


@dataclass(frozen=True)
class _SupremumCardinal(_CardinalExpression):
    r"""The supremum of finitely many pairwise undecided terms, none a supremum."""

    terms: tuple[Cardinal, ...]

    def display(self) -> str:
        return "sup(" + ", ".join(map(str, self.terms)) + ")"

    def sort_key(self) -> tuple[int, str]:
        return (3, self.display())

    def supremum_terms(self, cardinal_number: Cardinal) -> tuple[Cardinal, ...]:
        return self.terms

    def power_with_this_exponent(
        self,
        base: Cardinal,
        exponent: Cardinal,
    ) -> Cardinal:
        r"""``kappa^(max_i lambda_i) = max_i kappa^(lambda_i)`` for finitely many ``lambda_i``."""
        cardinalities = Cardinalities()
        return cardinalities.supremum(*(cardinalities.power(base, term) for term in self.terms))

    def power_with_this_base(
        self,
        base: Cardinal,
        exponent: Cardinal,
    ) -> Cardinal:
        r"""``(max_i kappa_i)^lambda = max_i kappa_i^lambda`` for finitely many ``kappa_i``."""
        cardinalities = Cardinalities()
        return cardinalities.supremum(*(cardinalities.power(term, exponent) for term in self.terms))


@dataclass(frozen=True)
class _IndexedSumCardinal(_CardinalExpression):
    r"""``sum_{i in I} kappa_i`` over an infinite index set, not evaluated."""

    index_set: Parent
    summands: Callable

    def display(self) -> str:
        return f"sum_{{i in {self.index_set}}} kappa_i"

    def sort_key(self) -> tuple[int, str]:
        return (4, self.display())

    def is_normal_form(self) -> bool:
        return False


@dataclass(frozen=True)
class _IndexedProductCardinal(_CardinalExpression):
    r"""``prod_{i in I} kappa_i`` over an infinite index set, not evaluated."""

    index_set: Parent
    factors: Callable

    def display(self) -> str:
        return f"prod_{{i in {self.index_set}}} kappa_i"

    def sort_key(self) -> tuple[int, str]:
        return (4, self.display())

    def is_normal_form(self) -> bool:
        return False


class CardinalComparison(Enum):
    LESS = -1
    EQUAL = 0
    GREATER = 1
    LESS_OR_EQUAL = 2
    GREATER_OR_EQUAL = 3
    INCOMPARABLE = 4


class CardinalityMorphism(CategoricalMor.ElementMethods):
    def __init__(self, parent: CardinalityMor) -> None:
        Morphism.__init__(self, parent)

    def is_identity(self) -> bool:
        return self.domain() is self.codomain()

    def __mul__(self, other):
        r"""Compose ``self ∘ other``.

        The right operand is arbitrary, which is Python's binary-operator
        protocol: like ``__eq__``, this decides about anything and answers
        ``NotImplemented`` for what is not a composable order arrow.
        """
        other_parent = element_parent(other)
        match other_parent:
            case CategoricalMor() if (
                other_parent.mor_category().is_subcategory(Cardinalities())
                and other.codomain() is self.domain()
            ):
                pass
            case _:
                return NotImplemented
        return Cardinalities().Mor(other.domain(), self.codomain()).unique_morphism()

    def _repr_(self) -> str:
        return f"{self.domain()} <= {self.codomain()}"


class CardinalityMor(CategoricalMor):
    ElementMethods = CardinalityMorphism

    def __init__(
        self,
        mor_family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def is_empty(self):
        r"""The cardinal-order Mor is empty exactly when its source exceeds its target.

        It is the negation of ``domain <= codomain``: decided when that
        comparison is decided, and otherwise the proposition that states it.
        """
        from sage_extensions.logic import negation

        return negation(Cardinalities().le(self.domain(), self.codomain()))

    def cardinality(self) -> Cardinal:
        r"""Zero or one when the cardinal comparison decides the Mor's emptiness."""
        empty = self.is_empty()
        assert empty is True or empty is False, (
            f"cannot compute the cardinality of {self}: it is undecided whether {self.domain()} <= "
            f"{self.codomain()}, so it is undecided whether this set of morphisms is empty"
        )
        return cardinal(0 if empty else 1)

    @cached_method
    def unique_morphism(self) -> CardinalityMorphism:
        empty = self.is_empty()
        if empty is True:
            raise ValueError(
                f"there is no morphism {self.domain()} -> {self.codomain()} of cardinals: "
                f"{self.domain()} is not <= {self.codomain()}"
            )
        assert empty is False, (
            f"cannot give the morphism {self.domain()} -> {self.codomain()} of cardinals: it is "
            f"undecided whether {self.domain()} <= {self.codomain()}"
        )
        return self.element_class(self)

    def _element_constructor_(self, morphism=None):
        if morphism is not None and morphism.parent() is not self:
            raise ValueError(f"{morphism} is not in {self}")
        return self.unique_morphism()

    @object_level
    def identity(self) -> CardinalityMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self.unique_morphism()


class CardinalityMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self) -> type[CardinalityMor]:
        return CardinalityMor


class Cardinalities(OwnedCategory):
    r"""The thin category associated to the represented cardinal order."""

    def set_category(self, size):
        r"""Classify a decided cardinal as finite, countably infinite, or uncountable."""
        from sage_extensions.categories.sets.set_categories import (
            FiniteSets, CountablyInfiniteSets, UncountableSets,
        )

        size = cardinal(size)
        match size.is_finite(), size.is_countably_infinite():
            case True, _:
                return FiniteSets()
            case False, True:
                return CountablyInfiniteSets()
            case _:
                return UncountableSets()

    def set_power_category(self, codomain, exponent):
        r"""Place `Y^X` at its construction from what the constructions of `X` and `Y` fix (``OWN-22``).

        Constructing a function set computes nothing about its endpoints.
        Finiteness, countability and infinitude are read from their
        placement.  An exact size, which decides the stronger placements
        (`|Y|^0 = 1`, `|Y| <= 1`, `|Y| >= 2`), is read only from an
        endpoint presented by an enumeration from an index set: its size is
        that of the index set, a defining datum.  No cardinality or
        finiteness algorithm runs.  Such an algorithm may need a map into the
        endpoint (the augmentation of a presented module), or an enumeration
        the endpoint has not got (a predicate subgroup of a finite group,
        counted by passing over the group); the exact cardinality of `Y^X`
        stays an operation of the constructed set, computed when asked.
        """
        from sage_extensions.categories.sets.set_categories import (
            Sets, FiniteSets, InfiniteSets, CountableSets,
            CountablyInfiniteSets, UncountableSets,
        )

        finite_exponent = exponent in FiniteSets()
        finite_codomain = codomain in FiniteSets()
        if finite_exponent and finite_codomain:
            return FiniteSets()

        if finite_exponent:
            size = self._size_fixed_by_enumeration(exponent)
            if size is not None:
                size = cardinal(size)
                assert size.is_finite(), (
                    f"{exponent} is finite, but its supplied cardinality is {size}"
                )
                if size == cardinal(0):
                    return FiniteSets()
                if codomain in CountableSets() and codomain in InfiniteSets():
                    return CountablyInfiniteSets()
                if codomain in UncountableSets():
                    return UncountableSets()
            if codomain in CountableSets():
                return CountableSets()
            return Sets()

        if finite_codomain:
            size = self._size_fixed_by_enumeration(codomain)
            if size is not None:
                size = cardinal(size)
                assert size.is_finite(), (
                    f"{codomain} is finite, but its supplied cardinality is {size}"
                )
                if size.finite_value() <= 1:
                    # Even an empty codomain gives at most one function,
                    # whether or not the exponent's emptiness is decided.
                    return FiniteSets()
                if exponent in InfiniteSets():
                    return UncountableSets()
        if exponent in InfiniteSets() and codomain in InfiniteSets():
            return UncountableSets()
        return Sets()

    def _size_fixed_by_enumeration(self, endpoint):
        r"""The size of a set presented by an enumeration from an index set, else ``None``.

        Private to the placements of this owner.  A set presented by an
        enumeration ``I -> X`` has the size of ``I``; the finite ordinal
        ``[n]`` is its own index set and retains ``n``.  This reads that
        defining datum through the ``Sets`` cardinality hook, which for
        such a set reads its index set.  Any other set supplies no size
        here, so that placing a construction never runs a cardinality
        algorithm.  ``None`` asserts nothing.
        """
        from sage_extensions.categories.sets.finite_ordered_sets import (
            OrderedEnumeratedSets,
        )

        match endpoint:
            case _ if endpoint in OrderedEnumeratedSets():
                return endpoint._cardinality_decision()
            case _:
                return None

    def finite_support_power_category(self, coefficient_ring, index_set):
        r"""Place finite-support functions using placements and defining sizes only.

        Finite support on countable sets with countable coefficients is
        countable. Nontrivial coefficients embed the index set by delta
        functions; a nonempty index embeds the coefficient ring. These
        bounds need no zero-ring or cardinality algorithm at construction.
        """
        from sage_extensions.categories.rings.ring_foundation import OwnedRings
        from sage_extensions.categories.sets.set_categories import (
            Sets, FiniteSets, InfiniteSets, CountableSets,
            CountablyInfiniteSets, UncountableSets,
        )

        if index_set in FiniteSets():
            return self.set_power_category(coefficient_ring, index_set)
        coefficient_size = self._size_fixed_by_enumeration(coefficient_ring)
        if coefficient_size is not None and cardinal(coefficient_size).is_finite():
            if cardinal(coefficient_size).finite_value() <= 1:
                return FiniteSets()
        nontrivial = coefficient_ring in OwnedRings().Nontrivial() or coefficient_ring in InfiniteSets()
        if coefficient_size is not None and cardinal(coefficient_size) > cardinal(1):
            nontrivial = True
        if index_set in InfiniteSets():
            if coefficient_ring in UncountableSets() or (nontrivial and index_set in UncountableSets()):
                return UncountableSets()
            if coefficient_ring in CountableSets() and index_set in CountableSets():
                return CountablyInfiniteSets() if nontrivial else CountableSets()
            if nontrivial:
                return InfiniteSets()
        if coefficient_ring in CountableSets() and index_set in CountableSets():
            return CountableSets()
        return Sets()

    def set_subset_category(self, source, *, fixed_size=None):
        r"""Place finite-subset sets from `2^|X|` or `|[X]^k|`."""
        from sage_extensions.categories.sets.set_categories import (
            Sets, EnumeratedSets, FiniteSets, InfiniteSets, CountableSets,
            CountablyInfiniteSets, UncountableSets,
        )

        match fixed_size, source:
            case 0, _:
                return self.set_category(cardinal(1))
            case _, _ if Sets().is_provably_finite(source):
                # Every family of subsets of a finite set is finite, even
                # before the source has acquired its FiniteSets placement.
                # Its exact cardinality need not yet be computed.
                return FiniteSets()
            case _, _ if source in InfiniteSets() and source in CountableSets():
                return CountablyInfiniteSets()
            case _, _ if source in UncountableSets():
                return UncountableSets()
            case _, _ if source in CountableSets():
                return CountableSets()
            case _, _ if source in InfiniteSets():
                return InfiniteSets()
            case _:
                return Sets()

    def set_indexed_category(self, family, *, operation):
        r"""Place a finite-index product or coproduct from its defining factors.

        Unknown individual cardinalities retain only bounds supplied by their
        categories. For products, an empty factor dominates every other size.
        """
        from sage_extensions.categories.sets.set_categories import (
            Sets, EnumeratedSets, FiniteSets, InfiniteSets, CountableSets,
            CountablyInfiniteSets, UncountableSets,
        )

        index = family.index_set()
        # Finite cardinality alone does not select a list of factors.
        # Computing finite sums/products requires the actual enumeration;
        # otherwise retain only the ambient category rather than iterating
        # an index set without a chosen order.
        if index not in FiniteSets() or index not in EnumeratedSets():
            return Sets()
        factors = tuple(family(i) for i in index)
        sizes = tuple(self._size_fixed_by_enumeration(factor) for factor in factors)
        match operation:
            case "product":
                if any(size is not None and cardinal(size) == cardinal(0) for size in sizes):
                    return FiniteSets()
                if all(f in FiniteSets() for f in factors):
                    return FiniteSets()
                nonempty = all(
                    f in InfiniteSets()
                    or (size is not None and cardinal(size) > cardinal(0))
                    for f, size in zip(factors, sizes, strict=True)
                )
                if nonempty and any(f in UncountableSets() for f in factors):
                    return UncountableSets()
                if all(f in CountableSets() for f in factors):
                    if nonempty and any(f in InfiniteSets() for f in factors):
                        return CountablyInfiniteSets()
                    return CountableSets()
                if nonempty and any(f in InfiniteSets() for f in factors):
                    return InfiniteSets()
                return Sets()
            case "sum":
                if all(f in FiniteSets() for f in factors):
                    return FiniteSets()
                if any(f in UncountableSets() for f in factors):
                    return UncountableSets()
                if all(f in CountableSets() for f in factors):
                    if any(f in InfiniteSets() for f in factors):
                        return CountablyInfiniteSets()
                    return CountableSets()
                if any(f in InfiniteSets() for f in factors):
                    return InfiniteSets()
                return Sets()
            case _:
                raise ValueError(f"cardinality of indexed {operation!r} is not a sum or product")

    def an_object(self) -> Cardinal:
        r"""The cardinal three."""
        return cardinal(3)

    _MorCategory = CardinalityMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    def _repr_(self) -> str:
        return "Card: cardinalities with a unique morphism kappa -> lambda exactly when kappa <= lambda"

    def _call_(self, value: SupportsInt | AnInfinity) -> Cardinal:
        r"""Construct the cardinal a literal names.

        The literal ingress of this category's one construction, reached
        through ``Cardinalities()(value)`` once ``value`` is not already a
        cardinal: Sage's ``Infinity`` names ``aleph_0``, and an exact
        nonnegative integer names the finite cardinal.  Anything else is
        refused by the construction, not caught.
        """
        if value is Infinity:
            return aleph(0)
        integer = int(value)
        if value != integer:
            raise TypeError(
                f"a finite cardinal is given by an integer, but {value!r} is not an integer"
            )
        if integer < 0:
            raise ValueError(f"a cardinal is nonnegative, but {integer} is negative")
        return _cardinal_with_expression(_FiniteCardinal(integer))

    def Mor(
        self,
        domain: Cardinal | SupportsInt | AnInfinity,
        codomain: Cardinal | SupportsInt | AnInfinity,
    ) -> CardinalityMor:
        return CardinalityMorCategoryConstruction(self).Of(cardinal(domain), cardinal(codomain))

    class ParentMethods:
        def __init__(self, expression: _CardinalExpression, **rest) -> None:
            self._expression = expression
            super().__init__(**rest)

        def expression(self) -> _CardinalExpression:
            return self._expression

        def cardinality(self) -> Cardinal:
            r"""``|kappa| = kappa``.

            Under the von Neumann assignment a cardinal is the initial ordinal
            of its size, a set whose cardinality is that cardinal.
            """
            return self

        def sort_key(self) -> tuple[int, str]:
            return self.expression().sort_key()

        def _repr_(self) -> str:
            return self.expression().display()

        def __hash__(self) -> int:
            if self.is_finite():
                return hash(self._finite_int())
            if self.is_countably_infinite():
                return hash(Infinity)
            return hash(self.expression())

        def __eq__(self, other) -> bool:
            r"""Equality of the defining terms, with a literal read as the cardinal it names."""
            match other:
                case _ if other in Cardinalities():
                    return self.expression() == other.expression()
                case _ if other is Infinity:
                    return self.expression() == Cardinalities()(other).expression()
                case _ if _is_session_integer(other) and int(other) >= 0:
                    return self.expression() == Cardinalities()(other).expression()
                case _:
                    return False

        def __ne__(self, other) -> bool:
            return not self == other

        def __lt__(self, other) -> bool | Predicate:
            return Cardinalities().lt(self, other)

        def __le__(self, other) -> bool | Predicate:
            return Cardinalities().le(self, other)

        def __gt__(self, other) -> bool | Predicate:
            return Cardinalities().gt(self, other)

        def __ge__(self, other) -> bool | Predicate:
            return Cardinalities().ge(self, other)

        def __add__(self, other):
            return Cardinalities().sum(self, other)

        __radd__ = __add__

        def __mul__(self, other):
            return Cardinalities().product(self, other)

        __rmul__ = __mul__

        def __pow__(self, exponent):
            return Cardinalities().power(self, exponent)

        def __rpow__(self, base):
            return Cardinalities().power(base, self)

        def is_finite(self) -> bool:
            expression = self.expression()
            assert expression.is_normal_form(), (
                f"cannot decide whether the cardinal {self} is finite: it is not a finite sum, product, or "
                "supremum of known cardinals"
            )
            return expression.is_finite()

        def is_infinite(self) -> bool:
            return not self.is_finite()

        def is_aleph(self) -> bool:
            return self.expression().is_aleph()

        def is_continuum(self) -> bool:
            return self.expression().is_continuum()

        def is_countable(self) -> bool:
            return self.is_finite() or self.is_countably_infinite()

        def is_uncountable(self) -> bool:
            r"""Whether ``kappa > aleph_0``.

            A countable cardinal is not; an aleph beyond ``aleph_0`` and a
            power ``kappa^lambda`` with infinite exponent are; a supremum is
            when one of its terms is.
            """
            expression = self.expression()
            assert expression.is_normal_form(), (
                f"cannot decide whether the cardinal {self} is uncountable: it is not a finite sum, product, "
                "or supremum of known cardinals"
            )
            if self.is_countable():
                return False
            return any(not term.is_countable() for term in expression.supremum_terms(self))

        def is_countably_infinite(self) -> bool:
            return self.expression().is_countably_infinite()

        def is_uncountably_infinite(self) -> bool:
            return self.is_infinite() and self.is_uncountable()

        def aleph_index(self) -> Ordinal:
            assert self.is_aleph(), f"{self} is not an aleph cardinal, so it has no aleph index"
            return self.expression().index

        def initial_ordinal(self) -> Ordinal:
            return omega(self.aleph_index())

        def _finite_int(self) -> int:
            assert self.is_finite(), f"{self} is not a finite cardinal"
            return self.expression().value

        def finite_value(self) -> int:
            r"""Return the ordinary nonnegative integer representing this finite cardinal."""
            return self._finite_int()

        def __int__(self) -> int:
            if not self.is_finite():
                raise TypeError(f"cannot convert infinite cardinal {self} to integer")
            return self._finite_int()

        def __index__(self) -> int:
            return int(self)

        def _integer_(self, ring=None):
            if not self.is_finite():
                raise TypeError(f"cannot convert infinite cardinal {self} to an integer")
            return ZZ(self._finite_int())

        def _rational_(self):
            if not self.is_finite():
                raise TypeError(f"cannot convert infinite cardinal {self} to a rational")
            from sage.rings.rational_field import QQ as SageQQ

            return SageQQ(self._finite_int())

        def Mor(
            self,
            codomain: Cardinal | SupportsInt | AnInfinity,
            category: Category | None = None,
        ) -> CardinalityMor:
            if category is not None and category is not Cardinalities():
                raise TypeError(
                    f"a morphism of cardinals lies in the category of cardinals, not in {category}"
                )
            return Cardinalities().Mor(self, codomain)

    def zero(self) -> Cardinal:
        return cardinal(0)

    def one(self) -> Cardinal:
        return cardinal(1)

    def sum(
        self,
        *summands: Cardinal | SupportsInt | AnInfinity,
    ) -> Cardinal:
        result = self.zero()
        for summand in map(cardinal, summands):
            if result.is_finite() and summand.is_finite():
                result = cardinal(result._finite_int() + summand._finite_int())
            elif result.is_finite():
                result = summand
            elif summand.is_infinite():
                result = self.supremum(result, summand)
        return result

    def product(
        self,
        *factors: Cardinal | SupportsInt | AnInfinity,
    ) -> Cardinal:
        result = self.one()
        for factor in map(cardinal, factors):
            if result == 0 or factor == 0:
                return cardinal(0)
            if result.is_finite() and factor.is_finite():
                result = cardinal(result._finite_int() * factor._finite_int())
            elif result.is_finite():
                result = factor
            elif factor.is_infinite():
                result = self.supremum(result, factor)
        return result

    def indexed_sum(
        self,
        index_set: Parent,
        summands: Callable[[IndexT], Cardinal | SupportsInt | AnInfinity],
    ) -> Cardinal:
        size = cardinal(index_set.cardinality())
        if size.is_finite():
            return self.sum(*(summands(index) for index in index_set))
        return _cardinal_with_expression(_IndexedSumCardinal(index_set, summands))

    def indexed_product(
        self,
        index_set: Parent,
        factors: Callable[[IndexT], Cardinal | SupportsInt | AnInfinity],
    ) -> Cardinal:
        size = cardinal(index_set.cardinality())
        if size.is_finite():
            return self.product(*(factors(index) for index in index_set))
        return _cardinal_with_expression(_IndexedProductCardinal(index_set, factors))

    def power(
        self,
        base: Cardinal | SupportsInt | AnInfinity,
        exponent: Cardinal | SupportsInt | AnInfinity,
    ) -> Cardinal:
        r"""``kappa^lambda``.

        With a finite exponent the power is computed or equals the infinite
        base.  With an infinite exponent ``lambda``, a base ``kappa`` with
        ``2 <= kappa <= lambda`` gives ``kappa^lambda = 2^lambda``, and the
        remaining reductions belong to the forms of the exponent and the base:
        a supremum distributes, and a power multiplies exponents.
        """
        cardinal_base = cardinal(base)
        cardinal_exponent = cardinal(exponent)
        if cardinal_exponent == 0:
            return cardinal(1)
        if cardinal_base == 0:
            return cardinal(0)
        if cardinal_base == 1:
            return cardinal(1)
        if cardinal_exponent.is_finite():
            if cardinal_base.is_finite():
                return cardinal(cardinal_base._finite_int() ** cardinal_exponent._finite_int())
            return cardinal_base
        if cardinal_base.is_finite() or self._proves_le(cardinal_base, cardinal_exponent):
            cardinal_base = cardinal(2)
        return cardinal_exponent.expression().power_with_this_exponent(cardinal_base, cardinal_exponent)

    def sum_morphism(
        self,
        *morphisms: CardinalityMorphism,
    ) -> CardinalityMorphism:
        r"""Apply cardinal addition to a finite family of comparison morphisms."""
        source = self.sum(*(morphism.domain() for morphism in morphisms))
        target = self.sum(*(morphism.codomain() for morphism in morphisms))
        return self.Mor(source, target).unique_morphism()

    def product_morphism(
        self,
        *morphisms: CardinalityMorphism,
    ) -> CardinalityMorphism:
        r"""Apply cardinal multiplication to a finite family of comparison morphisms."""
        source = self.product(*(morphism.domain() for morphism in morphisms))
        target = self.product(*(morphism.codomain() for morphism in morphisms))
        return self.Mor(source, target).unique_morphism()

    def power_morphism(
        self,
        base_morphism: CardinalityMorphism,
        exponent_morphism: CardinalityMorphism,
    ) -> CardinalityMorphism:
        r"""Apply exponentiation to comparisons when the source base is nonzero."""
        nonzero = self.le(1, base_morphism.domain())
        assert nonzero is True or nonzero is False, (
            f"cannot apply exponentiation to {base_morphism}: whether its source base "
            f"{base_morphism.domain()} is nonzero, {nonzero}, is not decided by the represented cardinal laws"
        )
        if nonzero is False:
            raise ValueError(
                f"exponentiation is monotone in the exponent only for a nonzero base, but the base "
                f"{base_morphism.domain()} is zero"
            )
        source = self.power(
            base_morphism.domain(),
            exponent_morphism.domain(),
        )
        target = self.power(
            base_morphism.codomain(),
            exponent_morphism.codomain(),
        )
        return self.Mor(source, target).unique_morphism()

    def supremum(
        self,
        *cardinal_numbers: Cardinal | SupportsInt | AnInfinity,
    ) -> Cardinal:
        r"""The supremum of finitely many cardinals: the maximal terms, or their undecided supremum."""
        terms: list[Cardinal] = [
            term
            for cardinal_number in map(cardinal, cardinal_numbers)
            for term in cardinal_number.expression().supremum_terms(cardinal_number)
        ]
        assert terms, (
            "the supremum of finitely many cardinals needs at least one cardinal, but none was given"
        )
        maximal_terms: list[Cardinal] = []
        for candidate in sorted(set(terms), key=lambda term: term.sort_key()):
            if any(self._proves_le(candidate, term) for term in maximal_terms):
                continue
            maximal_terms = [term for term in maximal_terms if not self._proves_le(term, candidate)]
            maximal_terms.append(candidate)
        maximal_terms.sort(key=lambda term: term.sort_key())
        if len(maximal_terms) == 1:
            return maximal_terms[0]
        return _cardinal_with_expression(_SupremumCardinal(tuple(maximal_terms)))

    def le(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool | Predicate:
        r"""Decide ``source <= target``, or return the proposition ``le(source, target)``.

        ``True`` when the represented laws prove ``source <= target``;
        ``False`` when they prove ``target < source``, which excludes
        ``source <= target`` by the Cantor--Schroeder--Bernstein theorem;
        otherwise the proposition, which ``ask`` answers ``Unknown`` (`DEF-06`).
        """
        match (self._proves_le(source, target), self._proves_lt(target, source)):
            case (True, _):
                return True
            case (_, True):
                return False
            case _:
                from sage_extensions.logic import AtomicProposition

                return AtomicProposition("le", cardinal(source), cardinal(target))

    def _proves_le(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool:
        r"""Whether the represented laws prove ``source <= target``.

        A supremum is below ``target`` when each of its terms is, and
        ``source`` is below a supremum when it is below one of its terms.
        ``False`` means that no proof was found, not that the inequality fails.
        """
        left = cardinal(source)
        right = cardinal(target)
        if left == right:
            return True
        return all(
            any(
                self._le_terms(left_term, right_term)
                for right_term in right.expression().supremum_terms(right)
            )
            for left_term in left.expression().supremum_terms(left)
        )

    def _le_terms(self, left: Cardinal, right: Cardinal) -> bool:
        r"""Decide ``left <= right`` for two cardinals, neither a supremum."""
        if left == right:
            return True
        if not (left.expression().is_normal_form() and right.expression().is_normal_form()):
            return False
        if left.is_finite():
            return not right.is_finite() or left._finite_int() <= right._finite_int()
        if right.is_finite():
            return False
        if left.is_aleph() and right.is_aleph():
            return left.aleph_index() <= right.aleph_index()
        if left.is_countably_infinite():
            return True
        if left.is_aleph() and left.aleph_index() == 1 and right.is_uncountable():
            return True
        return right.expression().bounds_above(left)

    def lt(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool | Predicate:
        r"""Decide ``source < target``, or return the proposition ``lt(source, target)``.

        ``True`` when the represented laws prove ``source < target``;
        ``False`` when they prove ``target <= source``, which excludes
        ``source < target`` by the Cantor--Schroeder--Bernstein theorem;
        otherwise the proposition, which ``ask`` answers ``Unknown`` (`DEF-06`).
        """
        match (self._proves_lt(source, target), self._proves_le(target, source)):
            case (True, _):
                return True
            case (_, True):
                return False
            case _:
                from sage_extensions.logic import AtomicProposition

                return AtomicProposition("lt", cardinal(source), cardinal(target))

    def _proves_lt(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool:
        r"""Whether the represented laws prove ``source < target``; ``False`` means that no proof was found."""
        left = cardinal(source)
        right = cardinal(target)
        if left == right:
            return False
        return all(
            any(
                self._lt_terms(left_term, right_term)
                for right_term in right.expression().supremum_terms(right)
            )
            for left_term in left.expression().supremum_terms(left)
        )

    def _lt_terms(self, left: Cardinal, right: Cardinal) -> bool:
        r"""Decide ``left < right`` for two cardinals, neither a supremum."""
        if left == right:
            return False
        if not (left.expression().is_normal_form() and right.expression().is_normal_form()):
            return False
        if left.is_finite():
            return not right.is_finite() or left._finite_int() < right._finite_int()
        if right.is_finite():
            return False
        if left.is_aleph() and right.is_aleph():
            return left.aleph_index() < right.aleph_index()
        if left.is_countably_infinite() and right.is_uncountable():
            return True
        return right.expression().strictly_bounds_above(left)

    def ge(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool | Predicate:
        return self.le(target, source)

    def gt(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool | Predicate:
        return self.lt(target, source)

    def compare(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> CardinalComparison:
        r"""The strongest relation between ``source`` and ``target`` that the represented laws decide.

        ``INCOMPARABLE`` means that neither ``source <= target`` nor
        ``target <= source`` is decided.
        """
        left = cardinal(source)
        right = cardinal(target)
        if left == right:
            return CardinalComparison.EQUAL
        if self.lt(left, right) is True:
            return CardinalComparison.LESS
        if self.lt(right, left) is True:
            return CardinalComparison.GREATER
        if self.le(left, right) is True:
            return CardinalComparison.LESS_OR_EQUAL
        if self.le(right, left) is True:
            return CardinalComparison.GREATER_OR_EQUAL
        return CardinalComparison.INCOMPARABLE

    def are_incomparable(
        self,
        source: Cardinal | SupportsInt | AnInfinity,
        target: Cardinal | SupportsInt | AnInfinity,
    ) -> bool:
        r"""Whether the represented cardinal laws leave both ``source <= target`` and ``target <= source`` undecided.

        ``True`` exactly when neither comparison is decided ``True`` or
        ``False``.  This is a statement about the represented laws, not
        incomparability in ZFC: under the axiom of choice any two cardinals
        are comparable.
        """
        forward = self.le(source, target)
        backward = self.le(target, source)
        return forward is not True and forward is not False and backward is not True and backward is not False


Cardinal = Cardinalities().ObjectType


class _OrdinalExpression(ABC):
    r"""A canonical order type represented by its Cantor-normal-form data.

    Finite and initial ordinals retain their distinguished constructors.  Every
    other represented ordinal is stored in Cantor normal form

    ``omega^beta_0 c_0 + ... + omega^beta_r c_r``,

    with decreasing exponents and positive finite coefficients.  An
    uncountable initial ordinal ``kappa`` is an epsilon ordinal
    (``omega^kappa = kappa``), so :class:`_InitialOrdinal` exposes that
    one-term CNF virtually instead of recursively storing itself.
    """

    @abstractmethod
    def display(self) -> str:
        r"""The notation of this term."""
        ...

    @abstractmethod
    def denoted_cardinality(self) -> Cardinal:
        r"""``|alpha|`` for the ordinal this term denotes."""
        ...

    def is_finite(self) -> bool:
        return False

    def is_initial(self) -> bool:
        return False

    @abstractmethod
    def cnf_terms(
        self,
        ordinal_number: Ordinal,
    ) -> tuple[tuple[Ordinal, Integer], ...]:
        r"""The decreasing Cantor-normal-form terms of ``ordinal_number``."""
        ...



@dataclass(frozen=True)
class _FiniteOrdinal(_OrdinalExpression):
    value: Integer

    def display(self) -> str:
        return repr(self.value)

    def denoted_cardinality(self) -> Cardinal:
        return cardinal(self.value)

    def is_finite(self) -> bool:
        return True

    def cnf_terms(
        self,
        ordinal_number: Ordinal,
    ) -> tuple[tuple[Ordinal, Integer], ...]:
        if self.value == 0:
            return ()
        return ((Ordinals().zero(), self.value),)


@dataclass(frozen=True)
class _InitialOrdinal(_OrdinalExpression):
    index: Ordinal

    def display(self) -> str:
        return f"ω_{self.index}"

    def denoted_cardinality(self) -> Cardinal:
        r"""``|omega_alpha| = aleph_alpha``."""
        return aleph(self.index)

    def is_initial(self) -> bool:
        return True

    def cnf_terms(
        self,
        ordinal_number: Ordinal,
    ) -> tuple[tuple[Ordinal, Integer], ...]:
        # omega_0 = omega^1.  Every later initial ordinal kappa is uncountable,
        # hence omega^kappa = kappa: for beta < kappa, omega^beta < kappa
        # because kappa is initial, while beta <= omega^beta makes the powers
        # cofinal in kappa.
        if self.index == 0:
            return ((Ordinals().one(), ZZ.one()),)
        return ((ordinal_number, ZZ.one()),)


@dataclass(frozen=True)
class _CantorNormalForm(_OrdinalExpression):
    r"""A non-finite, non-initial ordinal in canonical Cantor normal form."""

    terms: tuple[tuple[Ordinal, Integer], ...]

    def denoted_cardinality(self) -> Cardinal:
        # |omega^beta| = max(aleph_0, |beta|) for beta > 0; a finite
        # Cantor sum does not change the maximum.
        return Cardinalities().supremum(
            aleph(0),
            *(exponent.cardinality() for exponent, _coefficient in self.terms),
        )

    def cnf_terms(
        self,
        ordinal_number: Ordinal,
    ) -> tuple[tuple[Ordinal, Integer], ...]:
        return self.terms

    def display(self) -> str:
        def display_term(exponent: Ordinal, coefficient: Integer) -> str:
            if exponent == 0:
                return repr(coefficient)
            if exponent == 1:
                base = "ω_0"
            elif exponent.is_initial() and exponent.initial_index() != 0:
                # An uncountable initial ordinal kappa is omega^kappa.
                base = repr(exponent)
            else:
                base = f"ω_0^({exponent})"
            return base if coefficient == 1 else f"{base}*{coefficient}"

        return " + ".join(
            display_term(exponent, coefficient)
            for exponent, coefficient in self.terms
        )


class OrdinalMorphism(CategoricalMor.ElementMethods):
    r"""Methods for the generated comparison arrow ``alpha -> beta`` when ``alpha <= beta``."""

    def __init__(self, parent: OrdinalMor) -> None:
        Morphism.__init__(self, parent)

    def is_identity(self) -> bool:
        return self.domain() is self.codomain()

    def __mul__(self, other):
        r"""Compose two ordinal comparisons."""
        other_parent = element_parent(other)
        match other_parent:
            case CategoricalMor() if (
                other_parent.mor_category().is_subcategory(Ordinals())
                and other.codomain() is self.domain()
            ):
                pass
            case _:
                return NotImplemented
        return Ordinals().Mor(other.domain(), self.codomain()).unique_morphism()

    def _repr_(self) -> str:
        return f"{self.domain()} <= {self.codomain()}"


class OrdinalMor(CategoricalMor):
    r"""The zero-or-one-element Mor object of the ordinal order."""

    ElementMethods = OrdinalMorphism

    def __init__(
        self,
        mor_family: MorCategoryConstruction,
        domain: Parent,
        codomain: Parent,
    ) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def is_empty(self) -> bool:
        return not Ordinals().le(self.domain(), self.codomain())

    def cardinality(self) -> Cardinal:
        return cardinal(0 if self.is_empty() else 1)

    @cached_method
    def unique_morphism(self) -> OrdinalMorphism:
        empty = self.is_empty()
        if empty is True:
            raise ValueError(
                f"there is no morphism {self.domain()} -> {self.codomain()} of ordinals: "
                f"{self.domain()} is not <= {self.codomain()}"
            )
        return self.element_class(self)

    def _element_constructor_(self, morphism=None):
        if morphism is not None and morphism.parent() is not self:
            raise ValueError(f"{morphism} is not in {self}")
        return self.unique_morphism()

    @object_level
    def identity(self) -> OrdinalMorphism:
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        return self.unique_morphism()


class OrdinalMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self) -> type[OrdinalMor]:
        return OrdinalMor


class Ordinals(OwnedCategory):
    r"""The thin category ``Ord`` of represented ordinals under ``<=``.

    Ordinals are objects, not elements of a distinguished semiring object.
    Natural (Hessenberg) sum and product are the commutative-semiring
    operations on these objects.  Ordinary ordinal sum, product and power
    remain object operations because they are not that commutative semiring
    structure.
    """

    _MorCategory = OrdinalMorCategoryConstruction

    def an_object(self) -> Ordinal:
        return self(3)

    def super_categories(self):
        return [Objects()]

    def _repr_(self) -> str:
        return "Ord: ordinals with a unique morphism alpha -> beta exactly when alpha <= beta"

    def _call_(self, value: Ordinal | Cardinal | SupportsInt) -> Ordinal:
        if value in self:
            return value
        match value:
            case _ if value in Cardinalities():
                if not value.is_finite():
                    raise ValueError(
                        f"the cardinal {value} is not itself an ordinal in this literal ingress: only finite "
                        "cardinals identify canonically with their finite initial ordinals"
                    )
                integer = value.finite_value()
            case _ if _is_session_integer(value):
                integer = int(value)
            case _:
                raise ValueError(
                    f"{value!r} does not name an ordinal here: use an ordinal, a finite cardinal, or an exact "
                    "nonnegative integer"
                )
        if integer < 0:
            raise ValueError(f"an ordinal is nonnegative, but {integer} is negative")
        return _ordinal_with_expression(_FiniteOrdinal(ZZ(integer)))

    def from_expression(self, expression: _OrdinalExpression) -> Ordinal:
        return _ordinal_with_expression(expression)

    def Mor(
        self,
        domain: Ordinal | Cardinal | SupportsInt,
        codomain: Ordinal | Cardinal | SupportsInt,
    ) -> OrdinalMor:
        return OrdinalMorCategoryConstruction(self).Of(self(domain), self(codomain))

    class ParentMethods:
        def __init__(self, expression: _OrdinalExpression, **rest) -> None:
            self._expression = expression
            super().__init__(**rest)

        def expression(self) -> _OrdinalExpression:
            return self._expression

        def cnf_terms(self) -> tuple[tuple[Ordinal, Integer], ...]:
            r"""The canonical Cantor-normal-form terms of this ordinal."""
            return self.expression().cnf_terms(self)

        def _repr_(self) -> str:
            return self.expression().display()

        def __hash__(self) -> int:
            if self.expression().is_finite():
                return hash(int(self.expression().value))
            return hash(self.expression())

        def __eq__(self, other) -> bool:
            r"""Equality of the defining terms, with finite literals read as their ordinals."""
            match other:
                case _ if other in Ordinals():
                    return self.expression() == other.expression()
                case _ if other in Cardinalities() and other.is_finite():
                    return self.expression() == Ordinals()(other).expression()
                case _ if _is_session_integer(other) and int(other) >= 0:
                    return self.expression() == Ordinals()(other).expression()
                case _:
                    return False

        def __ne__(self, other) -> bool:
            return not self == other

        def __le__(self, other):
            return Ordinals().le(self, other)

        def __lt__(self, other):
            return Ordinals().lt(self, other)

        def __ge__(self, other):
            return Ordinals().ge(self, other)

        def __gt__(self, other):
            return Ordinals().gt(self, other)

        def __add__(self, other):
            return Ordinals().natural_sum(self, other)

        def __radd__(self, other):
            return Ordinals().natural_sum(other, self)

        def __mul__(self, other):
            return Ordinals().natural_product(self, other)

        def __rmul__(self, other):
            return Ordinals().natural_product(other, self)

        def ordinal_sum(self, other: Ordinal | SupportsInt) -> Ordinal:
            return Ordinals().ordinal_sum(self, other)

        def ordinal_product(self, other: Ordinal | SupportsInt) -> Ordinal:
            return Ordinals().ordinal_product(self, other)

        def ordinal_power(self, exponent: Ordinal | SupportsInt) -> Ordinal:
            return Ordinals().ordinal_power(self, exponent)

        def is_initial(self) -> bool:
            return self.expression().is_initial()

        def initial_index(self) -> Ordinal:
            assert self.is_initial(), f"{self} is not an initial ordinal, so it has no initial index"
            return self.expression().index

        def cardinality(self) -> Cardinal:
            r"""``|alpha|``, the cardinality of the von Neumann ordinal ``alpha``."""
            return self.expression().denoted_cardinality()

        def Mor(
            self,
            codomain: Ordinal | Cardinal | SupportsInt,
            category: Category | None = None,
        ) -> OrdinalMor:
            if category is not None and category is not Ordinals():
                raise TypeError(
                    f"a morphism of ordinals lies in the category of ordinals, not in {category}"
                )
            return Ordinals().Mor(self, codomain)

    def zero(self) -> Ordinal:
        return self(0)

    def one(self) -> Ordinal:
        return self(1)

    def initial(self, index: Ordinal | SupportsInt) -> Ordinal:
        return self.from_expression(_InitialOrdinal(self(index)))

    def _from_cnf_terms(self, terms) -> Ordinal:
        r"""Construct the unique represented ordinal with these CNF terms."""
        combined: dict[Ordinal, Integer] = {}
        for exponent, coefficient in terms:
            exponent = self(exponent)
            coefficient = ZZ(coefficient)
            if coefficient < 0:
                raise ValueError(
                    f"a Cantor-normal-form coefficient is nonnegative, but got {coefficient}"
                )
            if coefficient == 0:
                continue
            combined[exponent] = combined.get(exponent, ZZ.zero()) + coefficient
        if not combined:
            return self.zero()
        normalized = tuple(
            sorted(
                combined.items(),
                key=cmp_to_key(
                    lambda left, right: -self.compare(left[0], right[0])
                ),
            )
        )
        if len(normalized) == 1:
            exponent, coefficient = normalized[0]
            if exponent == 0:
                return self(coefficient)
            if coefficient == 1:
                if exponent == 1:
                    return self.initial(0)
                if exponent.is_initial() and exponent.initial_index() != 0:
                    return exponent
        return self.from_expression(_CantorNormalForm(normalized))

    def _omega_power(
        self,
        exponent: Ordinal | SupportsInt,
        coefficient: SupportsInt = 1,
    ) -> Ordinal:
        r"""Return omega to the exponent times a positive finite coefficient."""
        coefficient = ZZ(coefficient)
        if coefficient <= 0:
            raise ValueError(
                f"a Cantor-normal-form coefficient is positive, but got {coefficient}"
            )
        return self._from_cnf_terms(((self(exponent), coefficient),))

    def ordinal_sum(
        self,
        left: Ordinal | SupportsInt,
        right: Ordinal | SupportsInt,
    ) -> Ordinal:
        r"""The ordinary ordinal sum, computed on Cantor normal forms."""
        source = self(left)
        target = self(right)
        right_terms = target.cnf_terms()
        if not right_terms:
            return source
        left_terms = source.cnf_terms()
        if not left_terms:
            return target
        right_exponent, right_coefficient = right_terms[0]
        result: list[tuple[Ordinal, Integer]] = []
        for exponent, coefficient in left_terms:
            comparison = self.compare(exponent, right_exponent)
            if comparison > 0:
                result.append((exponent, coefficient))
                continue
            if comparison == 0:
                result.append(
                    (exponent, coefficient + right_coefficient)
                )
                result.extend(right_terms[1:])
                return self._from_cnf_terms(result)
            result.extend(right_terms)
            return self._from_cnf_terms(result)
        result.extend(right_terms)
        return self._from_cnf_terms(result)

    def ordinal_product(
        self,
        left: Ordinal | SupportsInt,
        right: Ordinal | SupportsInt,
    ) -> Ordinal:
        r"""The ordinary ordinal product, computed on Cantor normal forms."""
        source = self(left)
        target = self(right)
        source_terms = source.cnf_terms()
        target_terms = target.cnf_terms()
        if not source_terms or not target_terms:
            return self.zero()
        source_exponent, source_coefficient = source_terms[0]
        result: list[tuple[Ordinal, Integer]] = []
        for exponent, coefficient in target_terms:
            if exponent == 0:
                result.append(
                    (source_exponent, source_coefficient * coefficient)
                )
                result.extend(source_terms[1:])
                continue
            result.append(
                (
                    self.ordinal_sum(source_exponent, exponent),
                    coefficient,
                )
            )
        return self._from_cnf_terms(result)

    def _finite_ordinal_power(
        self,
        base: Ordinal,
        exponent: Integer,
    ) -> Ordinal:
        r"""Return a finite ordinal power by repeated squaring."""
        result = self.one()
        factor = base
        remaining = ZZ(exponent)
        while remaining:
            if remaining % 2:
                result = self.ordinal_product(result, factor)
            remaining //= 2
            if remaining:
                factor = self.ordinal_product(factor, factor)
        return result

    def _limit_divided_by_omega(self, limit: Ordinal) -> Ordinal:
        r"""Return q with omega*q = limit for a represented nonzero limit."""
        quotient_terms = []
        for exponent, coefficient in limit.cnf_terms():
            assert exponent != 0, (
                f"{limit} is not a limit ordinal: its Cantor normal form has a finite tail"
            )
            if exponent.expression().is_finite():
                quotient_exponent = self(exponent.expression().value - 1)
            else:
                quotient_exponent = exponent
            quotient_terms.append((quotient_exponent, coefficient))
        assert quotient_terms, "0 is not a nonzero limit ordinal"
        return self._from_cnf_terms(quotient_terms)

    def ordinal_power(
        self,
        base: Ordinal | SupportsInt,
        exponent: Ordinal | SupportsInt,
    ) -> Ordinal:
        r"""The ordinary ordinal power in canonical Cantor normal form."""
        base_ordinal = self(base)
        power = self(exponent)
        if power == 0:
            return self.one()
        if base_ordinal == 0:
            return self.zero()
        if base_ordinal == 1:
            return self.one()
        if power.expression().is_finite():
            return self._finite_ordinal_power(
                base_ordinal,
                power.expression().value,
            )

        power_terms = power.cnf_terms()
        finite_tail = ZZ.zero()
        if power_terms[-1][0] == 0:
            finite_tail = power_terms[-1][1]
            limit = self._from_cnf_terms(power_terms[:-1])
        else:
            limit = power
        assert limit != 0, (
            f"{power} was classified as infinite but has no nonzero limit part"
        )

        if base_ordinal.expression().is_finite():
            limit_exponent = self._limit_divided_by_omega(limit)
        else:
            leading_exponent = base_ordinal.cnf_terms()[0][0]
            limit_exponent = self.ordinal_product(
                leading_exponent,
                limit,
            )
        limit_power = self._omega_power(limit_exponent)
        if finite_tail == 0:
            return limit_power
        return self.ordinal_product(
            limit_power,
            self._finite_ordinal_power(base_ordinal, finite_tail),
        )

    def natural_sum(self, *summands) -> Ordinal:
        r"""The Hessenberg sum: add equal CNF coefficients termwise."""
        terms = []
        for summand in map(self, summands):
            terms.extend(summand.cnf_terms())
        return self._from_cnf_terms(terms)

    def natural_product(self, *factors) -> Ordinal:
        r"""The Hessenberg product: polynomial multiplication of CNFs."""
        result = self.one()
        for factor in map(self, factors):
            if result == 0 or factor == 0:
                return self.zero()
            products = []
            for left_exponent, left_coefficient in result.cnf_terms():
                for right_exponent, right_coefficient in factor.cnf_terms():
                    products.append(
                        (
                            self.natural_sum(
                                left_exponent,
                                right_exponent,
                            ),
                            left_coefficient * right_coefficient,
                        )
                    )
            result = self._from_cnf_terms(products)
        return result

    def natural_sum_morphism(self, *morphisms: OrdinalMorphism) -> OrdinalMorphism:
        source = self.natural_sum(*(morphism.domain() for morphism in morphisms))
        target = self.natural_sum(*(morphism.codomain() for morphism in morphisms))
        return self.Mor(source, target).unique_morphism()

    def natural_product_morphism(self, *morphisms: OrdinalMorphism) -> OrdinalMorphism:
        source = self.natural_product(*(morphism.domain() for morphism in morphisms))
        target = self.natural_product(*(morphism.codomain() for morphism in morphisms))
        return self.Mor(source, target).unique_morphism()

    def compare(
        self,
        left: Ordinal | Cardinal | SupportsInt,
        right: Ordinal | Cardinal | SupportsInt,
    ) -> int:
        r"""Compare canonical Cantor normal forms lexicographically."""
        source = self(left)
        target = self(right)
        if source is target or source.expression() == target.expression():
            return 0
        if source.is_initial() and target.is_initial():
            return self.compare(
                source.initial_index(),
                target.initial_index(),
            )
        source_terms = source.cnf_terms()
        target_terms = target.cnf_terms()
        for (source_exponent, source_coefficient), (
            target_exponent,
            target_coefficient,
        ) in zip(source_terms, target_terms):
            if source_exponent is target_exponent:
                exponent_comparison = 0
            else:
                exponent_comparison = self.compare(
                    source_exponent,
                    target_exponent,
                )
            if exponent_comparison:
                return exponent_comparison
            if source_coefficient < target_coefficient:
                return -1
            if source_coefficient > target_coefficient:
                return 1
        if len(source_terms) < len(target_terms):
            return -1
        return 1

    def le(
        self,
        left: Ordinal | Cardinal | SupportsInt,
        right: Ordinal | Cardinal | SupportsInt,
    ) -> bool:
        return self.compare(left, right) <= 0

    def lt(self, left, right) -> bool:
        return self.compare(left, right) < 0

    def ge(self, left, right) -> bool:
        return self.compare(left, right) >= 0

    def gt(self, left, right) -> bool:
        return self.compare(left, right) > 0

    def proves_le(
        self,
        left: Ordinal | Cardinal | SupportsInt,
        right: Ordinal | Cardinal | SupportsInt,
    ) -> bool:
        return self.le(left, right)


Ordinal = Ordinals().ObjectType
Ord = Ordinals()


@cached_function
def _ordinal_with_expression(expression: _OrdinalExpression) -> Ordinal:
    return _object_of(Ordinals(), expression=expression)


def ordinal(value: Ordinal | SupportsInt) -> Ordinal:
    return Ordinals()(value)


def omega(index: Ordinal | SupportsInt) -> Ordinal:
    return Ordinals().initial(index)


omega0 = omega(0)


@cached_function
def _cardinal_with_expression(expression: _CardinalExpression) -> Cardinal:
    return _object_of(Cardinalities(), expression=expression)


def cardinal(
    value: Cardinal | SupportsInt | AnInfinity,
) -> Cardinal:
    r"""Notation for ``Cardinalities()(value)``: ``value`` itself when it is a cardinal."""
    return Cardinalities()(value)


def aleph(index: Ordinal | SupportsInt) -> Cardinal:
    return _cardinal_with_expression(_AlephCardinal(ordinal(index)))


aleph0 = aleph(0)
continuum = cardinal(2) ** aleph0


__all__ = [
    "CardinalComparison",
    "Cardinalities",
    "CardinalityMor",
    "CardinalityMorphism",
    "Ord",
    "OrdinalMor",
    "OrdinalMorphism",
    "Ordinals",
    "aleph",
    "aleph0",
    "cardinal",
    "continuum",
    "omega",
    "omega0",
    "ordinal",
]
