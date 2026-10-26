"""Nonunital semirings, their unital and additive-group refinements, and Mors.

The natural numbers are the initial owned semiring. Ring objects refine the
semiring Mor theory by their stronger ring Mor theory, while every unital ring
still receives the unique semiring morphism from the natural numbers.
"""

from sage.categories.map import Map
from sage.rings.integer_ring import ZZ as SageZZ
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoryPacketMethods,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.group.magmas import (
    AdditiveGroups,
    AdditiveMonoids,
    MagmaMor,
    Monoids,
    Semigroups,
)
from sage_extensions.refine import RealizationHook
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class NonUnitalSemiringMor(MagmaMor):
    r"""Maps preserving addition, zero and multiplication.

    The actual fixed Mor supergraph supplies the additive-monoid and
    multiplicative-semigroup operations to its generated arrow class.
    There is no multiplicative-unit preservation requirement. Composition
    is the existing operation-preserving map composition inherited from
    those owners, and the constructor and identity are inherited from
    MagmaMor. As with that constructor, supplying defining map data declares
    the required laws. This does not decide membership of a previously
    constructed weaker arrow: unchanged reuse and membership require the
    actual stronger fixed-Mor graph.
    """


class NonUnitalSemiringMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return NonUnitalSemiringMor


class OwnedNonUnitalSemirings(CategoryPacketMethods, OwnedCategory):
    r"""Associative nonunital semirings.

    Addition is a commutative monoid with zero; multiplication is a
    semigroup law. Both distributive laws and ``0*x = x*0 = 0`` hold.
    No multiplicative identity or additive inverse is required. These are
    Mathlib's ``NonUnitalSemiring`` objects (Algebra/Ring/Defs); their maps
    are ``NonUnitalRingHom`` (Algebra/Ring/Hom/Defs).
    """

    _MorCategory = NonUnitalSemiringMorCategoryConstruction

    @classmethod
    def _repr_object_names(cls):
        return "nonunital semirings"

    def an_object(self):
        r"""The natural numbers, whose extra multiplicative unit is retained."""
        from sage_extensions.categories.sets.set_categories import NN

        return NN

    def super_categories(self):
        return [Semigroups(), AdditiveMonoids().AdditiveCommutative()]

    class ParentMethods:
        @RealizationHook
        def _reducedness_decision(self):
            r"""Protected decision of the absence of nonzero nilpotents.

            Only is_reduced calls this hook. A more specific category or
            owned realization may decide the positive-power predicate.
            Otherwise retain the proposition without selecting a nilradical
            representation or requiring commutative multiplication.
            """
            from sage_extensions.logic import AtomicProposition

            return AtomicProposition("is_reduced", self)

        def is_reduced(self):
            r"""Whether an element with a zero positive power must itself be zero.

            Positive powers use the associative multiplication and zero;
            this condition requires neither a multiplicative identity,
            additive inverses nor commutative multiplication. The nonunital
            semiring is the weakest declared common ancestor carrying that
            structure. A missing decision remains an owned proposition.
            """
            return self._reducedness_decision()

    class Commutative(CategoryWithAxiom):
        r"""Nonunital semirings whose multiplication is commutative."""

        @classmethod
        def _repr_object_names(cls):
            return "commutative nonunital semirings"

        def an_object(self):
            return OwnedNonUnitalSemirings().an_object()

        class ParentMethods:
            @RealizationHook
            def _nilradical_decision(self):
                r"""Protected represented nilradical, or None.

                Only nilradical calls this hook. A realization or a more
                specific category supplies the ideal of elements killed by
                a positive power, with its actual ambient inclusion. The
                default retains the mathematical operation without selecting
                an ideal representation or a radical algorithm.
                """
                return None

            def nilradical(self):
                r"""The ideal of elements killed by some positive power.

                Commutativity and distributivity make this set an ideal;
                the binomial proof does not use a multiplicative unit.
                With the ordinary commutative-ring ideal representation it
                is ``sqrt((0))``. Nilpotent elements need not form an ideal
                in a noncommutative semiring or ring.
                """
                result = self._nilradical_decision()
                assert result is not None, (
                    f"the nilradical of {self} is defined, but no ideal "
                    "representation of its positive-power nilpotents is supplied"
                )
                return result

            @RealizationHook
            def _krull_dimension_decision(self):
                r"""Protected selected prime-chain dimension, or None.

                Only krull_dimension calls this hook. A more specific
                category or owned realization supplies the dimension of
                this exact commutative nonunital semiring as an owned value.
                A missing computation supplies neither a finite value nor
                a dimension bound.
                """
                return None

            def krull_dimension(self):
                r"""Return the supremum of lengths of chains of proper prime ideals.

                Prime means ``xy in p`` implies ``x in p`` or ``y in p``.
                The supremum of lengths of nonempty finite chains is taken
                in ``{-infinity, 0, 1, ..., +infinity}``; an empty prime
                spectrum has dimension -infinity (Stacks, Tags 0055 and
                00KD). This definition uses neither additive inverses nor
                a unit. A selected computation must supply an owned
                representation of that fixed dimension value.
                """
                result = self._krull_dimension_decision()
                assert result is not None, (
                    f"Krull dimension is defined for {self}, but no exact "
                    "prime-chain dimension computation is represented"
                )
                return result

            @cached_method
            def prime_ideal_locus(self):
                r"""All proper prime-ideal subsets of this exact semiring.

                The full power set includes ideals without a finite
                generating presentation. An ideal is an absorbing additive
                submonoid and prime means ``xy in p`` forces ``x in p`` or
                ``y in p``. In a rng, primality also forces closure under
                additive inverses: ``(-x)^2 = x^2``. No predicate decision
                or enumeration is asserted.
                """
                from sage_extensions.logic import AtomicProposition

                return self.power_set().condition_set(
                    lambda subset: AtomicProposition("is_prime_ideal_subset", subset, self)
                )

            @cached_method
            def minimal_prime_locus(self):
                r"""The prime-ideal subsets minimal under inclusion."""
                from sage_extensions.logic import AtomicProposition

                return self.prime_ideal_locus().condition_set(
                    lambda ideal_subset: AtomicProposition(
                        "is_minimal_prime_ideal_subset", ideal_subset, self
                    )
                )

            @RealizationHook
            def _finite_minimal_primes(self):
                r"""Protected finite minimal-prime computation, or None.

                Only minimal_primes calls this hook. An owned realization
                or more specific category may supply a finite owned set of
                prime ideals of this exact object when finiteness is proved.
                No finite generation or enumeration follows from the
                default; the full ideal-subset locus remains available.
                """
                return None

            @cached_method
            def minimal_primes(self):
                r"""The minimal-prime locus, with a finite realization when supplied."""
                primes = self._finite_minimal_primes()
                return self.minimal_prime_locus() if primes is None else primes

            def irreducible_component_locus(self):
                r"""The closed subsets ``V(p)`` for the minimal prime ideals.

                These are the irreducible components of the prime-ideal
                space, including for nonreduced input. The represented
                family may be infinite; each value is the subset of primes
                containing its actual minimal-prime subset.
                """
                from sage_extensions.categories.sets.set_categories import Sets
                from sage_extensions.categories.sets.finite_ordered_sets import FiniteOrderedSets
                from sage_extensions.logic import AtomicProposition

                prime_subsets = self.prime_ideal_locus()
                minimal = self.minimal_primes()
                if minimal in FiniteOrderedSets():
                    # The selected finite computation returns owned ideal
                    # objects, but V(p) is indexed by the corresponding
                    # subsets of the ring. Convert each ideal through its
                    # membership predicate; do not pass the ideal object as
                    # though it were itself a subset of ring elements.
                    minimal_subsets = Sets().image_set(
                        lambda ideal: Sets().condition_set(
                            self, lambda element: element in ideal
                        ),
                        minimal,
                    )
                else:
                    minimal_subsets = minimal
                return Sets().image_set(
                    lambda minimal_prime: prime_subsets.condition_set(
                        lambda prime: AtomicProposition(
                            "contains_ideal_subset", prime, minimal_prime
                        )
                    ),
                    minimal_subsets,
                )


class SemiringMorphism:
    """A declared unital semiring morphism."""

    def __init__(self, parent, function) -> None:
        if not callable(function):
            raise TypeError(
                f"a semiring morphism {parent.domain()} -> {parent.codomain()} needs a map on elements, but "
                f"{function!r} is not callable"
            )
        self._function = function
        super().__init__(parent, function)

    def _composition(self, right):
        if not (
            isinstance(right, SemiringMorphism)
            and right.codomain() is self.domain()
        ):
            return NotImplemented
        target = OwnedSemirings().Mor(right.domain(), self.codomain())
        return target(lambda element: self(right(element)))


class SemiringMor(CategoricalMor):
    """The fixed Mor object of unital semiring morphisms."""

    ElementMethods = SemiringMorphism

    def _element_constructor_(self, function):
        if isinstance(function, Map):
            if (
                function.domain() is not self.domain()
                or function.codomain() is not self.codomain()
            ):
                raise ValueError(
                    f"{function} is a semiring morphism {function.domain()} -> {function.codomain()}, not a "
                    f"morphism {self.domain()} -> {self.codomain()}"
                )
            if function.parent() is self:
                return function
            raise TypeError(f"{function} belongs to another Mor; apply the functor between the categories")
        return self.element_class(self, function)

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism {self.domain()} -> {self.codomain()}: an identity exists only "
                "when the domain and codomain are the same semiring"
            )
        return self(lambda element: element)


class SemiringMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return SemiringMor


class RingMorCategoryConstruction(MorCategoryConstruction):
    r"""The owned family ``(A,B) |-> Hom_Ring(A,B)``."""

    def fixed_category_class(self):
        from sage_extensions.categories.rings.ring_foundation import RingMor

        return RingMor


class RngMorCategoryConstruction(MorCategoryConstruction):
    r"""The owned family ``(A,B) |-> Hom_Rng(A,B)``."""

    def fixed_category_class(self):
        from sage_extensions.categories.rings.ring_foundation import RngMor

        return RngMor


class OwnedSemirings(CategoryPacketMethods, OwnedCategory):
    """Semirings on the owned operation spine."""

    _MorCategory = SemiringMorCategoryConstruction

    def an_object(self):
        r"""The integers, which are in particular a semiring."""
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        return _owned_integers()

    def super_categories(self):
        return [OwnedNonUnitalSemirings(), Monoids()]

    class ParentMethods:
        @RealizationHook
        def _dual_numbers_construction(self, name):
            r"""Protected selected central dual-number construction, or None.

            Only dual_numbers calls this hook. An owned realization or a
            more specific category supplies the semiring of pairs with
            ``(a,b)*(c,d) = (a*c, a*d + b*c)`` and its selected parameter
            ``epsilon=(0,1)``. The base scalar data and this parameter are
            retained by that construction; its coefficient inclusion need
            not be central when the base is noncommutative. None supplies
            no selected construction.
            """
            return None

        def dual_numbers(self, name="epsilon"):
            r"""Return the central dual numbers of this unital semiring.

            The underlying pairs add componentwise and multiply by
            ``(a,b)*(c,d)=(a*c,a*d+b*c)``. The element ``epsilon=(0,1)``
            commutes with every pair and has square zero. This definition
            requires a unit to specify epsilon, and needs neither additive
            inverses nor commutativity of the base semiring.
            """
            result = self._dual_numbers_construction(name)
            assert result is not None, (
                f"central dual numbers are defined for {self}, but no "
                "construction retaining its coefficient data and parameter is supplied"
            )
            return result

        @RealizationHook
        def _characteristic_decision(self):
            r"""Protected exact characteristic of this semiring, or None.

            The public characteristic operation calls this hook. The
            PredicateSubrings cardinality supplier also reads it on the actual
            ambient unital ring, since a unital inclusion preserves
            characteristic. An owned parent realization or a more specific
            category supplies the nonnegative owned integer
            n for which m*1 = 0 exactly when n divides the natural number m.
            None means that no characteristic computation has been supplied;
            it does not mean characteristic zero.
            """
            return None

        def characteristic(self):
            r"""Return the characteristic determined by the natural-number map.

            This needs the semiring's zero, one and addition. The value is one
            for the zero semiring and zero when no positive multiple of one
            vanishes. For semirings, characteristic zero alone does not assert
            that the natural-number map is injective.

            Definition: Mathlib Algebra/CharP/Defs, ringChar.
            """
            from sage_extensions.categories.rings.ring_foundation import (
                _own_ring,
                _owned_integers,
            )

            if (self.one() == self.zero()) is True:
                return _owned_integers().one()
            characteristic = self._characteristic_decision()
            assert characteristic is not None, (
                f"characteristic is defined for {self}, but no computation of its natural-number kernel is available"
            )
            return characteristic

    def initial_object(self):
        """Return the natural numbers, initial among unital semirings."""
        from sage_extensions.categories.sets.set_categories import NN

        return NN

    def initial_morphism(self, codomain):
        """Return the unique unital semiring morphism from NN to codomain."""
        if codomain not in self:
            raise TypeError(
                f"the initial semiring morphism needs a semiring codomain, but {codomain} lies in "
                f"{codomain.category()}"
            )
        source = self.initial_object()
        morphisms = self.Mor(source, codomain)
        if codomain is source:
            return morphisms.identity()

        def image(natural):
            count = int(natural)
            result = codomain.zero()
            summand = codomain.one()
            while count:
                if count % 2:
                    result = result + summand
                count //= 2
                if count:
                    summand = summand + summand
            return result

        return morphisms(image)


class OwnedRngs(CategoryPacketMethods, OwnedCategory):
    """Rngs on the owned operation spine."""

    _MorCategory = RngMorCategoryConstruction

    def an_object(self):
        r"""The integers, which happen to be unital."""
        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        return _owned_integers()

    def super_categories(self):
        return [OwnedNonUnitalSemirings(), AdditiveGroups().AdditiveCommutative()]

    class ParentMethods:
        @RealizationHook
        def _ideal_generated_by(self, generators):
            r"""Protected selected two-sided rng-ideal construction, or None.

            Only the public ideal constructor calls this hook. Its input is
            a tuple of elements of this exact rng. A supplied result is the
            additive subgroup generated under left and right multiplication
            by ambient elements, with its actual ambient inclusion retained.
            A more specific category or an owned realization supplies its
            representation; None supplies no ideal-construction algorithm.
            """
            return None

        def ideal(self, *generators):
            r"""Return the two-sided rng ideal generated by these elements.

            It is the smallest additive subgroup containing the generators
            and stable under multiplication from either side. This is the
            ordinary ring/rng ideal convention; a merely absorbing additive
            submonoid in a semiring is different data. A finite input family
            does not assert that the resulting ideal has a finite module
            presentation.
            """
            if len(generators) == 1 and isinstance(generators[0], (tuple, list)):
                generators = tuple(generators[0])
            selected = tuple(self(generator) for generator in generators)
            result = self._ideal_generated_by(selected)
            assert result is not None, (
                f"the generated two-sided rng ideal of {self} is defined, but "
                "no construction for these retained generators is represented"
            )
            return result


__all__ = [
    "NonUnitalSemiringMor",
    "NonUnitalSemiringMorCategoryConstruction",
    "OwnedNonUnitalSemirings",
    "OwnedRngs",
    "OwnedSemirings",
    "RingMorCategoryConstruction",
    "SemiringMor",
    "SemiringMorCategoryConstruction",
    "SemiringMorphism",
]
