r"""Basic commutative-algebra constructions needed by affine scheme theory."""

from math import factorial
from operator import index

from sage.all import (
    PolynomialRing as _SagePolynomialRing,
)
from sage.all import (
    PowerSeriesRing as _SagePowerSeriesRing,
)
from sage.all import (
    Zp as _SageZp,
)
from sage.rings.finite_rings.finite_field_constructor import GF as _SageGF
from sage.categories.fields import Fields as SageFields
try:
    from sage.categories.ordered_fields import OrderedFields as SageOrderedFields
except ImportError:
    SageOrderedFields = None
from sage.categories.rings import Rings as SageRings
from sage.rings.rational_field import QQ as SageQQ
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.abc import Order as SageNumberFieldOrder
from sage.rings.fraction_field import FractionField_generic as SageFractionField
from sage.rings.ideal import Ideal_generic as SageIdeal
from sage.rings.infinity import Infinity
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.polynomial.polynomial_quotient_ring import PolynomialQuotientRing_generic
from sage.rings.quotient_ring import QuotientRing_generic
from sage.structure.element import CommutativeRingElement, Element, parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.objects import (
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.abstract_categories.products import (
    InverseSystem,
    PosetCategory,
    SelectedLimitConstruction,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    AlgebrasWithChosenFinitePresentation,
    _OwnedAlgebraElement,
    _OwnedAlgebraParent,
    _algebra_with_structure,
)
from sage_extensions.categories.algebras.free_algebras import SymmetricAlgebras
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.magmas import Monoids
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    LocalRingConstruction,
    LocalizationRings,
    OwnedAdicallyCompleteRings,
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedIntegralDomains,
    OwnedOrderedRings,
    OwnedOrders,
    OwnedPrincipalIdealDomains,
    OwnedRings,
    PrimeFields,
    _engine_element,
    _engine_krull_dimension,
    _engine_quotient_cover_ideal,
    _engine_ring,
    _engine_ring_value,
    _install_local_ring_construction,
    _own_ring,
    _ring_morphism_with_engine,
    _ring_morphisms_equal,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import aleph0, cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.sets.set_categories import (
    NN,
    CountablyInfiniteSets,
    FiniteSets,
    PartiallyOrderedSets,
    Sets,
    UncountableSets,
)
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import Category, CategoryWithAxiom


def _commutative_algebra_with_structure(algebra, base_ring, labels=None, *categories):
    r"""Construct the commutative owned algebra view over ``base_ring``."""
    return _algebra_with_structure(algebra, base_ring, labels, *categories)


class _PrimeSpectrumTopologyData:
    r"""Private topology datum for the Zariski space ``Spec R``."""

    def __init__(self, ring) -> None:
        self._ring = ring

    def ring(self):
        return self._ring

    def open_subsets(self, spectrum):
        return spectrum.power_set().condition_set(
            lambda subset: self.is_open_subset(spectrum, subset)
        )

    def is_open_subset(self, spectrum, subset) -> bool:
        # ``D(f)`` is the complement of the closed set ``V(f)`` (Stacks 00E0,
        # Lemma 10.17.2(11)), hence open.
        match subset:
            case _ if subset in DistinguishedOpenSubobjects(spectrum):
                return True
        power = spectrum.power_set()
        selected = power(subset)
        match selected:
            case _ if power.inclusion_order().le(selected, power.bottom()) is True:
                return True
            case _ if power.inclusion_order().le(power.top(), selected) is True:
                return True
            case _:
                assert False, (
                    f"cannot decide whether {subset} is open in {spectrum}: openness is decided here only for "
                    "the empty set, the whole spectrum, and subsets given as a Zariski-open set"
                )


class PrimeSpectra(OwnedCategory):
    r"""The prime spectra \(\operatorname{Spec}R\), ordered by inclusion.

    Unexecuted specialization specimen over a local ring. The primes
    ``(x)`` and ``(y)`` of ``QQ[x,y]_(x,y)`` are distinct and incomparable;
    both specialize to ``(x,y)`` (the localization prime correspondence,
    Atiyah--Macdonald, Proposition 3.11; Stacks, Tag 00E0)::

        sage: from dzack_research.preamble.all import *
        sage: A = QQ['x', 'y']
        sage: x = A.algebra_generator('x'); y = A.algebra_generator('y')
        sage: R = A.localize_at_prime(A.ideal(x, y))
        sage: spectrum = R.spectrum()
        sage: px = spectrum(R.ideal(R(x)))
        sage: py = spectrum(R.ideal(R(y)))
        sage: closed = spectrum(R.ideal(R(x), R(y)))
        sage: px == py
        False
        sage: px.specializes_to(py)
        False
        sage: py.specializes_to(px)
        False
        sage: px.specializes_to(closed) and py.specializes_to(closed)
        True
        sage: R.ideal(R(x)) in spectrum
        True
        sage: px in spectrum.D(R(y))
        True
        sage: px in spectrum.D(R(x))
        False
        sage: py in spectrum.V(R.ideal(R(x)))
        False
        sage: closed in spectrum.V(R.ideal(R(x)))
        True
    """

    def an_object(self):
        r"""\(\operatorname{Spec}\mathbb{Z}\)."""
        from sage.rings.integer_ring import ZZ as SageZZ

        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        return _owned_integers().spectrum()

    def super_categories(self):
        return [PartiallyOrderedSets(), TopologicalSpaces()]

    class ElementMethods(Element):
        r"""What a prime point is."""

        def __init__(self, parent, ideal) -> None:
            self._ideal = ideal
            Element.__init__(self, parent)

        def ideal(self):
            return self._ideal

        prime_ideal = ideal

        @cached_method
        def local_ring(self):
            return self.parent().ring().localize_at_prime(self.ideal())

        def stalk(self, *args, **kwargs):
            return self.local_ring(*args, **kwargs)

        @cached_method
        def residue_field(self):
            return self.local_ring().residue_field()

        @cached_method
        def residue_map(self):
            r"""Return the canonical map ``R -> kappa(p)`` attached to this point.

            This is the map whose factorization through ``R_p`` is the residue
            map of the local ring, so it is asked of the local ring rather than
            recomposed from it.
            """
            return self.local_ring().source_residue_map()

        @cached_method
        def residue_degree(self):
            r"""Return the finite degree ``[kappa(p):k]`` of a closed affine point."""
            ring = self.parent().ring()
            source = ring.quotient_source() if ring in QuotientRings() else ring
            base = source.base_ring()
            assert bool(_engine_ring(base).is_field()), (
                f"the residue degree [kappa(p) : k] at {self} is defined here relative to a coefficient field k, "
                f"but the coefficient ring {base} of {source} is not a field"
            )
            assert bool(self.ideal().is_maximal()), (
                f"the residue degree [kappa(p) : k] is finite here only at closed points, but the prime "
                f"{self.ideal()} of {ring} is not maximal"
            )
            point_engine = _engine_ideal(ring, self.ideal())
            if ring in QuotientRings():
                point_engine = _engine_quotient_cover_ideal(ring, point_engine)
            degree = int(point_engine.vector_space_dimension())
            return _owned_integers()(degree)

        @cached_method
        def closure_dimension(self):
            r"""Return ``dim closure({p}) = dim R/p`` for this prime point."""
            return self.parent().ring().quotient_ring(self.ideal()).krull_dimension()

        def generic_local_length(self, ideal):
            r"""Return ``length_{R_p}((R/I)_p)`` at an associated generic point.

            For a ``p``-primary component ``Q`` in a polynomial algebra over a
            field, degree is multiplicative with generic length:

            ``deg(R/Q) = length_{R_p}(R_p/Q_p) * deg(R/p)``.

            The maintained polynomial-ideal Hilbert computation supplies both
            degrees. This is the positive-dimensional analogue of
            :meth:`local_length`, whose vector-space colength computation is
            appropriate only when the local quotient is supported at a closed
            point.
            """
            ring = self.parent().ring()
            if ideal.ring() is not ring:
                raise ValueError(
                    f"the generic local length at {self} needs an ideal of {ring}, but {ideal} is an ideal of "
                    f"{ideal.ring()}"
                )
            source = ring.quotient_source() if ring in QuotientRings() else ring
            assert bool(_engine_ring(source.base_ring()).is_field()), (
                f"the generic local length at {self} is computed here by the degree formula for affine algebras "
                f"over a field, but the coefficient ring {source.base_ring()} of {source} is not a field"
            )

            def cover_ideal(selected):
                backend = _engine_ideal(ring, selected)
                if ring in QuotientRings():
                    backend = _engine_quotient_cover_ideal(ring, backend)
                return backend

            def projective_degree(backend):
                homogeneous = (
                    backend if backend.is_homogeneous() else backend.homogenize()
                )
                polynomial = homogeneous.hilbert_polynomial(algorithm="singular")
                if not polynomial:
                    raise ArithmeticError(
                        f"cannot compute the degree of the primary component {backend}: the Hilbert polynomial of its "
                        "homogenization is zero"
                    )
                return SageZZ(
                    polynomial.leading_coefficient()
                    * factorial(int(polynomial.degree()))
                )

            denominator = projective_degree(cover_ideal(self.ideal()))
            if denominator <= 0:
                raise ArithmeticError(
                    f"the prime {self.ideal()} has projective degree {denominator}, but the degree of a prime "
                    "component must be positive"
                )
            total = SageZZ.zero()
            for primary in ideal.primary_decomposition():
                if primary.radical() != self.ideal():
                    continue
                numerator = projective_degree(cover_ideal(primary))
                if numerator % denominator:
                    raise ArithmeticError(
                        f"the degree {numerator} of the {self.ideal()}-primary component {primary} of {ideal} is not "
                        f"divisible by the degree {denominator} of {self.ideal()}, so length_(R_p)(R_p/Q_p) is not an integer"
                    )
                total += numerator // denominator
            return _owned_integers()(total)

        def local_length(self, ideal):
            r"""Return ``length_{R_p}((R/I)_p)`` for a finite local quotient.

            If ``Q`` is the primary component supported at ``p``, then
            ``dim_k(R/Q) = length(R_p/Q_p) [kappa(p):k]``.  The residue-degree
            factor is therefore divided out explicitly, which is essential at
            a nonrational closed point.
            """
            ring = self.parent().ring()
            source = ring.quotient_source() if ring in QuotientRings() else ring
            assert bool(_engine_ring(source.base_ring()).is_field()), (
                f"the local length at {self} is computed here from finite-dimensional algebras over a field, "
                f"but the coefficient ring {source.base_ring()} of {source} is not a field"
            )
            ideal_engine = _engine_ideal(ring, ideal)
            point_engine = _engine_ideal(ring, self.ideal())
            if ring in QuotientRings():
                ideal_engine = _engine_quotient_cover_ideal(ring, ideal_engine)
                point_engine = _engine_quotient_cover_ideal(ring, point_engine)
            matching = tuple(
                component
                for component in ideal_engine.primary_decomposition()
                if component.radical() == point_engine
            )
            if not matching:
                return _owned_integers().zero()
            total_dimension = 0
            for component in matching:
                dimension = component.vector_space_dimension()
                if dimension not in SageZZ:
                    raise ValueError(
                        f"the localization of R/I at {self} does not have finite length: the component {component} "
                        f"has vector-space dimension {dimension}"
                    )
                total_dimension += int(dimension)
            residue_degree = int(self.residue_degree())
            if total_dimension % residue_degree:
                raise ArithmeticError(
                    f"the local dimension {total_dimension} at {self} is not divisible by the residue degree "
                    f"{residue_degree}, so the local length is not an integer"
                )
            return _owned_integers()(total_dimension // residue_degree)

        @cached_method
        def height(self):
            r"""The intrinsic height ``ht(p) = dim(R_p)`` of a prime ideal."""
            return self.local_ring().krull_dimension()

        @cached_method
        def embedding_dimension(self):
            r"""Return ``dim_kappa(p) pR_p/(pR_p)^2``.

            Nakayama identifies this dimension with the minimal number of
            generators of the maximal ideal of ``R_p``.  The local ideal is an
            actual represented module, so the value is obtained from its
            existing residue-module construction rather than from a separate
            Jacobian formula.
            """
            local = self.local_ring()
            return local.maximal_ideal().minimal_number_of_generators()

        @cached_method
        def is_regular(self) -> bool:
            r"""Return whether the local ring ``R_p`` is regular.

            For a Noetherian local ring, regularity is exactly
            ``edim(R_p) = dim(R_p)``.  Here the first side is the residue
            dimension of the represented maximal ideal and the second is the
            height of ``p`` in the supported catenary affine-domain regime.
            """
            return self.embedding_dimension() == self.height()

        @cached_method
        def is_locally_factorial(self):
            r"""Return local factoriality where it follows from represented regularity.

            Every regular local ring is a unique-factorization domain.  This
            gives an exact positive criterion from the local-ring data already
            represented here.  A singular local ring can still be factorial,
            so failure of regularity is not a negative criterion: the answer is
            then the proposition ``is_locally_factorial(R)``, until a
            divisor-class computation decides it.
            """
            if self.is_regular():
                return True
            return AtomicProposition("is_locally_factorial", self)

        def order_of_vanishing(self, function):
            r"""Return ``ord_p(f)`` at this height-one point.

            At a height-one prime of a normal domain ``R_p`` is a discrete
            valuation ring, and the order of vanishing is the length of
            ``R_p/(f)``, which is the valuation of ``f``.  Where the prime is
            generated by one element that element is a uniformizer, its powers
            are the powers of the maximal ideal, and the valuation is the
            multiplicity with which it divides ``f``.

            A prime that is not principal has no uniformizer, and its ordinary
            and symbolic powers can differ, so the multiplicity may not be read
            from membership in ``p^n``; that case is not computed here.
            """

            ring = self.parent().ring()
            function = ring(function)
            assert int(self.height()) == 1, (
                "an order of vanishing is stated at a prime of height one, and "
                f"{self.ideal()} has height {self.height()}"
            )
            prime = self.ideal()
            uniformizer = next(
                (
                    generator
                    for generator in prime.ideal_generators()
                    if ring.ideal(generator) == prime
                ),
                None,
            )
            assert uniformizer is not None, (
                "the order of vanishing is read from a uniformizer, so this prime must "
                f"be generated by one of its chosen generators, and {prime} is not"
            )
            assert not function.is_zero(), (
                f"the order of vanishing of a function at the prime {prime} is an integer only for a "
                "nonzero function, but the function is zero"
            )
            return function.valuation(uniformizer)

        def specializes_to(self, other) -> bool:
            r"""Whether this prime is contained in the target prime.

            The specialization order uses the actual ideals of the ring
            (Stacks, Tag 00E0), including localized ideals whose private
            computation field has a different ideal lattice.
            """
            if other.parent() is not self.parent():
                raise ValueError(
                    f"specialization is a relation between points of one spectrum, but {self} lies in "
                    f"{self.parent()} and {other} lies in {other.parent()}"
                )
            return self.ideal().is_contained_in(other.ideal())

        def _richcmp_(self, other, op):
            if element_parent(other) is not self.parent():
                return NotImplemented
            from sage.structure.richcmp import op_EQ, op_LE, op_LT, op_NE

            left_ideal = self.ideal()
            right_ideal = other.ideal()
            if op == op_EQ:
                return left_ideal == right_ideal
            if op == op_NE:
                return left_ideal != right_ideal
            if op == op_LE:
                return self.specializes_to(other)
            if op == op_LT:
                return conjunction((left_ideal != right_ideal, self.specializes_to(other)))
            return NotImplemented

        def __hash__(self):
            r"""Hash the prime ideal equality compares, so a point may key a cache."""
            return hash(self.ideal())

        def _repr_(self):
            return f"Point {self.ideal()} of {self.parent()}"

    class ParentMethods:

        def __init__(self, ring, **rest) -> None:
            self._ring = _own_ring(ring)
            assert self._ring in OwnedRings().Commutative(), (
                f"Spec(R) is defined for a commutative ring R, but {self._ring} is in {self._ring.category()}"
            )
            super().__init__(**rest)

        def ring(self):
            return self._ring

        def cardinality(self):
            r"""Return the exact number of prime points in supported finite spectra."""
            ring = self.ring()
            if ring in OwnedRings().Division().Commutative():
                return cardinal(1)
            assert ring in QuotientRings() and ring.quotient_source() is _owned_integers(), (
                f"cannot count the prime ideals of {ring}: the number of points of Spec(R) is computed here "
                "only for R a field or ZZ/(n)"
            )
            # The primes of ZZ/(n) are the (p)/(n) for the primes p dividing n.
            modulus = SageZZ(_engine_ideal(_owned_integers(), ring.defining_ideal()).gen())
            assert modulus != 0, (
                f"cannot count the prime ideals of {ring}: ZZ/(0) is ZZ, which has infinitely many"
            )
            return cardinal(len(tuple(modulus.prime_divisors())))

        def ringed_space(self):
            r"""Return the affine locally ringed space ``Spec(R)`` this spectrum underlies."""
            return self.ring().affine_spectrum()

        coordinate_ring = ring

        def __call__(self, ideal):
            r"""Construct a prime point directly from its represented ideal."""
            return self._element_constructor_(ideal)

        def _element_constructor_(self, ideal):
            r"""Construct from a prime ideal, or lift a localization-source prime.

            Primes of ``S^-1 A`` correspond to primes of ``A`` disjoint from
            ``S``; the lift is extension of the ideal (Mathlib,
            ``PrimeSpectrum.localization_comap_range``).

            Unexecuted inverse-image specimen::

                sage: from dzack_research.preamble.all import *
                sage: A = QQ['x']; x = A.algebra_generator('x')
                sage: B = A.localization(x)
                sage: p = A.spectrum()(A.ideal(x - A.one()))
                sage: lifted = B.spectrum()(p)
                sage: lifted.ideal() == p.ideal().extension_to_localization(B)
                True
                sage: spec = OwnedRings().Commutative().prime_spectrum_functor()
                sage: opposite = spec.domain()
                sage: arrow = opposite.Mor(opposite(B), opposite(A))(B.localization_map())
                sage: spec.on_morphism(arrow)(lifted) == p
                True
                sage: B.inverted_submonoid_meets(A.ideal(x))
                True
            """
            if isinstance(ideal, self.category().ElementType) and ideal.parent() is self:
                return ideal
            source = element_parent(ideal)
            ring = self.ring()
            if (
                source in PrimeSpectra()
                and ring in LocalizationRings()
                and ring.localization_source() is source.ring()
            ):
                prime = ideal.ideal()
                match ring.inverted_submonoid_meets(prime):
                    case False:
                        return self.element_class(self, prime.extension_to_localization(ring))
                    case True:
                        raise ValueError(
                            f"the prime {prime} meets the inverted submonoid of {ring}, "
                            "so it has no point above it in this localization"
                        )
                    case _:
                        assert False, (
                            f"lifting {ideal} to {self} requires deciding whether its prime "
                            "meets the inverted submonoid"
                        )
            candidate = _owned_ideal(self.ring(), ideal)
            if not bool(candidate.is_prime()):
                raise ValueError(f"{candidate} is not a prime ideal of {self.ring()}")
            return self.element_class(self, candidate)

        def __contains__(self, candidate) -> bool:
            if isinstance(candidate, self.category().ElementType):
                return candidate.parent() is self
            ideal = _owned_ideal(self.ring(), candidate)
            return bool(ideal.is_prime())

        def le(self, left, right) -> bool:
            return self._element_constructor_(left).specializes_to(
                self._element_constructor_(right)
            )

        def closed_set(self, ideal):
            return _zariski_closed_subobject(self, _owned_ideal(self.ring(), ideal))

        V = closed_set

        def distinguished_open(self, function):
            return _distinguished_open_subobject(self, function)

        D = distinguished_open

        def _repr_(self):
            return f"Spec({self.ring()})"


class _PrimeSpectrumFunctor(Functor):
    r"""``Spec: CRing^op -> Top``, acting on primes by contraction.

    A preimage of a prime along a unital ring map is prime. Continuity follows
    from ``Spec(f)^-1 D(a) = D(f(a))`` (Mathlib,
    ``PrimeSpectrum.comap_asIdeal``, ``PrimeSpectrum.continuous_comap`` and
    ``PrimeSpectrum.comap_basicOpen``). Contraction algorithms remain at the
    ring-map owner.

    Unexecuted localization-point specimen::

        sage: from dzack_research.preamble.all import *
        sage: A = QQ['x']; x = A.algebra_generator('x')
        sage: B = A.localization(x)
        sage: f = B.localization_map()
        sage: spec = OwnedRings().Commutative().prime_spectrum_functor()
        sage: opposite = spec.domain()
        sage: arrow = opposite.Mor(opposite(B), opposite(A))(f)
        sage: image = spec.on_morphism(arrow)
        sage: p = B.spectrum()(B.ideal(B(x - A.one())))
        sage: image(p) == A.spectrum()(A.ideal(x - A.one()))
        True
        sage: image(p) in A.spectrum().D(x)
        True
        sage: identity = opposite.Mor(opposite(A), opposite(A)).identity()
        sage: spec.on_morphism(identity)(image(p)) == image(p)
        True
        sage: negation_map = A.Mor(A)({'x': -x})
        sage: involution = OwnedRings().Commutative().Core().Mor(A, A)(negation_map, negation_map)
        sage: reverse = opposite.Mor(opposite(A), opposite(A))(involution)
        sage: homeomorphism = spec.on_morphism(reverse)
        sage: q = A.spectrum()(A.ideal(x - A.one()))
        sage: homeomorphism(q) == A.spectrum()(A.ideal(x + A.one()))
        True
        sage: homeomorphism.inverse()(homeomorphism(q)) == q
        True
    """

    def __init__(self, rings) -> None:
        Functor.__init__(self, rings.opposite(), TopologicalSpaces())

    def _apply_object(self, opposite_ring):
        return opposite_ring.underlying_object().spectrum()

    def _apply_morphism(self, opposite_arrow):
        from sage_extensions.categories.abstract_categories.arrow_categories import (
            _isomorphism_from_known_inverse_pair,
        )
        from sage_extensions.categories.abstract_categories.mor_categories import (
            CategoricalIsomorphism,
        )

        ring_map = opposite_arrow.underlying_arrow()
        source = self(opposite_arrow.domain())
        target = self(opposite_arrow.codomain())

        def prime_map(prime_source, prime_target, preimage):
            def image(point):
                contracted = preimage(prime_source(point).ideal())
                # PrimeSpectrum.comap_asIdeal: primality follows from the
                # unital map and the source prime.
                return prime_target.element_class(prime_target, contracted)

            return self.codomain().Mor(prime_source, prime_target)._from_continuous_set_map(
                Sets().Mor(prime_source, prime_target)(image)
            )

        if isinstance(ring_map, CategoricalIsomorphism):
            # For an isomorphism f, f^-1(J) is extension along its inverse.
            # These ideal transports are inverse, so their continuous maps
            # form the homeomorphism Spec(f), without a new inverse search.
            forward = prime_map(source, target, ring_map.inverse().forward().extension_of_ideal)
            inverse = prime_map(target, source, ring_map.forward().extension_of_ideal)
            return _isomorphism_from_known_inverse_pair(
                forward, inverse, base_category=self.codomain()
            )
        if ring_map.is_identity() is True:
            return self.codomain().Mor(source, target).identity()
        return prime_map(source, target, ring_map.contraction_of_ideal)


class IntegralPrimeSpectra(OwnedCategory):
    r"""Spectra of integral domains, with their distinguished generic point."""

    def super_categories(self):
        return [PrimeSpectra()]

    def an_object(self):
        return _owned_integers().spectrum()

    class ParentMethods:
        def generic_point(self):
            r"""The generic point corresponding to the zero prime ideal."""
            return self(self.ring().ideal(self.ring().zero()))


def _engine_ideal(ring, ideal):
    r"""Return the computation-ring ideal represented by ``ideal``.

    Protected commutative-algebra adapter under OWN-06. Representation
    dispatch is confined here; after a representation is selected, a failure
    in that route propagates rather than selecting another route by exception.
    """
    source = _own_ring(ring)
    engine = _engine_ring(source)
    from sage_extensions.categories.rings.commutative_ideals import (
        CommutativeIdeals,
        _engine_commutative_ideal,
    )

    if ideal in CommutativeIdeals(source):
        return _engine_commutative_ideal(ideal)
    if isinstance(ideal, GeneratedIdealView):
        return engine.ideal(
            tuple(
                _engine_element(ring, value)
                for value in ideal.ideal_generators()
            )
        )
    if isinstance(ideal, SageIdeal):
        if ideal.ring() is engine:
            return ideal
        return engine.ideal(
            tuple(_engine_ring_value(ring, value) for value in ideal.gens())
        )
    if isinstance(ideal, (tuple, list)):
        return engine.ideal(tuple(_engine_ring_value(ring, value) for value in ideal))
    return engine.ideal(_engine_ring_value(ring, ideal))


def _engine_coefficient_ring(engine):
    r"""Return the coefficient ring declared by a private ring realization."""
    return engine.base_ring()


def _owned_ideal(ring, ideal):
    r"""Return an owned ideal unchanged, or raise represented input into one."""
    source = _own_ring(ring)
    from sage_extensions.categories.rings.commutative_ideals import (
        CommutativeIdeals,
    )

    if ideal in CommutativeIdeals(source):
        return ideal
    backend = _engine_ideal(source, ideal)
    engine = _engine_ring(source)
    return source.ideal(
        *(_owned_engine_element(source, engine(generator)) for generator in backend.gens())
    )


def _canonical_map(domain, codomain, engine_map=None):
    source_engine = _engine_ring(domain)
    target_engine = _engine_ring(codomain)
    if engine_map is None and target_engine is not codomain:
        engine_map = target_engine.coerce_map_from(source_engine)

    def image(element):
        source = _engine_element(domain, domain(element))
        value = engine_map(source) if engine_map is not None else source
        return _owned_engine_element(codomain, target_engine(value))


    return _ring_morphism_with_engine(domain, codomain, image, engine_map)




class ZariskiClosedSubobjects(OwnedParameterizedCategory):
    r"""Closed subsets of one prime spectrum, retaining their defining ideal."""

    def an_object(self):
        spectrum = self.base()
        ring = spectrum.ring()
        return spectrum.closed_set(ring.ideal(ring.zero()))

    def parameter_category(self):
        return PrimeSpectra()

    def super_categories(self):
        return [Sets().Subobjects(self.base())]

    class ParentMethods:
        def __init__(self, defining_ideal, **rest):
            self._defining_ideal = defining_ideal
            super().__init__(**rest)

        def defining_ideal(self):
            return self._defining_ideal

        def _repr_(self):
            return f"V({self.defining_ideal()}) in {self.codomain()}"


class DistinguishedOpenSubobjects(OwnedParameterizedCategory):
    r"""Distinguished open subsets of one prime spectrum, retaining ``f``."""

    def an_object(self):
        spectrum = self.base()
        return spectrum.distinguished_open(spectrum.ring().one())

    def parameter_category(self):
        return PrimeSpectra()

    def super_categories(self):
        return [Sets().Subobjects(self.base())]

    class ParentMethods:
        def is_contained_in(self, other):
            r"""``D(f) <= D(g)`` exactly when ``g`` is a unit in ``A_f``.

            Reference: Mathlib
            ``PrimeSpectrum.basicOpen_le_basicOpen_iff_algebraMap_isUnit``.

            Unexecuted basis-containment specimen::

                sage: from dzack_research.preamble.all import *
                sage: A = QQ['x']; x = A.algebra_generator('x')
                sage: spectrum = A.spectrum()
                sage: spectrum.D(x).is_contained_in(spectrum.D(x*x))
                True
                sage: spectrum.D(x*x).is_contained_in(spectrum.D(x))
                True
                sage: spectrum.D(x) == spectrum.D(x*x)
                True
                sage: spectrum.D(A.one()).is_contained_in(spectrum.D(x))
                False
            """
            if other in DistinguishedOpenSubobjects(self.codomain()):
                ring = self.coordinate_ring()
                return ring.localization_map()(other.function()).is_unit()
            return super().is_contained_in(other)

        def __init__(self, function, **rest):
            self._function = function
            super().__init__(**rest)

        def function(self):
            return self._function

        def coordinate_ring(self):
            return self.codomain().ring().localization(self.function())

        def _repr_(self):
            return f"D({self.function()}) in {self.codomain()}"


def _zariski_closed_subobject(spectrum, ideal):
    domain = spectrum.condition_set(
        lambda point: ideal.is_contained_in(point.ideal())
    )
    inclusion = domain.inclusion()
    return Sets().Subobjects(spectrum).object(
        inclusion,
        categories=(ZariskiClosedSubobjects(spectrum),),
        construction_data={"defining_ideal": ideal},
    )


def _distinguished_open_subobject(spectrum, function):
    function = spectrum.ring()(function)
    domain = spectrum.condition_set(
        lambda point: negation(point.ideal().contains_ambient_element(function))
    )
    inclusion = domain.inclusion()
    return Sets().Subobjects(spectrum).object(
        inclusion,
        categories=(DistinguishedOpenSubobjects(spectrum),),
        construction_data={"function": function},
    )



def _engine_quotient_representative(quotient_engine, backend_value):
    r"""A source-engine representative of a class held by a quotient's selected realization.

    Private adapter of :class:`QuotientRings` (``OWN-06``), called only by its
    element constructor after the realization is selected.  Sage quotient
    rings and ``ZZ/nZZ`` lift a class by ``lift()``.  The realization of
    ``F_p[t]/(m)`` is a Sage finite field of degree ``deg m`` over its prime
    field, whose elements have no ``lift()``; ``polynomial()`` returns the
    reduced representative in ``F_p[t]`` (``element_givaro.pyx``,
    ``element_pari_ffelt.pyx``, ``element_ntl_gf2e.pyx``).
    """
    from sage.rings.finite_rings.finite_field_base import FiniteField as SageFiniteFieldClass

    match quotient_engine:
        case SageFiniteFieldClass() if quotient_engine.degree() > 1:
            return backend_value.polynomial()
        case _:
            return backend_value.lift()


class QuotientRings(OwnedCategory):
    r"""Commutative quotient rings equipped with their quotient map."""

    def super_categories(self):
        from sage_extensions.categories.group.magmas import AdditiveGroups

        return [AdditiveGroups().AdditiveCommutative()]

    def an_object(self):
        integers = _owned_integers()
        return integers.quotient_ring(integers.ideal(integers(2)))

    class ElementMethods(Element):
        r"""What a class in \(R/I\) is."""

        def __init__(self, parent, representative) -> None:
            self._representative = parent.quotient_source()(representative)
            CommutativeRingElement.__init__(self, parent)

        def lift(self):
            return self._representative

        representative = lift

        def _add_(self, other):
            return self.parent()(self.lift() + other.lift())

        def _mul_(self, other):
            return self.parent()(self.lift() * other.lift())

        def _neg_(self):
            return self.parent()(-self.lift())

        def _unit_decision(self):
            parent = self.parent()
            source = parent.quotient_source()
            unit_ideal = source.ideal(
                *parent.defining_ideal().ideal_generators(),
                self.lift(),
            )
            return unit_ideal.contains_ambient_element(source.one())

        def _unit_inverse_decision(self):
            return self.parent()._quotient_unit_inverse(self)

        __truediv__ = Monoids.ElementMethods.divide_by_unit

        def _richcmp_(self, other, op):
            if other.parent() is not self.parent():
                return NotImplemented
            if op not in (op_EQ, op_NE):
                return NotImplemented
            equal = self.parent().defining_ideal().contains_ambient_element(
                self.lift() - other.lift()
            )
            return equal if op == op_EQ else negation(equal)

        def _repr_(self):
            return f"{self.lift()} mod {self.parent().defining_ideal()}"

    class ParentMethods:
        _derived_construction_parameters = frozenset({"base_ring"})

        def __init__(
            self,
            source,
            defining_ideal,
            _engine_ring=None,
            **rest,
        ) -> None:
            def quotient_map():
                return source.Mor(self, category=OwnedRings())(
                    lambda element: self(element),
                )

            self._quotient_source = source
            self._quotient_defining_ideal = defining_ideal
            self._quotient_map_factory = quotient_map
            self._preamble_engine_ring = _engine_ring
            super().__init__(
                base_ring=source,
                _engine_product=lambda left, right: QuotientRings.ElementMethods._mul_(left, right),
                _engine_scalar_action=lambda scalar, element: QuotientRings.ElementMethods._mul_(self(scalar), self(element)),
                _engine_unit=lambda algebra: QuotientRings.ParentMethods.one(algebra),
                **rest,
            )

        def _element_constructor_(self, value):
            from sage.structure.element import parent as element_parent
            from sage_extensions.categories.modules.pure.modules import Modules

            source = element_parent(value)
            if source is not self and source in Modules(self.base_ring()) and source.unformed_module() is self:
                return source._element_of_unformed_module(value)
            if source is self:
                return value
            quotient_source = self.quotient_source()
            if source is quotient_source or quotient_source in LocalizationRings():
                # A class of an actual source element needs no computation
                # model, including for localizations with zero divisors.
                # The quotient factory supplies no native quotient engine
                # for a localized source; its exact comparison is separate.
                return self.element_class(self, quotient_source(value))
            source_engine = _engine_ring(quotient_source)
            value_parent = source
            quotient_engine = self._preamble_engine_ring
            if quotient_engine is not None and value_parent is quotient_engine:
                backend_value = quotient_engine(value)
                value = _owned_engine_element(
                    quotient_source,
                    source_engine(_engine_quotient_representative(quotient_engine, backend_value)),
                )
            elif value_parent in OwnedRings():
                value_engine = _engine_ring(value_parent)
                if value_parent is quotient_source or value_engine is source_engine:
                    value = _owned_engine_element(quotient_source,
                        source_engine(_engine_element(value_parent, value))
                    )
                elif quotient_engine is not None and value_engine is quotient_engine:
                    backend_value = quotient_engine(_engine_element(value_parent, value))
                    value = _owned_engine_element(
                        quotient_source,
                        source_engine(_engine_quotient_representative(quotient_engine, backend_value)),
                    )
            elif value_parent is source_engine:
                value = _owned_engine_element(quotient_source, source_engine(value))
            return self.element_class(self, value)

        def __call__(self, value):
            return self._element_constructor_(value)

        def _from_engine_element(self, value):
            r"""Cross the selected realization, or retain an owned source representative."""
            engine = self._preamble_engine_ring
            if engine is not None:
                return self._element_constructor_(engine(value))
            comparison = self._finite_localized_quotient_isomorphism()
            if comparison is None:
                return self(value)
            return comparison.forward()(_owned_engine_element(comparison.domain(), value))

        def _selected_engine_ring(self):
            r"""Return the selected quotient realization, or the owned parent itself.

            The latter is the OwnedRings self-realization contract. Exact
            source representatives and formal module presentations remain
            available without claiming a finite contraction comparison is
            an isomorphism when its finiteness hypothesis is unestablished.
            """
            engine = self._preamble_engine_ring
            if engine is not None:
                return engine
            comparison = self._finite_localized_quotient_isomorphism()
            if comparison is None:
                return self
            return _engine_ring(comparison.domain())

        def _engine_element(self, value):
            engine = self._preamble_engine_ring
            if engine is None:
                comparison = self._finite_localized_quotient_isomorphism()
                if comparison is None:
                    return self(value)
                return _engine_element(comparison.domain(), comparison.inverse()(self(value)))
            element = self(value)
            source_value = _engine_element(self.quotient_source(), element.lift())
            quotient_map = engine.coerce_map_from(_engine_ring(self.quotient_source()))
            if quotient_map is not None:
                return quotient_map(source_value)
            return engine(source_value)

        def _finite_localized_quotient_isomorphism(self):
            r"""Select the localization owner's retained finite comparison.

            This owner-local dispatcher is used only by this quotient's
            computation crossings and invariant hooks. A native quotient
            keeps its own selected engine; a quotient of a localization may
            compute through an exact finite isomorphism without replacing its
            source, defining ideal, projection, or category placement.
            """
            source = self.quotient_source()
            if source in LocalizationRings():
                return source._finite_quotient_contraction_isomorphism(self)
            return None

        def _quotient_unit_inverse(self, element):
            r"""Private parent computation for the monoid unit-inverse hook.

            Owner: QuotientRings.ParentMethods. The permitted caller is this
            category's element realization implementing _unit_inverse_decision.
            The input and result are owned elements of this exact quotient;
            only this parent inspects its selected quotient engine. None means
            it has no inverse computation, and a proved nonunit raises
            ZeroDivisionError.

            A unit of the actual source descends with its inverse. For a
            proper ideal in a local source, the converse holds: every proper
            ideal lies in the maximal ideal, so a source nonunit remains a
            nonunit. Neither statement requires a finite quotient comparison.
            """
            zero_quotient = self._is_zero_ring()
            if zero_quotient is True:
                return self.zero()
            if self._preamble_engine_ring is None:
                comparison = self._finite_localized_quotient_isomorphism()
                if comparison is not None:
                    return comparison.forward()(comparison.inverse()(element).inverse_of_unit())
                source = self.quotient_source()
                lift = element.lift()
                match (
                    lift.is_unit(),
                    zero_quotient,
                    source in OwnedRings().Commutative().Local(),
                ):
                    case (True, _, _):
                        return self(lift.inverse_of_unit())
                    case (False, False, True):
                        raise ZeroDivisionError(f"{element} is not a unit in {self}")
                    case _:
                        return None
            represented = self._engine_element(element)
            if not represented.is_unit():
                raise ZeroDivisionError(f"{element} is not a unit in {self}")
            return self._from_engine_element(represented**-1)

        def zero(self):
            return self(self.quotient_source().zero())

        def one(self):
            return self(self.quotient_source().one())

        def an_element(self):
            return self.one()

        def _is_zero_ring(self):
            r"""Whether this is ``R/R``, the zero ring."""
            return self.defining_ideal().contains_ambient_element(
                self.quotient_source().one()
            )

        def _finiteness_decision(self):
            if self._is_zero_ring() is True:
                return True
            if self._preamble_engine_ring is not None:
                from sage_extensions.categories.rings.ring_foundation import (
                    _engine_finiteness_decision,
                )

                decision = _engine_finiteness_decision(self._preamble_engine_ring)
                return (
                    AtomicProposition("is_finite", self)
                    if decision is None else decision
                )
            source = self.quotient_source()
            if source in LocalizationRings():
                # The canonical contracted quotient embeds into this
                # localization; if finite, it already inverts S.
                comparison = source._quotient_contraction_map_decision(self)
                if comparison is None:
                    return AtomicProposition("is_finite", self)
                return comparison.domain().is_finite()
            source_engine = source._selected_engine_ring()
            if isinstance(source_engine, SageNumberFieldOrder):
                return not _engine_ideal(
                    self.quotient_source(), self.defining_ideal()
                ).is_zero()
            return AtomicProposition("is_finite", self)

        def _cardinality_decision(self):
            # Sage's generic quotient of a field by its unit ideal has no
            # cardinality method; R/R has exactly one element.
            if self._is_zero_ring() is True:
                return cardinal(1)
            if self._preamble_engine_ring is not None:
                engine = self._preamble_engine_ring
                if not isinstance(engine, QuotientRing_generic):
                    return cardinal(engine.cardinality())
                # Sage's generic quotient has no total cardinality method.
                # Retain the source/ideal computations below rather than
                # treating an absent method as a mathematical answer.
            # For a k-algebra A over a field k and a proper ideal I, the
            # structure map k -> A/I is a ring map from a field to a nonzero
            # ring, hence injective, and A -> A/I is onto, so
            # |k| <= |A/I| <= |A|.  When |k| = |A| the cardinality is decided.
            base = self.quotient_source().base_ring()
            if base is not self.quotient_source() and base in OwnedFields():
                lower = base._cardinality_decision()
                upper = self.quotient_source()._cardinality_decision()
                if lower is not None and upper is not None and (cardinal(lower) == cardinal(upper)) is True:
                    return cardinal(lower)
            if self.quotient_source() in LocalizationRings():
                comparison = self._finite_localized_quotient_isomorphism()
                return None if comparison is None else comparison.domain()._cardinality_decision()
            source = self.quotient_source()
            source_engine = source._selected_engine_ring()
            if source_engine is None:
                return None
            if source_engine is SageZZ:
                # Every nonzero ideal of ZZ is (n), and ZZ/(n) has |n| elements.
                generator = _engine_ideal(source, self.defining_ideal()).gen()
                if generator != 0:
                    return cardinal(abs(generator))
            if isinstance(source_engine, SageNumberFieldOrder):
                defining = _engine_ideal(
                    self.quotient_source(), self.defining_ideal()
                )
                if not defining.is_zero():
                    return cardinal(SageZZ(defining.norm()))
            if (
                source not in LocalizationRings()
                and source in OwnedRings().Commutative().NoZeroDivisors().PrincipalIdeals()
                and source in OwnedRings().Commutative().Local()
            ):
                valuations = []
                for generator in self.defining_ideal().ideal_generators():
                    backend = _engine_ring_value(source, generator)
                    if backend == source_engine.zero():
                        continue
                    valuations.append(int(backend.valuation()))
                if valuations:
                    residue_size = source.residue_field()._cardinality_decision()
                    if residue_size is None or not cardinal(residue_size).expression().is_normal_form():
                        return None
                    return cardinal(residue_size) ** min(valuations)
            return None

        def _field_decision(self):
            r"""Return whether R/I is a field, equivalently whether I is maximal."""
            if self._is_zero_ring() is True:
                return False
            return self.defining_ideal().is_maximal()

        def _integral_domain_decision(self):
            if self._is_zero_ring() is True:
                return False
            return self.defining_ideal().is_prime()

        def _krull_dimension_decision(self):
            assert self._is_zero_ring() is not True, (
                "the empty prime spectrum has Krull dimension -infinity; "
                "an owned extended-dimension representation is not yet supplied"
            )
            if self._preamble_engine_ring is not None:
                return _engine_krull_dimension(self)
            source = self.quotient_source()
            if source in LocalizationRings():
                comparison = self._finite_localized_quotient_isomorphism()
                return None if comparison is None else comparison.domain().krull_dimension()
            source_engine = _engine_ring(source)
            if source_engine is source:
                return None
            backend = _engine_ideal(source, self.defining_ideal())
            if isinstance(source_engine, SageNumberFieldOrder) and not backend.is_zero():
                return _owned_engine_element(SageZZ, SageZZ.zero())
            return _owned_engine_element(SageZZ, SageZZ(backend.dimension()))

        def _repr_(self):
            return f"{self.quotient_source()} / {self.defining_ideal()}"

        def quotient_source(self):
            return self._quotient_source

        def defining_ideal(self):
            return self._quotient_defining_ideal

        def _has_selected_exact_coefficient_presentation(self) -> bool:
            r"""Whether the actual quotient cover is an available exact coefficient presentation.

            The inherited module-algorithm contract reads the fixed source
            and defining ideal of this quotient.  A polynomial cover over an
            actual field, or the integer cover, supplies these data directly;
            a larger computation field of a localization does not.
            """
            source = self.quotient_source()
            if source is _owned_integers():
                return True
            base = source.base_ring()
            return (
                base in OwnedRings().Division().Commutative()
                and source in SymmetricAlgebras(base)
                and source.algebra_generating_set() in FiniteSets()
            )

        def _exact_coefficient_presentation_ring(self):
            if self._has_selected_exact_coefficient_presentation():
                return self.quotient_source()
            return super()._exact_coefficient_presentation_ring()

        def _exact_coefficient_presentation_relations(self):
            if self._has_selected_exact_coefficient_presentation():
                return self.defining_ideal().ideal_generators()
            return super()._exact_coefficient_presentation_relations()

        def _lift_coefficient_to_presentation(self, value):
            if self._has_selected_exact_coefficient_presentation():
                return self(value).lift()
            return super()._lift_coefficient_to_presentation(value)

        def _descend_coefficient_from_presentation(self, value):
            if self._has_selected_exact_coefficient_presentation():
                return self(value)
            return super()._descend_coefficient_from_presentation(value)

        @cached_method
        def quotient_map(self):
            morphism = self._quotient_map_factory()
            if morphism.domain() is not self.quotient_source():
                raise ValueError(
                    f"the quotient map of {self} must start at {self.quotient_source()}, but it starts at "
                    f"{morphism.domain()}"
                )
            return morphism

        def _module_basis_along(self, ring_map):
            r"""The basis ``1, a, ..., a^{d-1}`` of ``k[x]/(p)`` over ``k``, along the coefficient map.

            Implements the protected contract declared at
            ``OwnedRings.ParentMethods._module_basis_along``.  The coefficient
            map is the composite ``k -> k[x] -> k[x]/(p)`` of the structure
            morphism of the quotient source with the quotient map; a
            ``ring_map`` equal to it gets the power basis of the class ``a`` of
            ``x``, by division with remainder by ``p``.  Sage realizes
            ``k[x]/(p)`` as a ``PolynomialQuotientRing_generic`` only for ``p``
            with unit leading coefficient, and its elements are remainders of
            degree below ``d``; this adapter reads them (``OWN-06``).  Every
            other realization or ring map takes the general contract.
            """
            from sage_extensions.categories.modules.native_modules import (
                _power_module_basis,
            )

            engine = self._preamble_engine_ring
            match engine:
                case PolynomialQuotientRing_generic() if engine.modulus().degree() > 0:
                    pass
                case _:
                    return super()._module_basis_along(ring_map)
            coefficient_map = self.quotient_map() * self.quotient_source().algebra_structure_morphism()
            match _ring_morphisms_equal(ring_map, coefficient_map):
                case True:
                    return _power_module_basis(
                        ring_map.domain(),
                        int(engine.modulus().degree()),
                        lambda exponent: self._from_engine_element(engine.gen()) ** exponent,
                        lambda element: self._engine_element(element).list(),
                    )
                case _:
                    return super()._module_basis_along(ring_map)

        def localization_comparison(self, localization_ring):
            r"""Return ``S^{-1}(R/I) ~= S^{-1}R/S^{-1}I`` with both maps."""
            return _quotient_localization_comparison(self, localization_ring)

        def completion_comparison(self, source_ideal, *, precision=20):
            r"""Return ``(R/J)^ ~= R^/J R^`` for the selected adic topology.

            Here ``self = R/J`` and ``source_ideal`` is the ideal ``I`` of
            ``R`` whose image defines the topology on ``R/J``.  The supported
            theorem is the finite-module completion theorem over a Noetherian
            source; the comparison is built from the two canonical completion
            maps and the quotient maps rather than from the selected finite
            computation precision.
            """
            return _quotient_completion_comparison(
                self,
                source_ideal,
                precision=precision,
            )

        def _characteristic_decision(self):
            source = self.quotient_source()
            if source is _owned_integers():
                # The selected integer ideal is canonicalized by Sage from
                # its entire generating family, not its first written entry.
                generator = abs(_engine_ideal(source, self.defining_ideal()).gen())
                return _owned_engine_element(SageZZ, generator)
            if (
                source in OwnedRings().Division().Commutative()
                and self._is_zero_ring() is False
            ):
                return source.characteristic()
            if source in LocalizationRings():
                # This canonical map is injective and unital even when its
                # domain is infinite, so it preserves the characteristic.
                return source.quotient_contraction_map(self).domain().characteristic()
            engine = self._preamble_engine_ring
            if engine is not None:
                return _owned_engine_element(SageZZ, SageZZ(engine.characteristic()))
            # A localization's fraction-field model need not have the
            # characteristic of its quotient by the selected ideal.
            return None

        @cached_method
        def _affine_normalization_data(self):
            r"""Retain the finite affine normalization after reduction.

            Its callers are the declared ``_normalization_data`` supplier
            and the selected ``_normality_decision`` computation.
            Singular normalizes the radical defining ideal in the same
            polynomial cover. The owned ring and module maps remain over
            this original quotient, including when it is nonreduced.
            """
            return _affine_quotient_normalization_data(self)

        def _normalization_data(self):
            r"""Supply the common normalization contract in the finite affine regime.

            The actual coefficient field and finite symmetric presentation
            establish finiteness of the normalization and its component
            family here. An arbitrary quotient or localization supplies no
            such computation merely by belonging to this category.
            """
            source = self.quotient_source()
            base = source.base_ring()
            if (
                base in OwnedRings().Division().Commutative()
                and source in SymmetricAlgebras(base)
                and source.algebra_generating_set() in FiniteSets()
            ):
                return self._affine_normalization_data()
            return None

        def _reducedness_decision(self):
            if self._is_zero_ring() is True:
                return True
            source = self.quotient_source()
            if source in LocalizationRings() or _engine_ring(source) is source:
                defining = self.defining_ideal()
                radical = defining._radical_decision()
                if radical is None:
                    return AtomicProposition("is_reduced", self)
                return radical == defining
            defining = _engine_ideal(self.quotient_source(), self.defining_ideal())
            return defining.radical() == defining

        @cached_method
        def _presentation_minimal_primes(self):
            r"""The exact finite minimal primes upstairs, or no selected computation.

            The defining ideal owns this computation, including its PID,
            quotient-cover and localization transports. Its result consists
            of ideals of the actual source of this quotient.
            """
            from sage_extensions.categories.rings.ring_foundation import OwnedNoetherianRings
            source = self.quotient_source()
            if source not in OwnedNoetherianRings():
                return None
            return self.defining_ideal().finite_minimal_primes()

        @cached_method
        def _finite_minimal_primes(self):
            r"""Transport the selected finite minimal primes into this quotient."""
            primes = self._presentation_minimal_primes()
            if primes is None:
                return None
            return finite_ordered_set(
                tuple(
                    self.ideal(
                        *(self(generator) for generator in prime.ideal_generators())
                    )
                    for prime in primes
                )
            )

        @cached_method
        def _finite_irreducible_components(self):
            r"""The component quotients of this ring by its own minimal primes.

            The primes computed in the presentation ring must first be
            transported to ideals of this quotient. Quotienting the cover
            directly loses the represented map out of this ring, even when
            the resulting abstract component rings are isomorphic.
            """
            primes = self._finite_minimal_primes()
            if primes is None:
                return None
            return finite_ordered_set(
                tuple(
                    self.quotient_ring(prime)
                    for prime in primes
                )
            )

        @cached_method
        def _total_quotient_map_decision(self):
            r"""The product-of-fields realization for a reduced Noetherian quotient.

            Finitely many minimal primes are required for this product formula
            (Stacks, Section 10.25). The common owner handles domains and the
            zero ring separately and retains this map together with its target.
            """
            if self.is_reduced() is not True:
                return None
            source = self.quotient_source()
            if source in LocalizationRings():
                # For I contracted from J, every denominator acts regularly
                # on B=R/I by S-saturation. It is already invertible in Q(B),
                # so localization changes neither that total quotient ring
                # nor its surviving component fields. Reuse their owner.
                contracted_quotient = source.quotient_contraction_map(self).domain()
                total_map = contracted_quotient.total_quotient_map()
                source_map = total_map * contracted_quotient.quotient_map()
                localized_map = source._induced_morphism_from_unit_images(source_map)
                return OwnedRings().Mor(self, localized_map.codomain())(
                    lambda element: localized_map(self(element).lift())
                )
            if self._presentation_minimal_primes() is None:
                return None
            components = tuple(self.irreducible_components())
            fields = tuple(component.fraction_field() for component in components)
            field_maps = tuple(component.fraction_field_map() for component in components)
            # Compose genuine ring arrows A -> A/p -> Frac(A/p) at the
            # categorical Mor owner. The component maps are independent of
            # any chosen lift of a representative in the presentation ring.
            component_maps = tuple(
                field_map * component.quotient_map()
                for component, field_map in zip(components, field_maps, strict=True)
            )
            target = OwnedRings().product(fields)
            target_engine = _engine_ring(target)

            def image(element):
                values = tuple(
                    component_map(self(element)) for component_map in component_maps
                )
                if len(values) == 1:
                    return values[0]
                backend = target_engine(
                    tuple(
                        _engine_element(field, value)
                        for field, value in zip(fields, values, strict=True)
                    )
                )
                return _owned_engine_element(target, backend)

            return OwnedRings().Mor(self, target)(image)

        def _normality_decision(self):
            r"""Selected finite affine normality computation at the common owner."""
            reduced = self.is_reduced()
            if reduced is False:
                return False
            source = self.quotient_source()
            if source in LocalizationRings():
                comparison = self._finite_localized_quotient_isomorphism()
                if comparison is not None:
                    return comparison.domain().is_normal()
                return AtomicProposition("is_normal", self)
            base = source.base_ring()
            if (
                reduced is True
                and base in OwnedRings().Division().Commutative()
                and source in SymmetricAlgebras(base)
                and source.algebra_generating_set() in FiniteSets()
            ):
                return self._affine_normalization_data().is_normal
            return AtomicProposition("is_normal", self)

    def super_categories(self):
        return [OwnedRings().Commutative()]


class _AffineNormalizationData(SageObject):
    r"""The retained finite affine normalization and its original scalar action.

    The native conductor and delta are private computation diagnostics.
    The corresponding mathematical values come from the retained actual
    normalization cokernel and its chosen coefficient restriction.

    A localization producer also retains the actual ring map ``B -> S^-1 B``
    and the module isomorphisms
    ``S^-1(A.regular_module()) -> (S^-1 A).regular_module()`` and
    ``S^-1 M -> coker(eta_S)``. These optional data are absent on a packet
    produced directly by the affine normalization computation.
    """

    def __init__(
        self,
        normalization,
        normalization_map,
        conductor,
        delta,
        is_normal,
        components,
        *,
        normalization_module_realization,
        normalization_unit_map,
        coefficient_map,
        component_module_numerators,
        component_projections,
        reduction_map,
        reduced_normalization_map,
        normalization_localization_map=None,
        normalization_regular_comparison=None,
        normalization_cokernel_comparison=None,
    ) -> None:
        self.normalization = normalization
        self.normalization_map = normalization_map
        self._native_conductor = conductor
        self._native_delta = None if delta is None else int(delta)
        self.is_normal = is_normal
        self.components = components
        self.normalization_module_realization = normalization_module_realization
        self.normalization_module = normalization_module_realization.domain()
        self.normalization_unit_map = normalization_unit_map
        self.normalization_cokernel = normalization_unit_map.cokernel()
        self.coefficient_map = coefficient_map
        self.component_module_numerators = component_module_numerators
        self.component_projections = component_projections
        self.reduction_map = reduction_map
        self.reduced_normalization_map = reduced_normalization_map
        self.normalization_localization_map = normalization_localization_map
        self.normalization_regular_comparison = normalization_regular_comparison
        self.normalization_cokernel_comparison = normalization_cokernel_comparison
        if normalization_localization_map is not None:
            assert normalization_localization_map.codomain() is normalization
        if normalization_regular_comparison is not None:
            assert normalization_regular_comparison.codomain() is normalization_unit_map.domain()
        if normalization_cokernel_comparison is not None:
            assert normalization_cokernel_comparison.codomain() is self.normalization_cokernel

    @property
    def conductor(self):
        return self.normalization_map.domain().conductor_ideal()

    @property
    def delta(self):
        return self.normalization_map.domain().delta_invariant()


def _identity_affine_normalization_data(algebra, coefficient_map, components):
    r"""Retain identity normalization when the affine owner proves normality.

    The callers are the finite symmetric-algebra producer over a field and
    the zero-quotient branch of ``_affine_quotient_normalization_data``.
    They supply respectively the single domain component and the empty
    component family; normality alone never supplies such an enumeration.
    """
    from sage_extensions.categories.modules.pure.modules import Modules

    identity = OwnedRings().Mor(algebra, algebra).identity()
    regular = algebra.regular_module()
    target = regular.restrict_scalars(identity)
    realization = Modules(algebra).Mor(regular, target)(
        {
            label: target.wrap(regular.module_generator(label))
            for label in regular.module_generating_set()
        }
    )
    unit_map = Modules(algebra).Mor(regular, regular).identity()
    indices = components.index_set()
    numerator_labels = finite_ordered_set((0,))
    numerators = finite_indexed_family(numerator_labels, lambda label: algebra.one())
    return _AffineNormalizationData(
        algebra,
        identity,
        None,
        None,
        True,
        components,
        normalization_module_realization=realization,
        normalization_unit_map=unit_map,
        coefficient_map=coefficient_map,
        component_module_numerators=finite_indexed_family(indices, lambda index: numerators),
        component_projections=finite_indexed_family(indices, lambda index: components.value(index)[2]),
        reduction_map=identity,
        reduced_normalization_map=identity,
    )


def _localized_affine_normalization_data(localization, source_data):
    r"""Localize a retained finite normalization along finitely many elements.

    The only caller is ``LocalizationRings._normalization_data``. It supplies
    the actual localization ``L=S^-1 A`` and a normalization packet over A
    with a chosen finite module presentation and an ordered finite component
    family.
    An undecided component-survival test returns ``None``; it is never read
    as permission to discard that component.

    Integral closure commutes with localization (Stacks, Tag 0307). For the
    retained finite product ``B=prod B_i``, its localization is represented
    by the product of the surviving ``C_i=(nu_i(S))^-1 B_i``. The actual
    map ``B -> prod C_i`` is retained. This does not ask a Cartesian-product
    computation engine to localize at zero divisors, nor identify this
    target with a separately constructed localization parent.

    Exact module localization carries N and the one diagonal unit map to
    L. The regular-source and cokernel comparisons are actual module
    isomorphisms. In particular the cokernel is ``S^-1(B/image(A))``. A
    proved normal L retains this normalized target; choosing L itself as
    target would additionally require a computed inverse of the unit map.
    """
    from sage_extensions.categories.abstract_categories.arrow_categories import (
        _isomorphism_from_known_inverse_pair,
    )
    from sage_extensions.categories.modules.pure.modules import Modules
    from sage_extensions.logic import conjunction

    source = localization.localization_source()
    assert source_data.normalization_map.domain() is source
    assert source_data.normalization_unit_map.domain() is source.regular_module()
    localization_map = localization.localization_map()
    inverted = tuple(localization.inverted_elements())
    surviving = []
    for index in source_data.components.index_set():
        prime, _, _ = source_data.components.value(index)
        match localization.inverted_submonoid_meets(prime):
            case True:
                pass
            case False:
                surviving.append(index)
            case _:
                return None
    indices = finite_ordered_set(tuple(surviving))

    localized_components = {}
    component_localizations = {}
    component_maps = {}
    for index in indices:
        _, component, component_map = source_data.components.value(index)
        localized_component = component.localization(
            *(component_map(element) for element in inverted)
        )
        component_localization = (
            OwnedRings().Mor(component, component).identity()
            if localized_component is component
            else localized_component.localization_map()
        )
        localized_components[index] = localized_component
        component_localizations[index] = component_localization
        component_maps[index] = localization.induced_morphism(
            component_localization * component_map
        )

    # If every minimal component is killed, a power of an element of S is
    # zero in A. Thus L itself is the zero ring and represents the empty
    # product; the product of rings is represented for a nonempty family.
    component_values = tuple(localized_components[index] for index in indices)
    normalization = OwnedRings().product(component_values) if component_values else localization
    normalization_engine = _engine_ring(normalization)

    def in_product(values):
        if not component_values:
            return localization.zero()
        if len(component_values) == 1:
            return component_values[0](values[0])
        return _owned_engine_element(
            normalization,
            normalization_engine(tuple(
                _engine_element(component, value)
                for component, value in zip(component_values, values, strict=True)
            )),
        )

    normalization_localization_map = OwnedRings().Mor(
        source_data.normalization, normalization
    )(
        lambda element: in_product(tuple(
            component_localizations[index](
                source_data.component_projections.value(index)(element)
            )
            for index in indices
        ))
    )

    source_reduction_map = source_data.reduction_map
    reduced_source = source_reduction_map.codomain()
    if source_reduction_map.is_identity() is True:
        reduced_localization = localization
        reduction_map = OwnedRings().Mor(localization, localization).identity()
    else:
        reduced_localization = reduced_source.localization(
            *(source_reduction_map(element) for element in inverted)
        )
        reduced_localization_map = (
            OwnedRings().Mor(reduced_source, reduced_source).identity()
            if reduced_localization is reduced_source
            else reduced_localization.localization_map()
        )
        reduction_map = localization.induced_morphism(
            reduced_localization_map * source_reduction_map
        )

    reduced_component_maps = {}
    for index in indices:
        source_leg = (
            component_localizations[index]
            * source_data.component_projections.value(index)
            * source_data.reduced_normalization_map
        )
        reduced_component_maps[index] = (
            source_leg
            if reduced_localization is reduced_source
            else reduced_localization.induced_morphism(source_leg)
        )
    reduced_normalization_map = OwnedRings().Mor(reduced_localization, normalization)(
        lambda element: in_product(tuple(
            reduced_component_maps[index](element) for index in indices
        ))
    )
    normalization_map = reduced_normalization_map * reduction_map

    def component_projection(position, index):
        component = localized_components[index]
        if len(component_values) == 1:
            return OwnedRings().Mor(normalization, component).identity()
        projection_engine = normalization_engine.cartesian_projection(position)
        return OwnedRings().Mor(normalization, component)(
            lambda element: _owned_engine_element(
                component,
                projection_engine(_engine_element(normalization, element)),
            )
        )

    projections = {
        index: component_projection(position, index)
        for position, index in enumerate(indices)
    }
    components = finite_indexed_family(indices, lambda index: (
        source_data.components.value(index)[0].extension_to_localization(localization),
        localized_components[index],
        component_maps[index],
    ))

    functor = localization.localization_functor()
    normalization_module = functor(source_data.normalization_module)
    localized_unit = functor(source_data.normalization_unit_map)
    localized_regular = localized_unit.domain()
    regular = localization.regular_module()
    (source_label,) = tuple(localized_regular.module_generating_set())
    (regular_label,) = tuple(regular.module_generating_set())
    to_regular = Modules(localization).Mor(localized_regular, regular)(
        {source_label: regular.module_generator(regular_label)}
    )
    from_regular = Modules(localization).Mor(regular, localized_regular)(
        {regular_label: localized_regular.module_generator(source_label)}
    )
    regular_comparison = _isomorphism_from_known_inverse_pair(to_regular, from_regular)
    unit_map = localized_unit * regular_comparison.inverse().forward()

    # The square changes only the actual rank-one source of the unit map.
    # The existing cokernel functor supplies its induced isomorphism, which
    # composes with the localization functor's own cokernel comparison.
    cokernels = Modules(localization).FinitelyPresented().cokernel_arrow_functor()
    arrows = cokernels.domain()
    localized_arrow = arrows(localized_unit)
    regular_arrow = arrows(unit_map)
    module_identity = Modules(localization).Mor(
        normalization_module, normalization_module
    ).identity()
    square = arrows.Mor(localized_arrow, regular_arrow)._from_commuting_edges(
        regular_comparison.forward(), module_identity
    )
    inverse_square = arrows.Mor(regular_arrow, localized_arrow)._from_commuting_edges(
        regular_comparison.inverse().forward(), module_identity
    )
    localized_cokernel_comparison = functor.cokernel_comparison(
        source_data.normalization_unit_map
    )
    cokernel_comparison = _isomorphism_from_known_inverse_pair(
        cokernels(square) * localized_cokernel_comparison.forward(),
        localized_cokernel_comparison.inverse() * cokernels(inverse_square),
    )

    source_regular = source_data.normalization.regular_module()
    (source_regular_label,) = tuple(source_regular.module_generating_set())
    target_regular = normalization.regular_module()
    (target_label,) = tuple(target_regular.module_generating_set())
    target_one = target_regular.module_generator(target_label)
    target = target_regular.restrict_scalars(normalization_map)

    def realized_generator(label):
        source_element = source_data.normalization_module.module_generator(label)
        source_value = source_data.normalization_module_realization(
            source_element
        ).underlying_element()
        coefficient = source_regular.framing_morphism().lift(source_value)(
            source_regular_label
        )
        return target.wrap(target_regular.scalar_multiple(
            normalization_localization_map(coefficient), target_one
        ))

    realization = Modules(localization).Mor(normalization_module, target)(realized_generator)
    normality = conjunction((localization.is_reduced(), unit_map.cokernel().is_zero()))
    coefficient_map = (
        None if source_data.coefficient_map is None
        else localization_map * source_data.coefficient_map
    )

    def component_numerators(index):
        numerators = source_data.component_module_numerators.value(index)
        # Direct affine packets retain polynomial-cover numerators. Read
        # them in their actual source A before applying A -> L. An already
        # localized packet has A-valued numerators and uses the same map.
        return finite_indexed_family(
            numerators.index_set(),
            lambda label: localization_map(source(numerators.value(label))),
        )

    return _AffineNormalizationData(
        normalization,
        normalization_map,
        None,
        None,
        normality,
        components,
        normalization_module_realization=realization,
        normalization_unit_map=unit_map,
        coefficient_map=coefficient_map,
        component_module_numerators=finite_indexed_family(indices, component_numerators),
        component_projections=finite_indexed_family(indices, lambda index: projections[index]),
        reduction_map=reduction_map,
        reduced_normalization_map=reduced_normalization_map,
        normalization_localization_map=normalization_localization_map,
        normalization_regular_comparison=regular_comparison,
        normalization_cokernel_comparison=cokernel_comparison,
    )


def _affine_normalization_module_maps(
    quotient,
    normalization_map,
    components,
    component_numerators,
):
    r"""Present the finite normalization module and retain its actual realization.

    Private construction adapter owned here. Its only caller is
    ``_affine_quotient_normalization_data``. The arguments are the
    owned affine quotient, its normalization ring map, and finite indexed
    families of component triples and exact ordered numerators. The result
    retains the owned module realization and the diagonal unit map.

    For the component prime K_i in A and the ordered numerator family U_i,
    Singular supplies B_i = U_i/c_i inside Frac(A/K_i), with c_i the LAST
    numerator.  The module owner constructs N_i = (U_i+K_i)/K_i from
    the kernel of the map from the free module on these exact labels.
    Division by c_i identifies N_i with B_i.  It is evaluated through the
    unique lift under multiplication by the nonzero c_i in B_i, which need
    not be a unit.

    The finite biproduct N of the N_i realizes Res_nu(B) for B = product B_i.
    Its unit map sends 1 to the sum of the classes labelled by the c_i.
    Its cokernel is therefore B/image(A), with the ONE diagonal image of A.
    Neither this construction nor its realization changes B's parent or
    equips B with a separately constructed underlying module.
    """
    from sage_extensions.categories.modules.pure.modules import Modules

    indices = components.index_set()
    component_values = tuple(components)
    normalization = normalization_map.codomain()
    normalization_engine = _engine_ring(normalization)
    regular = quotient.regular_module()
    (regular_label,) = tuple(regular.module_generating_set())
    regular_one = regular.module_generator(regular_label)
    target_regular = normalization.regular_module()
    (target_label,) = tuple(target_regular.module_generating_set())
    target_one = target_regular.module_generator(target_label)
    target = target_regular.restrict_scalars(normalization_map)

    def in_product(position, value):
        # Coordinate insertion is additive and A-linear; for more than one
        # component it is not unital and must never be made a ring morphism.
        if len(component_values) == 1:
            return value
        values = tuple(
            _engine_element(component, value if other == position else component.zero())
            for other, (_, component, _) in enumerate(component_values)
        )
        return _owned_engine_element(normalization, normalization_engine(values))

    modules = {}
    realization_legs = {}
    unit_labels = {}
    for index in indices:
        prime, component, component_map = components.value(index)
        numerators = component_numerators.value(index)
        labels = numerators.index_set()
        denominator_label = tuple(labels)[-1]
        component_quotient = prime.inclusion().cokernel()
        quotient_projection = component_quotient.cokernel_projection()
        free = quotient.free_module(labels)
        numerator_map = Modules(quotient).Mor(free, component_quotient)(
            {
                label: quotient_projection(
                    regular.scalar_multiple(quotient(numerators.value(label)), regular_one)
                )
                for label in labels
            }
        )
        module = numerator_map.kernel().inclusion().cokernel()
        modules[index] = module
        unit_labels[index] = denominator_label

        component_regular = component.regular_module()
        (component_label,) = tuple(component_regular.module_generating_set())
        component_one = component_regular.module_generator(component_label)
        denominator = component_map(quotient(numerators.value(denominator_label)))
        multiplication = Modules(component).Mor(component_regular, component_regular)(
            {component_label: component_regular.scalar_multiple(denominator, component_one)}
        )
        images = {}
        for label in labels:
            numerator = component_map(quotient(numerators.value(label)))
            preimage = multiplication.lift(
                component_regular.scalar_multiple(numerator, component_one)
            )
            value = component_regular.framing_morphism().lift(preimage)(component_label)
            images[label] = target.wrap(
                target_regular.scalar_multiple(in_product(int(index), value), target_one)
            )
        realization_legs[index] = Modules(quotient).Mor(module, target)(images)

    normalization_module = Modules(quotient).biproduct(
        finite_indexed_family(indices, lambda index: modules[index])
    )
    realization = normalization_module.from_coproduct_cocone(
        finite_indexed_family(indices, lambda index: realization_legs[index])
    )
    unit = sum(
        (
            normalization_module.injection(index)(
                modules[index].module_generator(unit_labels[index])
            )
            for index in indices
        ),
        normalization_module.zero(),
    )
    unit_map = Modules(quotient).Mor(regular, normalization_module)({regular_label: unit})
    return realization, unit_map


def _affine_quotient_normalization_data(quotient):
    r"""Cross Singular ``normal.lib`` output back into owned affine algebra data.

    This adapter intentionally uses Sage's persistent Singular interface rather
    than an ad-hoc process or textual file protocol.  ``normal.lib`` computes
    the normalization componentwise for the reduction of an affine quotient.
    Its input is the radical ideal, as required by ``normalConductor``.
    The source of all returned ring and module maps remains the original
    quotient ``A=P/I``. Thus the unit cokernel is ``B/image(A)``, even when
    the canonical map has the nonzero kernel ``sqrt(I)/I``.
    The returned Singular ring is converted by Sage's own ``sage()`` crossing,
    then reconstructed through the source ring's ``quotient_ring`` and ``Mor`` methods.
    """
    from sage_extensions.categories.modules.pure.modules import Modules

    source = quotient.quotient_source()
    source_engine = _engine_ring(source)
    assert source.algebra_base_ring() in OwnedRings().Division().Commutative(), (
        "affine normalization currently requires an actual coefficient field"
    )
    assert source in SymmetricAlgebras(source.algebra_base_ring()), (
        "affine normalization currently requires a symmetric-algebra presentation"
    )
    assert source.algebra_generating_set() in FiniteSets(), (
        "affine normalization currently requires a finite symmetric-algebra presentation"
    )

    coefficient_map = quotient.quotient_map() * source.algebra_structure_morphism()
    if quotient._is_zero_ring() is True:
        return _identity_affine_normalization_data(
            quotient,
            coefficient_map,
            finite_indexed_family(finite_ordered_set(()), lambda index: None),
        )

    defining = quotient.defining_ideal()
    radical = defining.radical()
    reduced = radical == defining
    reduction = quotient if reduced is True else source.quotient_ring(radical)
    reduction_map = (
        OwnedRings().Mor(quotient, quotient).identity()
        if reduction is quotient
        else OwnedRings().Mor(quotient, reduction)(
            lambda element: reduction(quotient(element).lift())
        )
    )
    defining_engine = _engine_ideal(source, radical)
    from sage.interfaces.singular import singular

    previous_ring = singular.current_ring()
    try:
        source_engine._singular_(singular).set_ring()
        singular.lib("normal.lib")
        defining_singular = defining_engine._singular_(singular)
        normal_data = defining_singular.normal("useRing", "withDelta", "prim")

        normal_rings = normal_data[1]

        # Retain the native diagnostic on the radical input. The public
        # conductor is Ann_A(B/image(A)) in the original quotient A.
        source_engine._singular_(singular).set_ring()
        conductor_singular = defining_singular.normalConductor(normal_data)
        conductor_engine = conductor_singular.sage(source_engine)
        conductor = source.ideal(
            *(
                _owned_engine_element(source, source_engine(generator))
                for generator in conductor_engine.gens()
            )
        )

        total_delta = int(normal_data[3][2].sage())

        # These ideals live in the ORIGINAL polynomial ring.  Their exact
        # generator order is data: the last entry is the common denominator.
        # computeRing may eliminate variables of the normalization cover, so
        # these positions are not positions of its polynomial generators.
        source_engine._singular_(singular).set_ring()
        module_numerator_families = []
        for position in range(1, len(normal_rings) + 1):
            numerator_singular = normal_data[2][position]
            # Converting the ideal as a whole would call a Sage ideal
            # constructor, which may normalize its generators. These
            # positions, especially the final denominator, are retained data.
            numerators = tuple(
                _owned_engine_element(source, generator.sage_poly(source_engine))
                for generator in numerator_singular
            )
            if not numerators:
                raise ArithmeticError(
                    f"Singular returned no numerator or denominator for normalization component {position}"
                )
            labels = finite_ordered_set(range(len(numerators)))
            module_numerator_families.append(
                finite_indexed_family(
                    labels,
                    lambda label, numerators=numerators: numerators[int(label)],
                )
            )

        source_quotient_engine = _engine_ring(quotient)
        normalizations = []
        normalization_maps = []
        component_primes = []
        from sage_extensions.categories.rings.commutative_ideals import (
            _from_engine_ideal,
        )

        for position in range(1, len(normal_rings) + 1):
            normal_ring_singular = normal_rings[position]
            normal_ring_singular.set_ring()
            normal_cover_engine = normal_ring_singular.sage()
            normal_ideal_engine = singular("norid").sage(normal_cover_engine)
            # These are the images of the ordered source variables, not an
            # ideal to canonicalize in the normalization cover.
            normal_map_images = tuple(
                generator.sage_poly(normal_cover_engine)
                for generator in singular("normap")
            )
            # Singular returned a polynomial presentation with these literal
            # coefficient ring and ordered variable labels. Reconstruct the
            # owned cover from that datum rather than adopting the returned
            # engine parent as a second ring object.
            normal_cover = _own_ring(normal_cover_engine.base_ring()).polynomial_ring(
                tuple(normal_cover_engine.variable_names())
            )
            normal_ideal = normal_cover.ideal(
                *(
                    _owned_engine_element(normal_cover, normal_cover_engine(generator))
                    for generator in normal_ideal_engine.gens()
                )
            )
            component = normal_cover.quotient_ring(normal_ideal)
            target_engine = _engine_ring(component)
            target_images = tuple(
                target_engine(generator)
                for generator in normal_map_images
            )
            if len(target_images) != source_engine.ngens():
                raise ArithmeticError(
                    f"the normalization map of {quotient} must send each of the {source_engine.ngens()} generators of "
                    f"{source} to one element, but Singular returned {len(target_images)} images"
                )
            source_component_map = source_engine.hom(target_images, target_engine)
            source_prime = _from_engine_ideal(source, source_component_map.kernel())
            component_prime = quotient.ideal(
                *(quotient(generator) for generator in source_prime.ideal_generators())
            )
            engine_component_map = source_quotient_engine.hom(target_images, target_engine)
            def component_image(
                element,
                component=component,
                engine_component_map=engine_component_map,
            ):
                return _owned_engine_element(component,
                    engine_component_map(_engine_element(quotient, element))
                )

            component_map = _ring_morphism_with_engine(
                quotient, component, component_image, engine_component_map
            )
            normalizations.append(component)
            normalization_maps.append(component_map)
            component_primes.append(component_prime)

        normalizations = tuple(normalizations)
        normalization_maps = tuple(normalization_maps)
        component_primes = tuple(component_primes)
        normalization = OwnedRings().product(normalizations)
        if len(normalizations) == 1:
            normalization_map = normalization_maps[0]
        else:
            product_engine = _engine_ring(normalization)

            def into_product(element, normalization=normalization, product_engine=product_engine):
                values = tuple(map_(element) for map_ in normalization_maps)
                backend = product_engine(
                    tuple(
                        _engine_element(component, value)
                        for component, value in zip(normalizations, values, strict=True)
                    )
                )
                return _owned_engine_element(normalization, backend)

            normalization_map = OwnedRings().Mor(quotient, normalization)(into_product)

        if reduction is quotient:
            reduced_normalization_map = normalization_map
        else:
            reduced_normalization_map = OwnedRings().Mor(reduction, normalization)(
                lambda element, source_map=normalization_map: source_map(
                    quotient(reduction(element).lift())
                )
            )
            normalization_map = reduced_normalization_map * reduction_map

        component_indices = finite_ordered_set(range(len(normalizations)))
        components = finite_indexed_family(
            component_indices,
            lambda position: (
                component_primes[int(position)],
                normalizations[int(position)],
                normalization_maps[int(position)],
            ),
            name=f"Normalized components of {quotient}",
        )
        component_module_numerators = finite_indexed_family(
            component_indices,
            lambda position: module_numerator_families[int(position)],
        )
        module_realization, unit_map = _affine_normalization_module_maps(
            quotient,
            normalization_map,
            components,
            component_module_numerators,
        )
        normality = conjunction((reduced, unit_map.cokernel().is_zero()))
        if normality is True:
            # For reduced A, eta is injective. Its zero cokernel makes it
            # an isomorphism, so its unique lifts realize the SAME selected
            # N and numerator labels in A with identity normalization.
            normalization = quotient
            normalization_map = OwnedRings().Mor(quotient, quotient).identity()
            reduced_normalization_map = normalization_map
            normalization_module = unit_map.codomain()
            target = unit_map.domain().restrict_scalars(normalization_map)
            module_realization = Modules(quotient).Mor(normalization_module, target)(
                {
                    label: target.wrap(unit_map.lift(normalization_module.module_generator(label)))
                    for label in normalization_module.module_generating_set()
                }
            )

        def component_projection(position):
            component = normalizations[int(position)]
            if normality is True:
                return normalization_maps[int(position)]
            if len(normalizations) == 1:
                return OwnedRings().Mor(normalization, component)(lambda element: element)
            projection_engine = product_engine.cartesian_projection(int(position))
            return OwnedRings().Mor(normalization, component)(
                lambda element: _owned_engine_element(
                    component,
                    projection_engine(_engine_element(normalization, element)),
                )
            )

        component_projections = finite_indexed_family(
            component_indices,
            component_projection,
        )
        return _AffineNormalizationData(
            normalization,
            normalization_map,
            quotient.ideal(*(quotient(generator) for generator in conductor.ideal_generators())),
            total_delta,
            normality,
            components,
            normalization_module_realization=module_realization,
            normalization_unit_map=unit_map,
            coefficient_map=coefficient_map,
            component_module_numerators=component_module_numerators,
            component_projections=component_projections,
            reduction_map=reduction_map,
            reduced_normalization_map=reduced_normalization_map,
        )
    finally:
        if previous_ring is not None:
            previous_ring.set_ring()







class QuotientLocalizationComparison(SageObject):
    r"""The canonical compatibility of quotient and localization."""

    def __init__(
        self,
        source_quotient,
        localization_ring,
        localized_quotient,
        quotient_after_localization,
        forward,
        inverse,
        extended_ideal,
    ) -> None:
        self._source_quotient = source_quotient
        self._localization_ring = localization_ring
        self._localized_quotient = localized_quotient
        self._quotient_after_localization = quotient_after_localization
        self._forward = forward
        self._inverse = inverse
        self._extended_ideal = extended_ideal

    def source_quotient(self):
        return self._source_quotient

    def localization_ring(self):
        return self._localization_ring

    def localized_quotient(self):
        r"""Return ``S^{-1}(R/I)``."""
        return self._localized_quotient

    def quotient_after_localization(self):
        r"""Return ``S^{-1}R/S^{-1}I``."""
        return self._quotient_after_localization

    def extended_ideal(self):
        return self._extended_ideal

    def forward(self):
        return self._forward

    isomorphism = forward

    def inverse(self):
        return self._inverse

    def _repr_(self):
        return (
            f"{self.localized_quotient()} ~= "
            f"{self.quotient_after_localization()}"
        )


class QuotientCompletionComparison(SageObject):
    r"""The canonical Noetherian comparison ``(R/J)^ ~= R^/J R^``."""

    def __init__(
        self,
        source_quotient,
        source_ideal,
        source_completion,
        completed_quotient,
        quotient_after_completion,
        extended_defining_ideal,
        forward,
        inverse,
    ) -> None:
        self._source_quotient = source_quotient
        self._source_ideal = source_ideal
        self._source_completion = source_completion
        self._completed_quotient = completed_quotient
        self._quotient_after_completion = quotient_after_completion
        self._extended_defining_ideal = extended_defining_ideal
        self._forward = forward
        self._inverse = inverse

    def source_quotient(self):
        return self._source_quotient

    def source_ideal(self):
        return self._source_ideal

    def source_completion(self):
        return self._source_completion

    def completed_quotient(self):
        r"""Return ``(R/J)^`` completed at the image of ``I``."""
        return self._completed_quotient

    def quotient_after_completion(self):
        r"""Return ``R^ / J R^``."""
        return self._quotient_after_completion

    def extended_defining_ideal(self):
        return self._extended_defining_ideal

    def forward(self):
        return self._forward

    isomorphism = forward

    def inverse(self):
        return self._inverse

    def _repr_(self):
        return (
            f"{self.completed_quotient()} ~= "
            f"{self.quotient_after_completion()}"
        )


class MaximalAdicLocalizationCompletionComparison(SageObject):
    r"""The canonical comparison ``R^_m ~= (R_m)^`` for Noetherian ``R``."""

    def __init__(
        self,
        source_completion,
        local_ring,
        local_completion,
        forward,
        inverse,
    ) -> None:
        self._source_completion = source_completion
        self._local_ring = local_ring
        self._local_completion = local_completion
        self._forward = forward
        self._inverse = inverse

    def source_completion(self):
        return self._source_completion

    def local_ring(self):
        return self._local_ring

    def local_completion(self):
        return self._local_completion

    def forward(self):
        return self._forward

    isomorphism = forward

    def inverse(self):
        return self._inverse

    def _repr_(self):
        return f"{self.source_completion()} ~= {self.local_completion()}"






class PrimeLocalizations(OwnedCategory):
    r"""Prime local rings ``R_p`` represented by fractions with denominator outside ``p``."""

    def an_object(self):
        return _owned_integers().localize_at_prime(2)

    def super_categories(self):
        r"""``R_p`` is the localization at the multiplicative set ``R \ p``."""
        return [LocalizationRings().Local()]

    class ElementMethods:
        def _unit_inverse_decision(self):
            match self.is_unit():
                case True:
                    pass
                case False:
                    raise ZeroDivisionError(f"{self} is not a unit in {self.parent()}")
                case _:
                    return None
            return self.parent().fraction(
                self.denominator(),
                self.numerator(),
            )

    class ParentMethods:
        def __init__(
            self,
            source,
            submonoid,
            *,
            engine_ring=None,
            **rest,
        ) -> None:
            base = source.base_ring()
            algebra_source = (
                source
                if base is not None and source in Algebras(base).Associative().Unital()
                else None
            )
            super().__init__(
                source,
                submonoid,
                _engine_ring=engine_ring,
                algebra_source=algebra_source,
                **rest,
            )

        def _krull_dimension_decision(self):
            r"""Return ``dim R_p``, the height of ``p``.

            The primes of ``R_p`` are the ``qR_p`` for the primes ``q`` of
            ``R`` inside ``p``, in order-preserving bijection, so a chain in
            ``R_p`` is a chain in ``R`` ending at ``p``.
            In the dimension-formula regime we can compute this intrinsic
            dimension from source and quotient dimensions.  Outside that
            regime no such equality is assumed.
            """
            source = self.localization_source()
            finite_type_source = source.quotient_source() if source in QuotientRings() else source
            finite_type_base = finite_type_source.base_ring()
            if (
                source in OwnedRings().Commutative().NoZeroDivisors()
                and (
                    source in OwnedRings().Commutative().NoZeroDivisors().PrincipalIdeals()
                    or (
                        finite_type_base in OwnedRings().Division().Commutative()
                        and finite_type_source in (
                            Algebras(finite_type_base).Associative().Unital().FinitelyGeneratedAsAlgebra()
                        )
                    )
                )
            ):
                return source.krull_dimension() - source.quotient_ring(self.localized_prime()).krull_dimension()
            assert False, (
                f"the intrinsic dimension of {self} requires a prime-chain or independent local-dimension "
                "realization outside the represented dimension-formula regime"
            )

        @cached_method
        def _selected_local_ring_construction(self):
            r"""Supply the actual local quotient datum of ``R_p`` lazily.

            Implements the protected ring-construction contract. The maximal
            ideal is the extension ``p R_p``. Its residue field is
            ``Frac(R/p)`` because the images of ``R \\ p`` in the domain
            ``R/p`` are precisely the nonzero elements. This needs no fraction
            field of R, even when R is reducible or nonreduced.

            The existing datum stores fixed factories separately: asking for
            ``p R_p`` does not construct the residue field. The residue-map
            factory uses the actual source quotient directly, so it never
            calls ``source_residue_map`` recursively.
            """
            source = self.localization_source()
            prime = self.localized_prime()

            def residue_field():
                quotient = source.quotient_ring(prime)
                if quotient in OwnedRings().Division().Commutative():
                    return quotient
                return quotient.fraction_field()

            def residue_map():
                quotient = source.quotient_ring(prime)
                residue = construction.residue_field()
                source_map = quotient.quotient_map()
                if residue is not quotient:
                    source_map = _canonical_map(quotient, residue) * source_map
                return self._induced_morphism_from_unit_images(source_map)

            construction = LocalRingConstruction(
                maximal_ideal_factory=lambda: prime.extension_to_localization(self),
                residue_field_factory=residue_field,
                residue_map_factory=residue_map,
            )
            return construction

        def localized_prime(self):
            structure = self.localization_submonoid()._structure_data()
            if structure.get("kind") != "prime_complement":
                raise ArithmeticError(
                    f"{self} is not the localization R_p at a prime p: its multiplicative set is not the "
                    "complement of a prime ideal"
                )
            prime = structure.get("prime_ideal")
            if prime is None:
                raise ArithmeticError(
                    f"{self} is a localization R_p at the complement of a prime, but the prime ideal p is missing"
                )
            return prime


class IdealExtensionData(SageObject):
    r"""One ideal extension ``I -> I S`` along a represented ring morphism.

    The extended ideal remains the canonical ideal subobject of the codomain;
    this construction object retains the source ideal and the morphism that
    produced it without making either one part of the ideal's identity.
    """

    def __init__(self, morphism, source_ideal) -> None:
        if source_ideal.ring() is not morphism.domain():
            raise ValueError(
                f"cannot extend the ideal {source_ideal} along {morphism}: it is an ideal of "
                f"{source_ideal.ring()}, but the morphism starts at {morphism.domain()}"
            )
        self._morphism = morphism
        self._source_ideal = source_ideal
        self._extended_ideal = morphism.extension_of_ideal(source_ideal)

    def morphism(self):
        return self._morphism

    extension_map = morphism

    def source_ideal(self):
        return self._source_ideal

    def extended_ideal(self):
        return self._extended_ideal

    def _repr_(self):
        return (
            f"Extension of {self.source_ideal()} along {self.morphism()} "
            f"to {self.extended_ideal()}"
        )


class AdicCompletions(Category):
    r"""Adic completions equipped with a source ring and its chosen completion ideal."""

    def an_object(self):
        r"""The 2-adic completion of the owned integers."""
        from sage.rings.integer_ring import ZZ as SageZZ

        integers = _owned_integers()
        return self(integers, integers.ideal(integers(2)), precision=4)

    def super_categories(self):
        return [OwnedAdicallyCompleteRings()]

    def _call_(self, ring, ideal, *, precision=20):
        r"""Construct the adic completion from its authoritative defining datum.

        Public notation and ring methods both route through this category
        constructor.  The private cached constructor receives only owned data,
        so repeated routes to the same ``(R,I,precision)`` return the same
        mathematical parent rather than parallel completion objects.
        """
        source = _own_ring(ring)
        defining = _owned_ideal(source, ideal)
        return _adic_completion_from_owned_data(
            source,
            defining,
            int(precision),
        )

    class Local(CategoryWithAxiom):
        r"""Selected adic completions whose completed ring is local."""

        def an_object(self):
            r"""The 2-adic completion of the integers."""
            return _owned_integers().adic_completion(2)

        class ParentMethods:
            @cached_method
            def source_residue_map(self):
                r"""Compose the retained completion map with the local residue map."""
                return self.residue_map() * self.completion_map()

    class ParentMethods:
        def completion_source(self):
            return self._adic_completion_source

        def completion_ideal(self):
            r"""Return the retained ideal ``I`` of ``completion_source()``.

            Its extension along ``completion_map()`` is the defining ideal
            of this completed ring, returned by ``ideal_of_definition()``.
            """
            return self._adic_completion_ideal

        def completion_map(self):
            morphism = self._realized_completion_map
            if morphism is None:
                morphism = self._adic_completion_map_factory()
                if (
                    morphism.domain() is not self.completion_source()
                    or morphism.codomain() is not self
                ):
                    raise ValueError(
                        f"the completion map of {self} must be {self.completion_source()} -> {self}, "
                        f"but the supplied map is {morphism.domain()} -> {morphism.codomain()}"
                    )
                self._realized_completion_map = morphism
            return morphism

        def _completion_projection_lift(self):
            r"""Return the retained finite-stage lift used to realize adic projections.

            Protected completion-realization contract. Its callers are this
            completion's projection operation and the prime-localization
            completion constructor, which transports the same retained lift
            through the localization map.
            """
            return self._adic_projection_lift

        @cached_method
        def ideal_extension(self):
            r"""Realize the fixed construction ``I -> I A^`` along the completion map.

            The source ideal and map are fixed at construction; evaluating
            their extension stays lazy, at this existing algorithm boundary.
            """
            return IdealExtensionData(
                self.completion_map(),
                self.completion_ideal(),
            )

        def extended_ideal(self):
            r"""Return ``I A^``, retaining its extension construction separately."""
            return self.ideal_extension().extended_ideal()

        @cached_method
        def truncation_ideal_extension(self, exponent):
            r"""Return the image ideal of ``I`` in ``A/I^exponent`` with its map."""
            target = self.adic_truncation(exponent)
            return IdealExtensionData(
                target.quotient_map(),
                self.completion_ideal(),
            )

        @cached_method
        def _completion_map_kernel_decision(self):
            r"""Supply the source kernel from retained data or the current exact cases.

            This protected completion decision is consumed only by
            ``completion_map_kernel``, the source-separatedness predicate,
            and exact-source element equality. Its result is an owned ideal
            of the retained source, or ``None`` when these computations do
            not establish that ideal. Constructor-supplied kernels are fixed
            data; finite precision by itself supplies no kernel.
            """
            source = self.completion_source()
            represented = self._adic_completion_map_kernel
            if represented is not None:
                return represented
            zero = source.ideal(source.zero())
            defining = self.completion_ideal()
            if (defining == zero) is True:
                return zero
            square = defining.power(2)
            if (square == zero) is True:
                return zero
            if (square == defining) is True:
                return defining
            supported_by_krull_intersection = (
                source in OwnedRings().Noetherian()
                and (
                    source in OwnedRings().Commutative().NoZeroDivisors()
                    or source in OwnedRings().Commutative().Local()
                )
                and defining.contains_ambient_element(source.one()) is False
            )
            if supported_by_krull_intersection:
                return zero
            return None

        def completion_map_kernel(self):
            r"""Return ``ker(R -> R_hat) = intersection I^n``.

            The retained, square-zero, and idempotent cases use their exact
            source ideals. Krull intersection gives zero for a proved proper
            ideal in a Noetherian domain or Noetherian local ring.
            """
            kernel = self._completion_map_kernel_decision()
            assert kernel is not None, (
                f"cannot compute ker({self.completion_source()} -> {self}), the intersection "
                f"of the powers of {self.completion_ideal()}: no represented kernel or "
                "applicable exact source-ideal computation is supplied"
            )
            return kernel

        def is_adically_separated(self):
            r"""Return whether the retained source is separated for its completion ideal."""
            kernel = self._completion_map_kernel_decision()
            if kernel is None:
                return AtomicProposition("is_adically_separated", self)
            return kernel.is_zero()

        def is_completion_map_injective(self):
            r"""Return injectivity exactly when the represented kernel is known."""
            return self.is_adically_separated()

        def is_flat_over_source(self):
            r"""Return flatness of ``A^`` over ``A`` in the Noetherian regime, else the proposition."""
            if self.completion_source() in OwnedRings().Noetherian():
                return True
            return AtomicProposition("is_flat_over_source", self)

        def computation_precision(self):
            return self._adic_completion_precision

        @cached_method
        def adic_inverse_system(self):
            r"""Return the represented inverse system ``n |-> A/I^(n+1)``."""
            functor = _AdicQuotientInverseSystem(self)
            return functor.system_category().object(functor)

        @cached_method
        def adic_truncation(self, exponent):
            r"""Return the canonical adic quotient ``A / I^exponent``.

            It is not called an Artin quotient without a finite-length
            hypothesis: for example ``QQ[x,y]/(x^n)`` still has positive
            dimension.
            """
            exponent = int(exponent)
            if exponent <= 0:
                raise ValueError(f"the truncation A/I^n needs n > 0, but n = {exponent}")
            source = self.completion_source()
            defining = self.completion_ideal()
            return source.quotient_ring(defining.power(exponent))

        def adic_artin_truncation(self, exponent):
            r"""Return ``A/I^exponent`` after requiring it to be Artinian."""
            quotient = self.adic_truncation(exponent)
            if quotient not in OwnedRings().Artinian():
                raise ValueError(
                    f"{quotient} is not known to be Artinian, so it has not been shown to have finite length"
                )
            return quotient

        @cached_method
        def adic_transition_map(self, higher_exponent, lower_exponent):
            r"""Return ``A/I^higher -> A/I^lower`` for ``higher >= lower``."""
            higher_exponent = int(higher_exponent)
            lower_exponent = int(lower_exponent)
            if lower_exponent <= 0 or higher_exponent < lower_exponent:
                raise ValueError(
                    f"the transition map A/I^m -> A/I^n needs m >= n > 0, but m = {higher_exponent} and "
                    f"n = {lower_exponent}"
                )
            higher = self.adic_truncation(higher_exponent)
            lower = self.adic_truncation(lower_exponent)
            lower_projection = lower.quotient_map()
            return OwnedRings().Mor(higher, lower)(
                lambda element: lower_projection(element.lift()),
            )

        @cached_method
        def adic_projection(self, exponent):
            r"""Return the canonical projection ``A_hat -> A/I^exponent``."""
            exponent = int(exponent)
            if exponent <= 0:
                raise ValueError(f"the projection A^ -> A/I^n needs n > 0, but n = {exponent}")
            target = self.adic_truncation(exponent)
            quotient_map = target.quotient_map()
            projection_lift = self._completion_projection_lift()

            def image(element):
                selected = self(element)
                source_expression = selected.exact_source_expression()
                if source_expression is not None:
                    return quotient_map(source_expression)
                assert projection_lift is not None, (
                    f"cannot compute the projection {self} -> {target} at {element}: "
                    "neither an exact source expression nor a finite-stage reduction is supplied"
                )
                backend = _engine_element(self, selected)
                return quotient_map(projection_lift(backend, exponent))

            return OwnedRings().Mor(self, target)(image)

        def induced_map(self, source_morphism, target_completion):
            r"""Extend the given ring map to the chosen complete target.

            A map from the source ``R`` may end at the complete target ``B``
            itself, with ``f(I)`` inside its chosen defining ideal, or at
            another completion's source ``S``, with ``f(I)`` inside that
            source's completion ideal. In the latter case it is composed
            with ``S -> B``. These sufficient continuity data determine a
            unique continuous map ``R_hat -> B``. Evaluation uses the retained exact
            source expression and otherwise keeps its computation boundary.
            """
            if target_completion not in OwnedAdicallyCompleteRings():
                raise TypeError(
                    f"an induced completion map needs a chosen complete target, but got {target_completion}"
                )
            if source_morphism.domain() is not self.completion_source():
                raise ValueError(
                    f"cannot induce a map of completions from {source_morphism}: it must start at "
                    f"{self.completion_source()}, but it starts at {source_morphism.domain()}"
                )
            source_map_owner = OwnedRings().Mor(
                self.completion_source(), source_morphism.codomain()
            )
            if source_morphism not in source_map_owner:
                raise TypeError(
                    f"an induced completion map requires an owned unital ring map, but got {source_morphism}"
                )
            if (
                source_morphism.domain() is source_morphism.codomain()
                and (
                    source_morphism is source_morphism.parent().identity()
                    or source_morphism.is_identity() is True
                )
                and target_completion is self
            ):
                return OwnedRings().Mor(self, self).identity()

            if source_morphism.codomain() is target_completion:
                target_ideal = target_completion.ideal_of_definition()
                into_target = source_morphism
            elif (
                target_completion in AdicCompletions()
                and source_morphism.codomain() is target_completion.completion_source()
            ):
                target_ideal = target_completion.completion_ideal()
                into_target = target_completion.completion_map() * source_morphism
            else:
                raise ValueError(
                    f"cannot induce a map {self} -> {target_completion} from {source_morphism}: "
                    "it must end at that complete target or its retained completion source"
                )
            continuity = conjunction(
                target_ideal.contains_ambient_element(source_morphism(generator))
                for generator in self.completion_ideal().ideal_generators()
            )
            match continuity:
                case True:
                    pass
                case False:
                    raise ValueError("the source completion ideal does not map into the selected target ideal")
                case _:
                    assert False, (
                        f"the induced map {self} -> {target_completion} requires the images of "
                        f"{self.completion_ideal()} to be established inside {target_ideal}"
                    )

            def image(element):
                selected = self(element)
                source_expression = selected.exact_source_expression()
                if source_expression is None:
                    raise AssertionError(
                        f"cannot evaluate the induced map of completions at {element}: it is not known as the image "
                        f"of an element of {self.completion_source()}"
                    )
                return into_target(source_expression)

            return OwnedRings().Mor(self, target_completion)(image)

        @cached_method
        def maximal_localization_comparison(self):
            r"""Return ``R^_m ~= (R_m)^`` when the source completion ideal is maximal.

            Each ``R/m^n`` is local, so localizing it outside the maximal
            ideal changes nothing; the inverse limits therefore agree.
            The current realization uses Noetherian source computations.
            Both arrows use the existing localization/completion universal
            maps, with their retained-source evaluation boundary.
            """
            source = self.completion_source()
            maximal = self.completion_ideal()
            assert source in OwnedRings().Noetherian(), (
                f"the comparison of completion and localization at a maximal ideal is computed here "
                f"for Noetherian source rings; no source computation is supplied for {source}"
            )
            match maximal.is_maximal():
                case True:
                    pass
                case False:
                    raise TypeError(
                        f"the comparison of completion and localization needs a maximal completion ideal, but "
                        f"{maximal} is not maximal in {source}"
                    )
                case _:
                    assert False, (
                        f"the comparison of completion and localization requires maximality of {maximal} "
                        f"in {source} to be established"
                    )
            local = source.localize_at_prime(maximal)
            local_completion = local.adic_completion(
                local.maximal_ideal(),
                precision=self.computation_precision(),
            )
            forward = self.induced_map(local.localization_map(), local_completion)
            local_to_completion = local._induced_morphism_from_unit_images(self.completion_map())
            inverse = local_completion.induced_map(local_to_completion, self)
            return MaximalAdicLocalizationCompletionComparison(
                self,
                local,
                local_completion,
                forward,
                inverse,
            )

        @cached_method
        def adic_limit_cone(self):
            r"""Return the canonical cone ``A_hat -> (A/I^n)_n``."""
            system = self.adic_inverse_system()
            diagram = system.functor()
            return system.Cones().cone(
                self,
                lambda index: self.adic_projection(diagram.exponent(index)),
            )

        @cached_method
        def adic_limit_construction(self):
            r"""Return the selected inverse-limit construction defining this completion.

            The represented completion and its cone are exact.  Constructing a
            map into an arbitrary infinite inverse limit from a supplied coherent
            cone is not implemented by the generic finite product/equalizer
            solver; the supported series engine is the selected realization of
            this particular limit.
            """
            system = self.adic_inverse_system()
            diagram = system.functor()
            cone = self.adic_limit_cone()

            def factorizer(supplied_cone):
                assert supplied_cone is cone, (
                    f"cannot factor the cone {supplied_cone} through the limit {self}: only the limit cone "
                    "itself factors here, because compatible series are not constructed"
                )
                return OwnedRings().Mor(self, self).identity()

            return SelectedLimitConstruction(diagram, cone, factorizer)


class _AdicQuotientInverseSystem(Functor):
    r"""The inverse system ``A/I <- A/I^2 <- ...`` owned by one completion."""

    def __init__(self, completion) -> None:
        self._completion = completion
        self._base_index = PosetCategory(NN)
        self._system_category = InverseSystem(
            self._base_index,
            OwnedRings().Commutative(),
        )
        super().__init__(
            self._system_category.index_category(),
            OwnedRings().Commutative(),
        )

    def completion(self):
        return self._completion

    def base_index_category(self):
        return self._base_index

    def system_category(self):
        return self._system_category

    def exponent(self, index):
        return NN(int(index.underlying_object().value()) + 1)

    def _apply_object(self, index):
        return self.completion().adic_truncation(self.exponent(index))

    def _apply_morphism(self, morphism):
        underlying = morphism.underlying_arrow()
        lower = int(underlying.domain().value()) + 1
        higher = int(underlying.codomain().value()) + 1
        return self.completion().adic_transition_map(higher, lower)


class _AdicCompletionElement(_OwnedAlgebraElement):
    r"""An element of a completion with equality respecting its information model."""

    def __init__(self, parent, backend_value, *, exact_source_expression=None) -> None:
        super().__init__(parent, backend_value)
        self._exact_source_expression = exact_source_expression

    def exact_source_expression(self):
        r"""Return the retained exact source expression, or ``None``.

        A finite computational approximation does not become exact merely by
        living in the completion.  Expressions arriving through the completion
        map, however, still carry their exact source expression, and ordinary
        ring operations preserve that information while both operands have it.
        """
        return self._exact_source_expression

    def _cache_key(self):
        r"""Return a conservative key for caches that accept completion elements.

        Exact source expressions determine exact completion elements, so they
        may key by that retained datum.  Without such an expression, finite
        completion data need not decide equality; identity is then the only
        sound cache key and deliberately does not merge two representatives.
        """
        source_expression = self.exact_source_expression()
        match source_expression:
            case None:
                return (self.parent(), id(self))
            case _:
                return (self.parent(), source_expression)

    def _with_source_expression(self, backend_value, source_expression):
        return self.parent()._completion_element(
            backend_value,
            source_expression=source_expression,
        )

    def _add_(self, other):
        left_source = self.exact_source_expression()
        right_source = other.exact_source_expression()
        source_expression = None
        if left_source is not None and right_source is not None:
            source_expression = left_source + right_source
        return self._with_source_expression(
            self._backend() + other._backend(),
            source_expression,
        )

    def _mul_(self, other):
        left_source = self.exact_source_expression()
        right_source = other.exact_source_expression()
        source_expression = None
        if left_source is not None and right_source is not None:
            source_expression = left_source * right_source
        return self._with_source_expression(
            self._backend() * other._backend(),
            source_expression,
        )

    def __mul__(self, other):
        r"""Multiply while retaining exact source data for completion scalars."""
        from sage_extensions.categories.modules.pure.modules import Modules

        other_parent = element_parent(other)
        if other_parent is not self.parent() and other_parent in Modules(self.parent()):
            return other_parent.scalar_multiple(self, other)
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return self._mul_(other)

    def __rmul__(self, other):
        r"""Multiply a coerced left scalar without dropping exact source data."""
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return other._mul_(self)

    def _neg_(self):
        source_expression = self.exact_source_expression()
        if source_expression is not None:
            source_expression = -source_expression
        return self._with_source_expression(-self._backend(), source_expression)

    def __pow__(self, exponent, modulus=None):
        if modulus is not None:
            return super().__pow__(exponent, modulus)
        try:
            exponent = exponent.__index__()
        except AttributeError:
            return NotImplemented
        source_expression = self.exact_source_expression()
        if source_expression is not None and exponent >= 0:
            source_expression = source_expression**exponent
        else:
            source_expression = None
        return self._with_source_expression(
            self._backend() ** exponent,
            source_expression,
        )

    def _exact_source_equality_status(self, other):
        left_source = self.exact_source_expression()
        right_source = other.exact_source_expression()
        if left_source is None or right_source is None:
            return None
        difference = left_source - right_source
        if (difference == self.parent().completion_source().zero()) is True:
            return True
        kernel = self.parent()._completion_map_kernel_decision()
        if kernel is None:
            return None
        return kernel.contains_ambient_element(difference)

    def _completion_equal(self, other):
        parent = self.parent()
        try:
            other = parent(other)
        except (TypeError, ValueError):
            return False
        if self is other:
            return True
        left = self._backend()
        right = other._backend()
        source_status = self._exact_source_equality_status(other)
        if source_status is not None:
            return source_status
        mode = parent.completion_arithmetic_mode()
        if mode == "exact_backend":
            return bool(left == right)
        if mode == "exact_lazy":
            options = left.parent().options
            old_secure = options["secure"]
            options["secure"] = True
            try:
                return bool(left == right)
            finally:
                options["secure"] = old_secure
        difference = left - right
        if bool(difference):
            return False
        return AtomicProposition("equal", self, other)

    def __eq__(self, other):
        return self._completion_equal(other)

    def __ne__(self, other):
        return negation(self._completion_equal(other))

    __hash__ = None

    def __bool__(self):
        return bool(negation(self._completion_equal(self.parent().zero())))

    def is_zero(self):
        return self._completion_equal(self.parent().zero())

    def is_one(self):
        return self._completion_equal(self.parent().one())

    def _unit_decision(self):
        return bool(self._backend().is_unit())

    def _unit_inverse_decision(self):
        match self.is_unit():
            case True:
                pass
            case False:
                raise ZeroDivisionError(f"{self} is not a unit in {self.parent()}")
            case _:
                return None
        return _owned_engine_element(self.parent(), self._backend() ** -1)

    def precision_absolute(self):
        r"""Return the selected absolute computation precision when represented."""
        if self.parent().completion_arithmetic_mode() == "finite_precision":
            return self._backend().precision_absolute()
        return self.parent().computation_precision()

    def refine_precision(self, precision):
        r"""Refine an exact source image without inventing missing coefficients."""
        source_expression = self.exact_source_expression()
        if source_expression is None:
            raise AssertionError(
                f"cannot refine the precision of {self} to {precision}: it is not known as the image of an "
                "element of the ring being completed"
            )
        refined = self.parent().completion_source().adic_completion(
            self.parent().completion_ideal(), precision=int(precision)
        )
        return refined.completion_map()(source_expression)


class _AdicCompletionAlgebraParent(_OwnedAlgebraParent):
    r"""An engine-backed adic completion with its defining data fixed at construction."""

    Element = _AdicCompletionElement

    def __init__(
        self,
        engine,
        source,
        defining_ideal,
        precision,
        *,
        engine_map=None,
        completed_ideal_generators=None,
        projection_lift=None,
        arithmetic_mode="finite_precision",
        completion_image=None,
        completion_map_kernel=None,
        algebra_base=None,
        algebra_labels=None,
        formal_parameter_labels=None,
        extra_categories=(),
    ) -> None:
        selected_engine_map = engine_map
        if completion_image is None:
            source_engine = _engine_ring(source)
            if selected_engine_map is None:
                selected_engine_map = engine.coerce_map_from(source_engine)

            def completion_image(element):
                source_value = _engine_element(source, source(element))
                value = (
                    selected_engine_map(source_value)
                    if selected_engine_map is not None
                    else engine(source_value)
                )
                return engine(value)

        def completion_map_factory():
            def completion_map_image(element):
                selected = source(element)
                return self._completion_element(
                    completion_image(selected),
                    source_expression=selected,
                )

            return _ring_morphism_with_engine(
                source, self, completion_map_image, selected_engine_map
            )

        self._adic_completion_source = source
        self._adic_completion_ideal = defining_ideal
        self._adic_completion_precision = int(precision)
        self._adic_projection_lift = projection_lift
        self._adic_arithmetic_mode = arithmetic_mode
        self._adic_completion_map_kernel = completion_map_kernel
        self._adic_completion_map_factory = completion_map_factory
        self._realized_completion_map = None
        match formal_parameter_labels:
            case None:
                self._preamble_formal_parameter_labels = None
            case _:
                self._preamble_formal_parameter_labels = finite_ordered_set(
                    formal_parameter_labels
                )
        placements = [AdicCompletions(), *extra_categories]
        ring_placements = []
        if source in OwnedRings().Commutative():
            ring_placements.append(OwnedRings().Commutative())
        if source in OwnedRings().Noetherian():
            placements.append(OwnedRings().Noetherian())
            ring_placements.append(OwnedRings().Noetherian())
        formal_base = algebra_base
        match formal_base:
            case None:
                formal_base_is_local = False
                formal_base_is_complete_local = False
            case _:
                formal_base = _own_ring(formal_base)
                formal_base_is_local = (
                    formal_parameter_labels is not None
                    and formal_base in OwnedRings().Commutative().Local()
                )
                formal_base_is_complete_local = (
                    formal_parameter_labels is not None
                    and formal_base in OwnedRings().Commutative().Local().Complete()
                )

        # A formal-power-series specialization knows the quotient by its
        # represented ideal of variables exactly. For an arbitrary adic
        # completion, maximality is the defining ideal owner's computation;
        # a failure of that selected computation is a failure, not a category
        # decision.
        if formal_parameter_labels is not None and formal_base is not None:
            defining_ideal_is_maximal = (
                True if formal_base in OwnedRings().Division().Commutative() else None
            )
        else:
            defining_ideal_is_maximal = defining_ideal.is_maximal()

        match (
            defining_ideal_is_maximal,
            formal_base_is_complete_local,
            formal_base_is_local,
        ):
            case (True, _, _) | (_, True, _):
                local_complete = OwnedRings().Commutative().Local().Complete()
                placements.append(local_complete)
                ring_placements.append(local_complete)
            case (_, _, True):
                local = OwnedRings().Commutative().Local()
                placements.append(local)
                ring_placements.append(local)
            case _:
                pass
        _OwnedAlgebraParent.__init__(
            self,
            engine,
            source if algebra_base is None else algebra_base,
            algebra_labels,
            categories=tuple(placements),
            ring_placement=lambda: tuple(ring_placements),
        )
        completion_map = self.completion_map()
        match (formal_base_is_local, defining_ideal_is_maximal):
            case (True, _):
                formal_parameters = tuple(
                    completion_map(
                        source.algebra_generator(label)
                    )
                    for label in self._preamble_formal_parameter_labels
                )
                residue = formal_base.residue_field()
                residue_map = OwnedRings().Mor(self, residue)(
                    lambda value: formal_base.residue_map()(
                        self(value).coefficient(0)
                    )
                )
                self._local_ring_construction = LocalRingConstruction(
                    maximal_ideal_factory=lambda: _maximal_ideal_over_local_base(
                        self, formal_base, formal_parameters
                    ),
                    residue_field=residue,
                    residue_map=residue_map,
                )
            case (_, True):
                maximal_ideal = completion_map.extension_of_ideal(defining_ideal)
                residue = source.residue_field_at(defining_ideal)

                def residue_map_factory():
                    projection = self.adic_projection(1)
                    if projection.codomain() is residue:
                        return projection
                    return _canonical_map(projection.codomain(), residue) * projection

                self._local_ring_construction = LocalRingConstruction(
                    maximal_ideal=maximal_ideal,
                    residue_field=residue,
                    residue_map_factory=residue_map_factory,
                )
            case _:
                pass

    def _selected_adic_defining_ideal(self):
        r"""Supply this completion's fixed target ideal to ``ideal_of_definition``."""
        return self.ideal_extension().extended_ideal()

    def _selected_algebra_structure_morphism(self):
        r"""Supply the retained completion map when it is the scalar structure map."""
        if self.algebra_base_ring() is self.completion_source():
            return self.completion_map()
        return None

    def completion_arithmetic_mode(self):
        return self._adic_arithmetic_mode

    def _completion_element(self, value, *, source_expression=None):
        if element_parent(value) is not self._engine:
            value = self._engine(value)
        return self.element_class(
            self,
            value,
            exact_source_expression=source_expression,
        )

    def _element_constructor_(self, value):
        value_parent = element_parent(value)
        if value_parent is self:
            return value
        completion_map = self._realized_completion_map
        if completion_map is None:
            return super()._element_constructor_(value)
        source = self.completion_source()
        if (
            value_parent is source
            or value_parent is source.base_ring()
            or value_parent is None
            or not isinstance(value, SageObject)
        ):
            return completion_map(source(value))
        return super()._element_constructor_(value)

    def zero(self):
        completion_map = self._realized_completion_map
        if completion_map is None:
            return super().zero()
        return completion_map(self.completion_source().zero())

    def one(self):
        completion_map = self._realized_completion_map
        if completion_map is None:
            return super().one()
        return completion_map(self.completion_source().one())


class GeneratedIdealView(SageObject):
    r"""An ideal remembered by its ambient ring and chosen generators."""

    def __init__(self, ring, generators, source_ideal=None) -> None:
        self._ring = ring
        self._generators = tuple(generators)
        self._source_ideal = source_ideal

    def ring(self):
        return self._ring

    def ideal_generators(self):
        return self._generators

    def source_ideal(self):
        return self._source_ideal

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if not isinstance(other, GeneratedIdealView) or other.ring() is not self.ring():
            return False
        if self.source_ideal() is not None and other.source_ideal() is not None:
            ring = self.ring()
            if ring in LocalizationRings():
                source = ring.localization_source()
                return bool(
                    _engine_ideal(source, self.source_ideal())
                    == _engine_ideal(source, other.source_ideal())
                )
            return bool(self.source_ideal() == other.source_ideal())
        return self.ideal_generators() == other.ideal_generators()

    def __ne__(self, other) -> bool:
        return not self == other

    def _repr_(self):
        return f"Ideal ({', '.join(map(str, self.ideal_generators()))}) of {self.ring()}"


def _maximal_ideal_over_local_base(algebra, base, uniformizers):
    r"""Return the maximal ideal ``m A + (t_1, ..., t_n)`` of a local-base construction.

    Let ``(R, m)`` be local and let ``A`` be ``R[[t_1, ..., t_n]]`` or
    ``R[e]/(e^2)``.  An element of ``A`` is a unit exactly when its constant
    term is a unit of ``R``, hence exactly when that constant term lies outside
    ``m``.  So the non-units of ``A`` are the elements whose constant term lies
    in ``m``, and that set is the ideal generated by the image of ``m``
    together with the new variables.  Either part alone understates it: over a
    field ``m`` is zero and only the variables remain, while over ``Z_(p)`` the
    scalar ``p`` is a non-unit of ``A`` as well.

    The residue field is unchanged by the extra generators, because
    ``A/(m A + (t)) = R/m``.

    Protected local-construction supplier under OWN-05--07. Its callers are
    the selected maximal-ideal factories of the formal-power-series and
    dual-number constructors. The input variables are actual target
    elements; a formal variable additionally retains its exact expression
    in the polynomial completion source. The result is an owned ideal
    subobject of this literal algebra, with its regular-module inclusion.
    The existing ideal and module owners supply the required source
    relations; unavailable computations remain their ordinary frontier.

    Completion uses the existing flat extension of the polynomial ideal
    when its source is Noetherian. A dual quotient uses the actual quotient
    source and its ordered relations, without treating the quotient map as
    flat. No generator is removed by forcing an undecided zero predicate.
    """
    if base in LocalizationRings() and base not in OwnedRings().Division().Commutative():
        assert base._has_selected_exact_coefficient_presentation(), (
            f"cannot construct the maximal ideal over {base}: its polynomial "
            "ideal computations need an exact coefficient presentation, not "
            "a larger localization computation model"
        )
    source = algebra.completion_source() if algebra in AdicCompletions() else algebra
    coefficient_map = source.algebra_structure_morphism()
    if coefficient_map.codomain() is not source:
        coefficient_map = coefficient_map.codomain().inclusion() * coefficient_map
    assert coefficient_map.domain() is base and coefficient_map.codomain() is source, (
        "a local-base ideal must use the retained map from that exact coefficient ring"
    )
    base_maximal = tuple(
        coefficient_map(generator)
        for generator in base.maximal_ideal().ideal_generators()
    )
    if algebra in AdicCompletions():
        variables = tuple(variable.exact_source_expression() for variable in uniformizers)
        assert all(variable is not None for variable in variables), (
            "the selected formal variables must retain their polynomial source expressions"
        )
        source_ideal = source.ideal(*base_maximal, *variables)
        return algebra.completion_map().extension_of_ideal(source_ideal)
    from sage_extensions.categories.rings.commutative_ideals import (
        _quotient_source_commutative_ideal,
    )

    return _quotient_source_commutative_ideal(
        algebra, (*base_maximal, *uniformizers)
    )


@cached_function
def _quotient_ring(source, defining_ideal):
    r"""Return the one ``R/I`` for this ring and this ideal.

    ``R/I`` is determined by ``R`` and ``I``, so it is interned on them.  The
    key is the ideal itself rather than a generating set, and ideals decide
    their own equality, so ``(2)`` and ``(2,4)`` reach the same quotient of the
    integers.

    A localization keeps its localization engine as a private realization of
    fractions, not as quotient-construction data. Its quotient is therefore
    represented by classes directly; equality is the owned membership
    ``a - b in I`` and is exact. This is essential for prime localizations,
    whose fraction-field realization would otherwise collapse every nonzero
    ideal to the unit ideal, and it gives every represented localization the
    same construction rule without probing backend quotient capabilities.
    A source with the OwnedRings self-realization contract likewise retains
    actual classes. This includes a further quotient of an engine-free
    quotient; neither its source nor its defining ideal is flattened away.
    """
    exact_source_quotient = (
        source in LocalizationRings() or _engine_ring(source) is source
    )
    if exact_source_quotient:
        quotient_engine = None
    else:
        engine = _engine_ring(source)
        defining = _engine_ideal(source, defining_ideal)
        match engine:
            case SageNumberFieldOrder():
                # Sage's generic QuotientRing order branch attempts to replace an
                # order ideal I by K.ideal(I), treating the ideal itself as a field
                # element.  The owned quotient already has the exact class model:
                # equality is membership modulo I.
                quotient_engine = None
            case QuotientRing_generic():
                lifted = _engine_quotient_cover_ideal(source, defining)
                quotient_engine = lifted.ring().quotient(lifted)
            case _ if engine in SageFields():
                # Sage names a field's quotient generator after the field's
                # generator, which for Qp(3) is the invalid "3bar"
                # (TRAPS.md); the quotient of a field is the field or zero,
                # so the private name is never read.
                quotient_engine = engine.quotient(defining, names=("quotient_generator",))
            case _:
                quotient_engine = engine.quotient(defining)

    # O/I is finite for an order O and a nonzero ideal I, placed by that
    # construction: O is a free ZZ-module of finite rank, so a nonzero ideal
    # has full rank and finite index (Mathlib
    # ``Ideal.finiteQuotientOfFreeOfNeBot``,
    # Mathlib/LinearAlgebra/FreeModule/IdealQuotient.lean).  ZZ is the order
    # of QQ: ZZ/(n) is ``ZMod n`` (``Int.quotientSpanNatEquivZMod``), finite
    # for n != 0 (``ZMod.fintype``, Mathlib/Data/ZMod/Defs.lean).  The
    # placement reads the source's construction and the ideal's generators,
    # never the class of a realization (ARC-08).
    # A nonzero ideal of a finite-rank order has finite index, so its quotient
    # is finite and Artinian. Read only the retained generators here: an
    # undecided equality to zero is not a premise for finite placement.
    finite_order_quotient = (
        not exact_source_quotient
        and source in OwnedOrders()
        and any(
            (generator == source.zero()) is False
            for generator in defining_ideal.ideal_generators()
        )
    )

    # A field/domain placement is inherited from the ideal's construction
    # category, never selected by asking its maximality/primality predicate.
    # Unplaced ideals leave the quotient's corresponding property to the
    # caller, as required by CON-07 and ARC-08.
    quotient_is_field = (
        not exact_source_quotient
        and Category.__contains__(CommutativeIdeals(source).Maximal(), defining_ideal)
    )
    quotient_is_domain = quotient_is_field or (
        not exact_source_quotient
        and Category.__contains__(CommutativeIdeals(source).PrimeAsIdeal(), defining_ideal)
    )
    # ZZ/(p) for a maximal (p) is the prime field F_p, one object for every
    # route (``GF(p)``, ``PrimeFields()(p)``, ``Zmod(p)``).  It has no proper
    # subfield: every ring map into ZZ/(p) is onto (Mathlib
    # ``ZMod.ringHom_surjective``, Mathlib/Data/ZMod/Basic.lean:1135, with
    # ``Int.quotientSpanNatEquivZMod``), so a subfield, containing the image
    # of ZZ, is all of it.  Sage's prime field ``GF(p)`` is selected as the
    # private realization of this quotient (CON-12).
    prime_field = (
        quotient_is_field
        and not exact_source_quotient
        and source is _owned_integers()
    )
    if prime_field:
        quotient_engine = _SageGF(abs(defining.gen()))
    # F_p[t]/(m) for a maximal (m) is the field F_q, q = p^(deg m): the
    # classes of 1, t, ..., t^(deg m - 1) are an F_p-basis (Mathlib
    # ``AdjoinRoot.powerBasis``, Mathlib/RingTheory/AdjoinRoot.lean), so it
    # has p^(deg m) elements.  This is the construction of ``GF(q, label)``.
    # Sage's finite field with modulus exactly m is selected as its private
    # realization (CON-12); the modulus is the caller's (OWN-22), so Sage
    # does not re-test irreducibility.
    finite_extension_field = (
        quotient_is_field
        and not exact_source_quotient
        and not prime_field
        and source.base_ring() in PrimeFields()
        and source.base_ring().characteristic() != 0
        and source in SymmetricAlgebras(source.base_ring())
        and source.algebra_generating_set().is_finite() is True
        and (source.algebra_generating_set().cardinality() == cardinal(1)) is True
    )
    if finite_extension_field:
        modulus = defining.gen()
        characteristic = int(_engine_ring(source.base_ring()).characteristic())
        quotient_engine = _SageGF(
            characteristic ** int(modulus.degree()),
            _engine_ring(source).variable_name(),
            modulus=modulus,
            check_irreducible=False,
        )
    from sage_extensions.categories.group.magmas import AdditiveGroups

    # The quotient has the quotient abelian-group structure of its source.
    # Record the inherited additive axiom on the concrete parent rather than
    # relying on the category join to materialize it transitively.
    placements = [AdditiveGroups().AdditiveCommutative()]
    if source in OwnedRings().Noetherian():
        placements.append(OwnedRings().Noetherian())
    if prime_field:
        placements.append(PrimeFields())
    if quotient_is_field:
        placements.append(OwnedRings().Division().Commutative())
    elif quotient_is_domain:
        # A prime ideal is proper, so this quotient is also nontrivial.
        placements.append(OwnedIntegralDomains())
    if source in FiniteSets() or finite_order_quotient or finite_extension_field:
        placements.append(FiniteSets())
    if finite_order_quotient or finite_extension_field:
        placements.append(OwnedRings().Artinian())

    quotient = _object_of(
        owned_category_join((
            QuotientRings(),
            Algebras(source).Associative().Unital().Commutative(),
            *placements,
        )),
        source=source,
        defining_ideal=defining_ideal,
        _engine_ring=quotient_engine,
    )

    # For p prime and k > 1, an integer class modulo p^k is a unit exactly
    # when it is not divisible by p.  Thus all nonunits lie in (p), making
    # (p) the unique maximal ideal; the quotient by it is Z/p.  The selected
    # integer generator is the construction datum; use its exact prime-power
    # factorization rather than testing any property of the quotient or its
    # engine realization.
    if source is _owned_integers() and not exact_source_quotient:
        integer_generators = tuple(defining_ideal.ideal_generators())
        if len(integer_generators) == 1:
            modulus = abs(int(integer_generators[0]))
            if modulus > 1:
                prime_power = SageZZ(modulus).is_prime_power(get_data=True)
                if prime_power and int(prime_power[1]) > 1:
                    prime, _exponent = prime_power
                    maximal_ideal = CommutativeIdeals(quotient).Maximal()(
                        quotient(_owned_integers()(prime))
                    )
                    residue_field = _owned_integers().quotient_ring(
                        _owned_integers().ideal(_owned_integers()(prime))
                    )
                    residue_map = quotient.Mor(residue_field)(
                        lambda element: residue_field(element.lift())
                    )
                    _install_local_ring_construction(
                        quotient, maximal_ideal, residue_field, residue_map
                    )
    return quotient


def _localization_descent(source, elements):
    r"""Return the ring under a tower of localizations and these elements there.

    ``a/s`` is a unit exactly when ``a`` is, ``s`` being one already, so
    inverting ``a/s`` over the tower is inverting the numerator over the ring
    at its bottom.  The descent stops at a localization that inverts a set with
    no chosen finite generating set, such as the complement of a prime.
    """
    while source in LocalizationRings() and source not in PrimeLocalizations():
        elements = tuple(
            source.localization_fraction_data(element)[0] for element in elements
        )
        source = source.localization_source()
    return source, elements


def _one_step_inverted_family(source, generators):
    r"""Return the ring and the family that invert in one step what this does.

    Localizing ``S^{-1}A`` at ``g = a/s`` inverts ``S`` together with ``a``:
    ``s`` is a unit already, so ``a/s`` is a unit exactly when ``a`` is.  Then
    ``(S^{-1}A)[1/g]`` and ``(S union {a})^{-1}A`` invert the same subset of
    ``A``, each factors uniquely through the other by the universal property,
    and the canonical isomorphism between them identifies the two.

    Sage localizes ``A`` at a family and refuses to localize ``A[1/x]`` at
    anything, so the one-step family over the bottom ring is the presentation
    a realization can hold.  The owned source and map are unaffected: they
    record the ring that was localized, not the ring underneath.

    The descent stops at a localization that inverts a set with no chosen
    finite generating set, such as the complement of a prime, which no family
    presents.

    The family of ``S^{-1}A`` comes first and the numerators of the new
    generators follow, so the family of a tower extends the family of the
    localization below it.  The inverse-variable realization of the tower
    therefore extends that of the ring below it variable by variable.
    """
    inverted = tuple(generators)
    while source in LocalizationRings() and source not in PrimeLocalizations():
        inverted = tuple(source.inverted_elements()) + tuple(
            source.localization_fraction_data(element)[0] for element in inverted
        )
        source = source.localization_source()
    return source, inverted


def _fraction_over_localized_bottom(ring, element, bottom):
    r"""Write an element of an iterated localization of ``bottom`` as one fraction over it.

    In ``T^{-1}(S^{-1}A)`` an element ``n/d`` with ``n = a/s`` and ``d = b/t``
    is ``(a t)/(s b)``, a fraction of ``A`` whose denominator lies in the
    submonoid generated by the one-step inverted family of
    :func:`_one_step_inverted_family`, so its image in the inverse-variable
    presentation is a unit.  The descent follows the same chain of
    localization sources.
    """
    if ring is bottom:
        return element, bottom.one()
    source = ring.localization_source()
    numerator, numerator_denominator = _fraction_over_localized_bottom(source, element.numerator(), bottom)
    denominator, denominator_denominator = _fraction_over_localized_bottom(source, element.denominator(), bottom)
    return numerator * denominator_denominator, numerator_denominator * denominator


def _submonoid_contains_zero_in_domain(source, submonoid):
    r"""Decide whether a represented multiplicative submonoid contains zero in a domain.

    Private localization-construction contract. Permitted callers are
    _localization_size_placements, _finite_generated_localization, the
    LocalizationRings._cardinality_decision computation, and
    LocalizedModules._fraction_equality_status after its domain and
    torsion-free hypotheses are established. The source is an actual integral
    domain, with distinct zero and one, and the submonoid is selected in that
    same source. The result is True,
    False, or an owned proposition; an undecided result supplies neither
    domain placement nor a negative equality answer.

    In an integral domain a finite product is zero exactly when one factor is
    zero.  Thus a submonoid given by generators contains zero exactly when one
    chosen generator is zero.  Predicate-defined submonoids use their selected
    membership predicate instead.
    """
    assert source in OwnedIntegralDomains(), (
        f"cannot decide whether 0 lies in {submonoid} by its generators: {source} is not "
        f"known to be an integral domain, and outside a domain a product of nonzero "
        f"elements can vanish"
    )
    match submonoid._selected_representation_kind():
        case "predicate":
            return submonoid.defining_predicate()(source.zero())
        case "generators":
            generators = tuple(submonoid.monoid_generators())
            return negation(conjunction(
                negation(generator == source.zero()) for generator in generators
            ))
        case representation:
            raise AssertionError(
                f"unknown selected submonoid representation {representation!r}"
            )


def _localization_size_placements(source, submonoid):
    r"""Return exact cardinality placements inherited by ``S^-1 R``.

    A localization of a finite ring is finite.  For an infinite domain with
    ``0 not in S``, the canonical map is injective, while every fraction is a
    pair from ``R x S``; hence the localization has exactly the cardinality of
    ``R``.
    """
    if source in FiniteSets():
        return (FiniteSets(),)
    if source not in OwnedIntegralDomains():
        return ()
    contains_zero = _submonoid_contains_zero_in_domain(source, submonoid)
    if contains_zero is not False:
        return ()
    if source in CountablyInfiniteSets():
        return (CountablyInfiniteSets(),)
    if source in UncountableSets():
        return (UncountableSets(),)
    return ()


def _flattened_symmetric_localization_engine(source, inverted):
    r"""Realize a localization of ``Sym_C(M)`` when ``C`` is itself localized.

    For a finitely generated localization ``C = S^{-1}A`` and a finite
    polynomial algebra ``C[x_1,...,x_n]``, localizing at finitely many
    polynomials is canonically the corresponding localization of
    ``A[x_1,...,x_n]`` after adjoining the already inverted elements of ``S``.
    Sage's nested polynomial localization currently misidentifies such
    polynomials as units; its flattened multivariate polynomial ring has the
    maintained localization implementation and represents the same ring.

    The returned decoder is private representation correspondence from a
    numerator/denominator in that flattened engine back to the owned source
    polynomial algebra.  Public localization data remain ``source`` and its
    selected submonoid.
    """

    coefficient_ring = source.base_ring()
    if (
        source not in SymmetricAlgebras(coefficient_ring)
        or coefficient_ring not in LocalizationRings()
        or coefficient_ring in PrimeLocalizations()
    ):
        return None, None, None
    if (
        coefficient_ring.localization_submonoid()._structure_data().get("kind")
        != "finitely_generated"
    ):
        return None, None, None
    coefficient_inverted = tuple(coefficient_ring.inverted_elements())
    coefficient_bottom, coefficient_family = _one_step_inverted_family(
        coefficient_ring,
        coefficient_inverted,
    )
    source_engine = _engine_ring(source)
    coefficient_engine = _engine_ring(coefficient_ring)
    coefficient_bottom_engine = _engine_ring(coefficient_bottom)
    names = tuple(source_engine.variable_names())
    # In one variable Sage's own localization of C[x] decides units, while
    # the flattened A[x] inverting a constant raises on every nonconstant
    # element (TRAPS.md); only several variables take the flattened route.
    if len(names) == 1:
        return None, None, None
    polynomial_bottom = _SagePolynomialRing(
        coefficient_bottom_engine,
        names=names,
    )

    flattening = polynomial_bottom.flattening_morphism()
    engine_bottom = flattening.codomain()
    unflatten = flattening.section()
    to_engine_bottom = flattening

    variables = tuple(polynomial_bottom.gens())

    def powers_of(exponent):
        if len(variables) == 1:
            return (int(exponent),)
        return tuple(int(power) for power in exponent)

    def cleared_polynomial(element):
        represented = source_engine(_engine_element(source, element))
        coefficients = represented.dict()
        common_denominator = coefficient_bottom_engine.one()
        for coefficient in coefficients.values():
            common_denominator *= coefficient_bottom_engine(
                coefficient.denominator()
            )
        cleared = source_engine(coefficient_engine(common_denominator)) * represented
        result = polynomial_bottom.zero()
        for exponent, coefficient in cleared.dict().items():
            if coefficient.denominator() != coefficient_bottom_engine.one():
                raise ArithmeticError(
                    f"cannot clear the denominators of {element}: after multiplying by {common_denominator}, "
                    f"the coefficient {coefficient} still has a denominator"
                )
            term = polynomial_bottom(
                coefficient_bottom_engine(coefficient.numerator())
            )
            for variable, power in zip(variables, powers_of(exponent), strict=True):
                if power:
                    term *= variable**power
            result += term
        return to_engine_bottom(result)

    engine_inverted = [
        to_engine_bottom(
            polynomial_bottom(_engine_element(coefficient_bottom, element))
        )
        for element in coefficient_family
    ]
    engine_inverted.extend(cleared_polynomial(element) for element in inverted)
    localization_engine = engine_bottom.localization(tuple(engine_inverted))

    def decode(element):
        nested = unflatten(engine_bottom(element))
        return _owned_engine_element(source, source_engine(nested))

    def encode(element):
        represented = source_engine(_engine_element(source, source(element)))
        result = localization_engine.zero()
        for exponent, coefficient in represented.dict().items():
            represented_coefficient = coefficient_engine(coefficient)
            numerator = coefficient_bottom_engine(
                represented_coefficient.numerator()
            )
            denominator = coefficient_bottom_engine(
                represented_coefficient.denominator()
            )
            numerator_term = localization_engine(
                to_engine_bottom(polynomial_bottom(numerator))
            )
            denominator_term = localization_engine(
                to_engine_bottom(polynomial_bottom(denominator))
            )
            term = numerator_term / denominator_term
            for variable, power in zip(
                variables, powers_of(exponent), strict=True
            ):
                if power:
                    term *= localization_engine(
                        to_engine_bottom(variable)
                    ) ** int(power)
            result += term
        return result

    return localization_engine, decode, encode


def _finite_generated_localization(source, submonoid):
    generators = tuple(submonoid.monoid_generators())
    if not generators:
        return source
    bottom, inverted = _one_step_inverted_family(source, generators)
    values = tuple(_engine_element(bottom, value) for value in inverted)
    engine_bottom = _engine_ring(bottom)
    engine_source_decoder = None
    engine_source_encoder = None
    if all(value.is_unit() for value in values):
        localization_engine = engine_bottom
    elif isinstance(engine_bottom, QuotientRing_generic):
        # Protected OWN-06 dispatch: a Sage generic quotient parent requires
        # the standard auxiliary-variable localization presentation.
        cover = engine_bottom.cover_ring()
        defining = engine_bottom.defining_ideal()
        cover_names = tuple(cover.variable_names())
        occupied = set(cover_names)
        inverse_names = []
        for position in range(len(values)):
            candidate = f"localization_inverse_{position}"
            while candidate in occupied:
                candidate = "localization_" + candidate
            occupied.add(candidate)
            inverse_names.append(candidate)
        extended_cover = _SagePolynomialRing(
            cover.base_ring(),
            names=(*cover_names, *inverse_names),
        )
        inverse_variables = tuple(
            extended_cover.gen(len(cover_names) + position)
            for position in range(len(values))
        )
        relations = tuple(
            extended_cover(generator) for generator in defining.gens()
        ) + tuple(
            inverse * extended_cover(value.lift()) - extended_cover.one()
            for inverse, value in zip(inverse_variables, values, strict=True)
        )
        localization_engine = extended_cover.quotient(
            extended_cover.ideal(relations)
        )

        def engine_source_encoder(element):
            numerator, denominator = _fraction_over_localized_bottom(source, element, bottom)
            return localization_engine(
                extended_cover(_engine_element(bottom, numerator).lift())
            ) / localization_engine(
                extended_cover(_engine_element(bottom, denominator).lift())
            )
    elif (
        bottom is source
        and hasattr(engine_bottom, "variable_names")
        and engine_bottom.base_ring().is_integral_domain() is False
    ):
        # An arbitrary commutative coefficient ring admits localization,
        # although Sage's PolynomialRing.localization demands a domain.
        # The inverse-variable presentation represents the universal ring
        # without imposing a false no-zero-divisors hypothesis.
        source_names = tuple(engine_bottom.variable_names())
        occupied = set(source_names)
        inverse_names = []
        for i in range(len(values)):
            candidate = f"localization_inverse_{i}"
            while candidate in occupied:
                candidate += "_"
            occupied.add(candidate)
            inverse_names.append(candidate)
        extended = _SagePolynomialRing(
            engine_bottom.base_ring(), names=(*source_names, *inverse_names)
        )
        relations = tuple(
            extended.gen(len(source_names) + i) * extended(value) - extended.one()
            for i, value in enumerate(values)
        )
        localization_engine = extended.quotient(extended.ideal(relations))
        engine_source_encoder = lambda element: localization_engine(
            extended(_engine_element(source, element))
        )
    else:
        (
            localization_engine,
            engine_source_decoder,
            engine_source_encoder,
        ) = _flattened_symmetric_localization_engine(bottom, inverted)
        if localization_engine is None:
            localization_engine = engine_bottom.localization(values)
    from sage_extensions.categories.group.magmas import AdditiveGroups

    # Localization inherits the source ring's abelian addition, including
    # the zero localization.  Owned joins do not guarantee that this inherited
    # facet is materialized on the concrete parent; module construction and
    # the fraction-field path require the actual additive-group placement.
    placements = [
        *_localization_size_placements(source, submonoid),
        AdditiveGroups().AdditiveCommutative(),
    ]
    if source in OwnedRings().Noetherian():
        placements.append(OwnedRings().Noetherian())
    if source in OwnedRings().Commutative().NoZeroDivisors():
        # The zero-product property survives even the zero localization.
        placements.append(OwnedRings().Commutative().NoZeroDivisors())
    # Localization preserves a domain (and a PID) only when zero is not
    # inverted. Noetherianity also holds for the zero localization. An
    # undecided zero-membership predicate supplies no nontriviality edge.
    if (
        source in OwnedIntegralDomains()
        and _submonoid_contains_zero_in_domain(source, submonoid) is False
    ):
        if source in OwnedPrincipalIdealDomains():
            placements.append(OwnedPrincipalIdealDomains())
        else:
            placements.append(OwnedIntegralDomains())
    base = source.base_ring()
    algebra_source = (
        source
        if base is not None and source in Algebras(base).Associative().Unital()
        else None
    )
    algebra_categories = []
    if algebra_source is not None:
        algebra_base = algebra_source.base_ring()
        algebra_categories = [Algebras(algebra_base).Associative().Unital()]
        if algebra_source in Algebras(algebra_base).Associative().Unital().Commutative():
            algebra_categories.append(Algebras(algebra_base).Associative().Unital().Commutative())
    full_placement = owned_category_join(
        (LocalizationRings(), *placements, *algebra_categories)
    )
    initial_placement = (
        owned_category_join((LocalizationRings(), *placements))
        if algebra_source is not None
        else full_placement
    )
    return _object_of(
        initial_placement,
        source=source,
        submonoid=submonoid,
        _engine_ring=localization_engine,
        _engine_source_decoder=engine_source_decoder,
        _engine_source_encoder=engine_source_encoder,
        algebra_source=algebra_source,
        _preamble_pending_localization_placement=(
            full_placement if initial_placement is not full_placement else None
        ),
    )


@cached_function
def _nonzero_element_submonoid(source):
    r"""Construct the predicate submonoid of nonzero elements of ``source``.

    Protected constructor under OWN-05. Its caller is the ring owner's
    ``nonzero_multiplicative_submonoid`` method. The source is an owned
    nontrivial ring without zero divisors: these hypotheses supply the
    identity and multiplication-closure premises of ``predicate_submonoid``.
    The result retains this literal source, its nonzero predicate, its
    monoid inclusion, and the existing ``nonzero_elements`` construction
    tag. No commutativity, fraction construction, or restriction of an
    arbitrary ring map is asserted.
    """
    if source not in OwnedRings().NoZeroDivisors().Nontrivial():
        raise TypeError(
            f"the nonzero multiplicative submonoid requires a nontrivial ring without "
            f"zero divisors, but {source} is not placed in that category"
        )
    return source.predicate_submonoid(
        lambda element: negation(element == source.zero()),
        f"Nonzero multiplicative elements of {source}",
        structure_data={"kind": "nonzero_elements"},
    )


def _fraction_field_localization(source, submonoid):
    r"""``(R-{0})^-1 R``, the fraction field of the domain ``R``, retaining its localization datum.

    The localization is itself the field; Sage's fraction field of the
    source's realization is selected privately as its realization (``CON-12``).
    """
    if source not in OwnedIntegralDomains():
        raise ValueError(
            f"the fraction field (R - {{0}})^-1 R needs R an integral domain, but {source} is not known to be one"
        )
    if submonoid._structure_data().get("kind") != "nonzero_elements":
        raise ValueError(
            f"the fraction field of {source} is the localization at R - {{0}}, but {submonoid} is a different "
            "multiplicative set"
        )
    if source in OwnedRings().Division().Commutative():
        return source

    engine = _engine_ring(source)
    assert engine is not source, (
        f"cannot construct the fraction field of {source}: it has no computer-algebra model"
    )
    match engine:
        case QuotientRing_generic():
            # Sage's IntegralDomains.ParentMethods.fraction_field is precisely
            # FractionField_generic(self).  A represented quotient carries the
            # domain theorem in its owned construction, while its private Sage
            # realization remains in Sage's quotient-ring category.  Use that
            # maintained constructor directly instead of mutating the
            # realization merely to make the category method appear.  An owned
            # quotient whose engine is not a generic quotient (ZZ/(0) is
            # realized by ZZ itself) asks its engine, which knows its field.
            fraction_engine = SageFractionField(engine)
        case _:
            fraction_engine = engine.fraction_field()
    from sage_extensions.categories.group.magmas import AdditiveGroups

    placements = [
        OwnedIntegralDomains(),
        OwnedRings().Division().Commutative(),
        AdditiveGroups().AdditiveCommutative(),
    ]
    if source in OwnedRings().Noetherian():
        placements.append(OwnedRings().Noetherian())
    # An ordered integral domain has a unique order extension to its fraction
    # field. Newer Sage versions expose that contract as OrderedFields. Older
    # supported Sage images lack the category module, so retain the order only
    # for QQ or an unchanged field engine there; do not infer an order for an
    # arbitrary rational-function or other field merely from field membership.
    realizes_ordered_field = (
        fraction_engine is SageQQ
        or fraction_engine is engine
        or (
            SageOrderedFields is not None
            and fraction_engine in SageOrderedFields()
        )
    )
    if (
        source in OwnedOrderedRings()
        and fraction_engine in SageFields()
        and realizes_ordered_field
    ):
        placements.append(OwnedOrderedRings())
    base = source.base_ring()
    algebra_source = (
        source
        if base is not None and source in Algebras(base).Associative().Unital()
        else None
    )
    algebra_categories = []
    if algebra_source is not None:
        algebra_base = algebra_source.base_ring()
        algebra_categories = [Algebras(algebra_base).Associative().Unital()]
        if algebra_source in Algebras(algebra_base).Associative().Unital().Commutative():
            algebra_categories.append(
                Algebras(algebra_base).Associative().Unital().Commutative()
            )
    full_placement = owned_category_join(
        (LocalizationRings(), *placements, *algebra_categories)
    )
    initial_placement = (
        owned_category_join((LocalizationRings(), *placements))
        if algebra_source is not None
        else full_placement
    )
    return _object_of(
        initial_placement,
        source=source,
        submonoid=submonoid,
        _engine_ring=fraction_engine,
        algebra_source=algebra_source,
        _preamble_pending_localization_placement=(
            full_placement if initial_placement is not full_placement else None
        ),
    )


def _localization(source, *datum):
    r"""Return ``S^{-1}R`` from a submonoid ``S -> (R,*)``.

    Passing ring elements is convenience syntax for the submonoid they generate.
    The mathematical localization datum stored on the result is always the
    represented subobject ``S -> (R,*)``.
    """
    if len(datum) == 1 and datum[0] in Monoids().Subobjects(source):
        return _localization_at_submonoid(source, datum[0])
    return _localization_at_elements(
        source,
        tuple(source(element) for element in datum),
    )


@cached_function
def _localization_at_elements(source, elements):
    r"""Return the one ``S^{-1}R`` for the submonoid these elements generate.

    The interning is keyed here rather than on the submonoid, because the
    submonoid is built from the elements and is a fresh subobject on every
    call.  So the key is the chosen generating family, and two families that
    generate one submonoid stay two objects: ``<2>`` and ``<2,4>`` are the same
    submonoid of ``(Z,*)`` and give the same ring, but deciding that two
    finitely generated submonoids of a commutative monoid coincide is not
    something the preamble can do, and it is not claimed here.
    """
    return _localization_at_submonoid(
        source,
        source.generated_submonoid(
            elements,
            description=f"Submonoid generated by {elements!r} in {source}",
            structure_data={"kind": "finitely_generated"},
        ),
    )


@cached_function
def _localization_at_submonoid(source, submonoid):
    r"""Return the one ``S^{-1}R`` for this ring and this represented submonoid."""
    structure = submonoid._structure_data()
    if structure.get("kind") == "prime_complement":
        localization = _PrimeLocalizationFromSubmonoid(source, submonoid)
    elif structure.get("kind") == "nonzero_elements":
        localization = _fraction_field_localization(source, submonoid)
    else:
        localization = _finite_generated_localization(source, submonoid)
    # All represented localizations are unital rings over their retained
    # source. Their object constructor is _object_of rather than
    # _OwnedRingParent, so make the regular module explicit at this common
    # construction boundary. The fraction-field specialization has already
    # done this and is idempotently recognized here.
    from sage_extensions.categories.algebras.algebras import (
        _algebra_from_native_ring,
    )
    from sage_extensions.categories.modules.pure.modules import Modules

    if Modules.ParentMethods._native_module_presentation(localization) is None:
        algebra_source = getattr(localization, "algebra_source", None)

        def scalar_action(scalar, element):
            if algebra_source is None:
                scalar_image = localization(scalar)
            else:
                # Preserve the source algebra's selected structure map
                # k -> A, then apply the canonical localization map A -> S^-1 A.
                # Coercing k directly into the localization can choose a
                # different ambient coercion path and loses the exact retained
                # scalar structure when A was constructed over a nontrivial map.
                # A unital algebra's structure map is recovered from its
                # retained scalar action on 1. Do not use parent coercion as
                # a substitute: coercion can follow a different ambient route
                # from the selected k-algebra structure.
                source_scalar = algebra_source._owned_scalar_multiple(
                    scalar, algebra_source.one()
                )
                scalar_image = localization.localization_map()(source_scalar)
            return scalar_image * localization(element)

        _algebra_from_native_ring(
            localization,
            lambda left, right: localization(left * right),
            localization.one(),
            scalar_action,
            scalar_ring=(
                algebra_source.base_ring()
                if algebra_source is not None
                else localization.base_ring()
            ),
        )
    pending_placement = vars(localization).pop(
        "_preamble_pending_localization_placement", None
    )
    if pending_placement is not None:
        from sage_extensions.refine import refine

        refine(localization, pending_placement)
    return localization


def _quotient_representative(element):
    assert element.parent() in QuotientRings(), (
        "a represented quotient element used in quotient/localization comparison must carry its canonical lift"
    )
    return element.lift()


def _localization_element_from_source_fraction(localization_ring, numerator, denominator):
    assert localization_ring in LocalizationRings(), (
        "source-fraction reconstruction requires a represented localization"
    )
    return localization_ring.fraction(numerator, denominator)


def _quotient_localization_comparison(source_quotient, localization_ring):
    r"""Return the canonical isomorphism

    ``S^{-1}(R/I) -> S^{-1}R/S^{-1}I``.

    Localizing ``R/I`` means inverting the image of ``S``.  Where ``S`` is
    given by a chosen finite generating set that image is the submonoid the
    images of those generators generate.  Where ``S`` is the complement of a
    prime ``p`` containing ``I``, the image is the complement of the prime
    ``p/I``, so the left side is the prime localization ``(R/I)_{p/I}`` and the
    comparison is the local ring of a point of the closed subscheme ``V(I)``
    read either way round.
    """
    if source_quotient not in QuotientRings():
        raise TypeError(
            f"the comparison (R/I)_S = R_S / I R_S needs a quotient ring R/I, but {source_quotient} is not one"
        )
    source_ring = source_quotient.quotient_source()
    if localization_ring not in LocalizationRings():
        raise TypeError(
            f"the comparison (R/I)_S = R_S / I R_S needs a localization of R = {source_ring}, but "
            f"{localization_ring} is not a localization"
        )
    if localization_ring.localization_source() is not source_ring:
        raise ValueError(
            f"the comparison (R/I)_S = R_S / I R_S needs a localization of R = {source_ring}, but "
            f"{localization_ring} is a localization of {localization_ring.localization_source()}"
        )

    source_submonoid = localization_ring.localization_submonoid()
    quotient_map = source_quotient.quotient_map()
    defining_ideal = source_quotient.defining_ideal()

    if localization_ring in PrimeLocalizations():
        prime = localization_ring.localized_prime()
        assert all(
            prime.contains_ambient_element(generator)
            for generator in defining_ideal.ideal_generators()
        ), (
            f"the image of the complement of {prime} in {source_quotient} is the complement "
            f"of a prime only when {defining_ideal} lies inside {prime}; otherwise that "
            "image contains zero and both sides of the comparison are the zero ring, which "
            "is not constructed here"
        )
        localized_quotient = source_quotient.localize_at_prime(
            quotient_map.extension_of_ideal(prime)
        )
    else:
        assert source_submonoid._selected_representation_kind() == "generators", (
            "the quotient/localization comparison reads the image of S from a chosen "
            "finite generating set, or from the prime whose complement S is"
        )
        source_generators = tuple(source_submonoid.monoid_generators())

        quotient_submonoid = source_quotient.generated_submonoid(
            tuple(quotient_map(generator) for generator in source_generators),
            description=f"Image of {source_submonoid} in {source_quotient}",
            structure_data={"kind": "quotient_image"},
        )
        localized_quotient = source_quotient.localization(quotient_submonoid)

    extended_ideal = defining_ideal.extension_to_localization(localization_ring)
    quotient_after_localization = localization_ring.quotient_ring(extended_ideal)

    right_quotient_map = quotient_after_localization.quotient_map()

    def forward_image(element):
        numerator, denominator = localized_quotient.localization_fraction_data(element)
        numerator_lift = source_ring(_quotient_representative(numerator))
        denominator_lift = source_ring(_quotient_representative(denominator))
        localized = _localization_element_from_source_fraction(
            localization_ring,
            numerator_lift,
            denominator_lift,
        )
        return right_quotient_map(localized)


    forward = localized_quotient.Mor(quotient_after_localization)(
        forward_image,
    )

    def inverse_image(element):
        representative = _quotient_representative(element)
        numerator, denominator = localization_ring.localization_fraction_data(representative)
        return localized_quotient.fraction(
            quotient_map(numerator),
            quotient_map(denominator),
        )

    inverse = quotient_after_localization.Mor(localized_quotient)(
        inverse_image,
    )
    return QuotientLocalizationComparison(
        source_quotient,
        localization_ring,
        localized_quotient,
        quotient_after_localization,
        forward,
        inverse,
        extended_ideal,
    )


def _quotient_completion_comparison(source_quotient, source_ideal, *, precision=20):
    r"""Return the canonical Noetherian comparison ``(R/J)^ ~= R^/J R^``.

    The topology on ``R/J`` is defined by the image of ``source_ideal``.  The
    two arrows are assembled from the quotient and completion maps.  Their
    mathematical existence is the finite-module completion theorem over a
    Noetherian ring; evaluation away from exact retained source expressions
    stays at the ordinary completion computational frontier.
    """
    if source_quotient not in QuotientRings():
        raise TypeError(
            f"the comparison (R/I)^ = R^ / I R^ needs a quotient ring R/I, but {source_quotient} is not one"
        )
    source = source_quotient.quotient_source()
    if source not in OwnedRings().Noetherian():
        raise TypeError(
            f"the comparison (R/I)^ = R^ / I R^ needs R Noetherian, but {source} is not known to be Noetherian"
        )
    source_ideal = _owned_ideal(source, source_ideal)
    quotient_map = source_quotient.quotient_map()
    quotient_ideal = quotient_map.extension_of_ideal(source_ideal)

    source_completion = source.adic_completion(source_ideal, precision=precision)
    completed_quotient = source_quotient.adic_completion(
        quotient_ideal,
        precision=precision,
    )
    extended_defining_ideal = source_completion.completion_map().extension_of_ideal(
        source_quotient.defining_ideal()
    )
    quotient_after_completion = source_completion.quotient_ring(
        extended_defining_ideal
    )
    right_quotient_map = quotient_after_completion.quotient_map()

    def quotient_source_to_right(element):
        representative = _quotient_representative(source_quotient(element))
        return right_quotient_map(
            source_completion.completion_map()(representative)
        )

    source_to_right = source_quotient.Mor(quotient_after_completion)(
        quotient_source_to_right,
    )

    def forward_image(element):
        selected = completed_quotient(element)
        source_expression = selected.exact_source_expression()
        if source_expression is None:
            raise AssertionError(
                f"cannot evaluate the comparison map at {element}: it is not known as the image of an element "
                f"of {source}"
            )
        return source_to_right(source_expression)

    forward = completed_quotient.Mor(quotient_after_completion)(
        forward_image,
    )

    completion_to_completed_quotient = source_completion.induced_map(
        quotient_map,
        completed_quotient,
    )
    for generator in extended_defining_ideal.ideal_generators():
        if completion_to_completed_quotient(generator) != completed_quotient.zero():
            raise ArithmeticError(
                f"the map from the completion to the completed quotient {completed_quotient} does not kill "
                f"{generator}, a generator of the extended defining ideal {extended_defining_ideal}"
            )

    def inverse_image(element):
        representative = _quotient_representative(
            quotient_after_completion(element)
        )
        return completion_to_completed_quotient(representative)

    inverse = quotient_after_completion.Mor(completed_quotient)(
        inverse_image,
    )
    return QuotientCompletionComparison(
        source_quotient,
        source_ideal,
        source_completion,
        completed_quotient,
        quotient_after_completion,
        extended_defining_ideal,
        forward,
        inverse,
    )


def _residue_field_at(source, ideal):
    r"""Return ``R/m`` for a represented maximal ideal ``m`` of ``R``."""
    defining = _owned_ideal(source, ideal)
    maximal = defining.is_maximal()
    if maximal is False:
        raise ValueError(
            f"the residue field R/m needs a maximal ideal m, but {defining} is not maximal in {source}"
        )
    assert maximal is True, (
        f"the residue field R/m requires maximality of {defining} in {source}, "
        "but that proposition is undecided"
    )
    quotient = source.quotient_ring(defining)
    if quotient not in OwnedRings().Division().Commutative():
        raise ArithmeticError(
            f"the quotient {quotient} of {source} by the maximal ideal {defining} was not constructed as a field"
        )
    return quotient


def _PrimeLocalizationFromSubmonoid(source, submonoid):
    r"""Return ``R_p`` for a submonoid represented as the complement of ``p``.

    When R is a domain, ``R -> R_p`` is injective and the localization embeds
    in ``Frac(R)``; that field supplies its computation model below. Otherwise
    this constructor selects no source fraction-field model. This makes no
    claim that ``R_p`` has zero divisors: localization can remove a component.
    The owned fractions and ideal computations in R against p remain the
    actual localization in either case.
    """
    structure = submonoid._structure_data()
    prime_ideal = structure.get("prime_ideal")
    if prime_ideal is None:
        raise ValueError(
            f"the localization R_p needs the prime ideal p whose complement is {submonoid}, but it is missing"
        )
    from sage_extensions.categories.group.magmas import AdditiveGroups

    # Prime localization is still a localization of the source ring, so its
    # addition is abelian.  It has a separate owner from finite-generated
    # localization because its inverted set has no selected finite family.
    placements = [
        *_localization_size_placements(source, submonoid),
        AdditiveGroups().AdditiveCommutative(),
    ]
    if source in OwnedRings().Commutative().NoZeroDivisors().PrincipalIdeals():
        placements.append(OwnedRings().Commutative().NoZeroDivisors().PrincipalIdeals())
    else:
        if source in OwnedRings().Noetherian():
            placements.append(OwnedRings().Noetherian())
        if source in OwnedRings().Commutative().NoZeroDivisors():
            placements.append(OwnedRings().Commutative().NoZeroDivisors())
    if source in OwnedIntegralDomains():
        fraction_engine = _engine_ring(source.fraction_field())
    else:
        fraction_engine = None
    base = source.base_ring()
    algebra_source = (
        source
        if base is not None and source in Algebras(base).Associative().Unital()
        else None
    )
    algebra_categories = []
    if algebra_source is not None:
        algebra_categories.append(Algebras(base).Associative().Unital())
        if source in Algebras(base).Associative().Unital().Commutative():
            algebra_categories.append(Algebras(base).Associative().Unital().Commutative())
    full_placement = owned_category_join(
        (PrimeLocalizations(), *placements, *algebra_categories)
    )
    initial_placement = (
        owned_category_join((PrimeLocalizations(), *placements))
        if algebra_source is not None
        else full_placement
    )
    return _object_of(
        initial_placement,
        source=source,
        submonoid=submonoid,
        engine_ring=fraction_engine,
        algebra_source=algebra_source,
        _preamble_pending_localization_placement=(
            full_placement if initial_placement is not full_placement else None
        ),
    )


def _prime_localization_from_input(source, prime):
    r"""Return ``R_p`` using the submonoid ``R \ p -> (R,*)``."""
    if source not in OwnedRings().Commutative():
        raise TypeError(
            f"the localization R_p needs a commutative ring R, but {source} is in {source.category()}"
        )
    prime_ideal = _owned_ideal(source, prime)
    primality = prime_ideal.is_prime()
    if primality is False:
        raise ValueError(
            f"the localization R_p needs a prime ideal p, but {prime_ideal} is not prime in {source}"
        )
    assert primality is True, (
        f"the localization R_p requires primality of {prime_ideal} in {source}, "
        "but that proposition is undecided"
    )
    return _prime_localization(source, prime_ideal)


@cached_function(key=lambda source, prime_ideal: (id(source), id(prime_ideal)))
def _prime_localization(source, prime_ideal):
    r"""Return ``R_p`` retaining this exact source and selected prime ideal.

    The complement of a prime is a predicate submonoid, freshly built on each
    call and never recognizable as a copy of itself. Interning therefore
    uses the identities of the source and prime-ideal datum, without deciding
    equality of arbitrary ideals. Distinct equal ideal presentations need
    not produce the same parent. The common ring's
    ``localize_at_prime`` entry establishes primality before this protected
    constructor is called. The resulting predicate uses membership in that
    exact owned ideal, including its retained quotient or localization data;
    a larger fraction-field computation model does not determine the subset.
    Undecided membership remains a proposition. Primality supplies the unit
    and multiplication-closure premises of the predicate submonoid.
    """
    complement = source.predicate_submonoid(
        lambda element: negation(prime_ideal.contains_ambient_element(source(element))),
        f"{source} \\ {prime_ideal}",
        structure_data={"kind": "prime_complement", "prime_ideal": prime_ideal},
    )
    return _localization_at_submonoid(source, complement)


@cached_function
def _adic_completion_from_owned_data(source, defining, precision):
    r"""Private implementation of the represented adic completion ``R^``.

    ``source`` and ``defining`` are already owned and normalized by
    :class:`AdicCompletions`.  This is the sole implementation factory for the
    family; public notation is defined below and delegates back to the category
    constructor.
    """
    if source in PrimeLocalizations() and (defining == source.maximal_ideal()) is True:
        bottom = source.localization_source()
        prime = source.localized_prime()
        assert prime.is_maximal() is True, (
            f"reusing the completion of {bottom} at {prime} to complete {source} requires every element "
            f"outside {prime} to become a unit in that completion; this selected construction requires "
            "the prime to be proved maximal in the original source"
        )
        bottom_completion = AdicCompletions()(
            bottom,
            prime,
            precision=precision,
        )
        local_to_completion = source._induced_morphism_from_unit_images(
            bottom_completion.completion_map()
        )
        completion_engine = _engine_ring(bottom_completion)
        bottom_projection_lift = bottom_completion._completion_projection_lift()
        assert bottom_projection_lift is not None, (
            f"cannot complete {source} at {defining}: the completion {bottom_completion} of "
            f"{bottom} has no way to reduce its elements modulo powers of {prime}"
        )

        def completion_image(element):
            return _engine_element(
                bottom_completion,
                local_to_completion(source(element)),
            )

        def projection_lift(value, exponent):
            return source.localization_map()(
                bottom_projection_lift(value, exponent)
            )

        completed_ideal_generators = tuple(
            completion_image(generator)
            for generator in defining.ideal_generators()
        )
        return _AdicCompletionAlgebraParent(
            completion_engine,
            source,
            defining,
            precision,
            completed_ideal_generators=completed_ideal_generators,
            projection_lift=projection_lift,
            arithmetic_mode=bottom_completion.completion_arithmetic_mode(),
            completion_image=completion_image,
            completion_map_kernel=(
                source.ideal(source.zero()) if source in OwnedRings().Noetherian() else None
            ),
            # The selected maximal ideal is proper, so the completion has
            # a nonzero residue quotient.
            extra_categories=(OwnedRings().Nontrivial(),),
        )
    defining_engine = _engine_ideal(source, defining)
    generators = tuple(defining_engine.gens())
    engine = _engine_ring(source)
    zero_ideal = source.ideal(source.zero())
    unit_ideal = source.ideal(source.one())
    defining_is_unit = defining == unit_ideal
    degenerate_formal_data = {}
    base = source.base_ring()
    if source in SymmetricAlgebras(base) and source.is_framed_algebra() is True:
        from sage_extensions.categories.sets.finite_ordered_sets import FiniteOrderedSets

        labels = source.algebra_generating_set()
        if labels in FiniteOrderedSets() and (
            (source.one() == source.zero()) is True
            or (
                (labels.cardinality() == cardinal(0)) is True
                and (defining == zero_ideal) is True
            )
        ):
            # Zero coefficients and an empty variable family may be realized
            # by scalar engines. Their fixed formal variables and coefficient
            # ring remain the data of the same formal-series construction.
            degenerate_formal_data = {
                "algebra_base": base,
                "formal_parameter_labels": tuple(labels),
                "extra_categories": (FormalPowerSeriesRings(base),),
            }
    if defining_is_unit is True:
        zero_quotient = source.quotient_ring(unit_ideal)
        zero_engine = _engine_ring(zero_quotient)
        assert zero_engine is not zero_quotient, (
            f"cannot construct the completion of {source} at the unit ideal, which is the zero ring: "
            f"{zero_quotient} has no computer-algebra model"
        )

        def completion_image(_element):
            return zero_engine.zero()

        def projection_lift(_value, _exponent):
            return source.zero()

        return _AdicCompletionAlgebraParent(
            zero_engine,
            source,
            defining,
            precision,
            projection_lift=projection_lift,
            arithmetic_mode="exact_backend",
            completion_image=completion_image,
            completion_map_kernel=unit_ideal,
            **degenerate_formal_data,
        )
    # Completion maps onto R/I; proper I implies nontrivial completion.
    # This says nothing about zero divisors or a truncation model's domain status.
    nontrivial_categories = (
        (OwnedRings().Nontrivial(),) if defining_is_unit is False else ()
    )
    if nontrivial_categories:
        degenerate_formal_data["extra_categories"] = (
            *degenerate_formal_data.get("extra_categories", ()),
            *nontrivial_categories,
        )
    if (defining == zero_ideal) is True:
        def projection_lift(value, _exponent):
            return _owned_engine_element(source, engine(value))

        return _AdicCompletionAlgebraParent(
            engine,
            source,
            defining,
            precision,
            projection_lift=projection_lift,
            arithmetic_mode="exact_backend",
            completion_image=lambda element: _engine_element(source, source(element)),
            completion_map_kernel=zero_ideal,
            **degenerate_formal_data,
        )
    if len(generators) == 1 and engine is SageZZ:
        generator = generators[0]
        prime = abs(SageZZ(generator))
        if not prime.is_prime():
            raise ValueError(
                f"the completion of ZZ at (p) needs p prime, but the ideal {defining} is generated by {generator}"
            )
        completion_engine = engine.completion(prime, int(precision))

        def projection_lift(value, exponent):
            value_precision = value.precision_absolute()
            assert exponent <= value_precision, (
                f"the truncation at exponent {exponent} exceeds the represented element's "
                f"absolute precision {value_precision}"
            )
            return source(int(value.lift()))

        return _AdicCompletionAlgebraParent(
            completion_engine,
            source,
            defining,
            precision,
            projection_lift=projection_lift,
            completion_map_kernel=zero_ideal,
            extra_categories=nontrivial_categories,
        )

    base = source.base_ring()
    assert (
        source in SymmetricAlgebras(base)
        or source in AlgebrasWithChosenFinitePresentation(base)
    ), (
        f"cannot construct the completion of {source} at {defining}: it is computed only for "
        "polynomial rings, the p-adic integers, and quotients of polynomial rings"
    )
    if source not in SymmetricAlgebras(base):
        if source in AlgebrasWithChosenFinitePresentation(base):
            selected_power = defining.power(int(precision))
            truncation = source.quotient_ring(selected_power)
            truncation_engine = _engine_ring(truncation)
            assert truncation_engine is not truncation, (
                f"cannot construct the completion of {source} at {defining}: the truncation {truncation} "
                "has no computer-algebra model"
            )
            quotient_map = truncation.quotient_map()

            def completion_image(element):
                return _engine_element(truncation, quotient_map(source(element)))

            def projection_lift(value, exponent):
                assert exponent <= int(precision), (
                    f"the truncation at exponent {exponent} exceeds the precision {precision} of the completion"
                )
                return _owned_engine_element(truncation, value).lift()

            completed_ideal_generators = tuple(
                completion_image(generator)
                for generator in defining.ideal_generators()
            )
            arithmetic_mode = "finite_approximation"
            completion_map_kernel = None
            if (selected_power == zero_ideal) is True:
                arithmetic_mode = "exact_backend"
                completion_map_kernel = zero_ideal
            elif (defining.power(2) == defining) is True:
                arithmetic_mode = "exact_backend"
                completion_map_kernel = defining
            return _AdicCompletionAlgebraParent(
                truncation_engine,
                source,
                defining,
                precision,
                completed_ideal_generators=completed_ideal_generators,
                projection_lift=projection_lift,
                arithmetic_mode=arithmetic_mode,
                completion_image=completion_image,
                completion_map_kernel=completion_map_kernel,
                extra_categories=nontrivial_categories,
            )

    source_engine = _engine_ring(source)
    selected_variables = []
    engine_variables = tuple(source_engine.gens())
    for generator in generators:
        matching = tuple(variable for variable in engine_variables if generator == variable)
        assert len(matching) == 1, (
            f"cannot complete {source} at {defining}: completion of a polynomial ring is computed only "
            f"at an ideal generated by variables, and the generator {generator} is not a variable"
        )
        selected_variables.append(matching[0])
    completion_parameter = (
        selected_variables[0]
        if len(selected_variables) == len(engine_variables) == 1
        else tuple(selected_variables)
    )
    completion_engine = source_engine.completion(
        completion_parameter,
        prec=Infinity,
    )
    engine_map = completion_engine.coerce_map_from(source_engine)
    completed_ideal_generators = tuple(
        completion_engine(variable) for variable in selected_variables
    )

    def projection_lift(value, exponent):
        polynomial = value.truncate(exponent).polynomial()
        return _owned_engine_element(source, source_engine(polynomial))

    algebra_base = None
    formal_parameter_labels = None
    extra_categories = nontrivial_categories
    if len(selected_variables) == len(engine_variables):
        algebra_base = base
        formal_parameter_labels = tuple(source_engine.variable_names())
        extra_categories = (FormalPowerSeriesRings(base), *nontrivial_categories)
    return _AdicCompletionAlgebraParent(
        completion_engine,
        source,
        defining,
        precision,
        engine_map=engine_map,
        completed_ideal_generators=completed_ideal_generators,
        projection_lift=projection_lift,
        arithmetic_mode="exact_lazy",
        # A polynomial has finite degree in the selected variables over any
        # coefficient ring, so no nonzero polynomial lies in all their powers.
        completion_map_kernel=zero_ideal,
        algebra_base=algebra_base,
        formal_parameter_labels=formal_parameter_labels,
        extra_categories=extra_categories,
    )


class FormalPowerSeriesRings(OwnedCategoryOverBaseRing):
    r"""Formal power-series rings over the owned commutative ring ``R``.

    The selected construction retains a finite ordered family of formal
    variables and the completion map from the polynomial ring on that family.
    The coefficient ring remains ``R`` with its actual constant-series map;
    the formal variables need not generate the completed ring as an algebra.
    """

    def parameter_category(self):
        r"""The coefficient ring is commutative, with the zero ring allowed."""
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The formal power series ring in one variable."""
        return self.base_ring().power_series_ring("t")

    def _repr_object_names(self):
        return f"formal power-series rings over {self.base_ring()}"

    def super_categories(self):
        return [
            Algebras(self.base_ring()).Associative().Unital().Commutative(),
            OwnedAdicallyCompleteRings(),
        ]

    def _call_(self, *args, **kwargs):
        r"""Construct ``R[[x_1,...,x_n]]`` as the selected adic completion.

        Sage's power-series constructor is used only to parse its established
        notation and computational precision.  The mathematical object is the
        completion of ``R[x_1,...,x_n]`` at the ideal generated by the selected
        variables, through the general :class:`AdicCompletions` constructor.
        """
        parser = _SagePowerSeriesRing(_engine_ring(self.base_ring()), *args, **kwargs)
        labels = tuple(parser.variable_names())
        polynomial = self.base_ring().polynomial_ring(labels)
        defining = polynomial.ideal(
            *(polynomial.algebra_generator(label) for label in labels)
        )
        precision = parser.default_prec()
        completion = AdicCompletions()(
            polynomial,
            defining,
            precision=int(precision),
        )
        if completion not in self:
            raise ArithmeticError(
                f"the completion {completion} of {polynomial} at {defining} was not constructed as a "
                f"power series ring"
            )
        return completion

    class ParentMethods:
        def formal_parameter_set(self):
            r"""Return the formal labels in the polynomial generator order."""
            labels = self._preamble_formal_parameter_labels
            assert labels is not None, (
                f"the realization of {self} supplies no selected formal parameter family"
            )
            return labels

        def formal_parameter(self, label):
            r"""Return the corresponding polynomial generator's completion image."""
            labels = self.formal_parameter_set()
            normalized = labels(label)
            position = int(labels.ranking_map()(normalized))
            source = self.completion_source()
            source_label = source.algebra_generating_set()[position]
            return self.completion_map()(source.algebra_generator(source_label))

        def power_series_variable(self):
            labels = self.formal_parameter_set()
            if int(labels.cardinality()) != 1:
                raise ArithmeticError(
                    f"{self} is not a power series ring in one variable: it has {labels.cardinality()} formal variables"
                )
            return self.formal_parameter(labels[0])

        def _cardinality_decision(self):
            r"""Supply the finite-variable formula from retained cardinal data.

            An empty variable family gives ``|R|``.  A positive finite family
            has countably many monomials, giving ``|R|^aleph0``.  A missing
            coefficient cardinal or an unsupported parameter cardinal leaves
            this optional computation unavailable.
            """
            coefficient_size = self.base_ring()._cardinality_decision()
            if coefficient_size is None:
                return None
            parameter_size = self.formal_parameter_set()._cardinality_decision()
            if parameter_size is None:
                return None
            parameter_size = cardinal(parameter_size)
            if (
                not parameter_size.expression().is_normal_form()
                or parameter_size.is_finite() is not True
            ):
                return None
            parameter_count = int(parameter_size.finite_value())
            match parameter_count:
                case 0:
                    return cardinal(coefficient_size)
                case _:
                    if not cardinal(coefficient_size).expression().is_normal_form():
                        return None
                    return cardinal(coefficient_size) ** aleph0

    class ElementMethods:
        def coefficient(self, degree):
            r"""Return one coefficient in the actual coefficient ring.

            In one variable, ``degree`` may be an integer.  In several
            variables it is an exponent tuple in ``formal_parameter_set``
            order.  The integer zero also denotes the constant coefficient
            in every arity.  Negative exponents have coefficient zero.

            This computation uses the selected finite ordered variable family
            and the existing exact series realization.  Native multivariate
            series indexing first returns a homogeneous polynomial; the
            exponent tuple then selects its scalar monomial coefficient.
            """
            parent = self.parent()
            base = parent.base_ring()
            parameters = parent.formal_parameter_set()
            assert parameters in FiniteOrderedSets(), (
                f"coefficient extraction in {parent} currently requires a selected "
                "finite ordered formal parameter family"
            )
            labels = tuple(parameters)
            if isinstance(degree, (tuple, list)):
                exponents = tuple(index(exponent) for exponent in degree)
                if len(exponents) != len(labels):
                    raise ValueError(
                        f"a coefficient of {parent} needs {len(labels)} exponents "
                        f"in formal parameter order, but {degree} supplies {len(exponents)}"
                    )
            else:
                exponent = index(degree)
                if exponent < 0:
                    return base.zero()
                if exponent == 0:
                    exponents = (0,) * len(labels)
                elif len(labels) == 1:
                    exponents = (exponent,)
                else:
                    raise ValueError(
                        f"a coefficient of {parent} needs an exponent tuple in "
                        "formal parameter order; only the constant coefficient "
                        "has the integer index zero in this arity"
                    )
            if any(exponent < 0 for exponent in exponents):
                return base.zero()
            if (base.one() == base.zero()) is True:
                return base.zero()
            backend = parent._engine_element(self)
            if not labels:
                return _owned_engine_element(base, backend)
            if len(labels) == 1:
                coefficient = backend[exponents[0]]
            else:
                homogeneous = backend[sum(exponents)]
                exponent_by_label = dict(zip(labels, exponents, strict=True))
                native_exponents = tuple(
                    exponent_by_label[label]
                    for label in backend.parent().variable_names()
                )
                coefficient = homogeneous[native_exponents]
            return _owned_engine_element(base, coefficient)

        def __getitem__(self, degree):
            return self.coefficient(degree)


def Zp(*args, **kwargs):
    source = _owned_integers()
    prime_value = args[0] if args else kwargs.get("p")
    owned_prime = source(prime_value)
    prime = SageZZ(_engine_element(source, owned_prime))
    engine_kwargs = dict(kwargs)
    # The precision is a session integer, which Sage's factory cannot read;
    # it crosses as the Sage integer it names.
    match args[1:2]:
        case (precision,):
            args = (args[0], SageZZ(_engine_element(source, source(precision))), *args[2:])
    if "prec" in engine_kwargs:
        engine_kwargs["prec"] = SageZZ(_engine_element(source, source(engine_kwargs["prec"])))
    engine_args = (prime, *args[1:]) if args else args
    if not args and "p" in engine_kwargs:
        engine_kwargs["p"] = prime
    parser = _SageZp(*engine_args, **engine_kwargs)
    defining = source.ideal(owned_prime)
    return AdicCompletions()(
        source,
        defining,
        precision=int(parser.precision_cap()),
    )
class _DualNumbersAlgebraParent(_OwnedAlgebraParent):
    r"""The dual-number quotient with its defining quotient data fixed at construction."""

    class Element(_OwnedAlgebraElement):
        def __init__(self, parent, backend_value):
            r"""Supply the inherited quotient lift's actual source datum.

            The native element constructor and every ring-arithmetic result
            enter through this selected element class. The public lift
            operation remains at QuotientRings.ElementMethods.
            """
            super().__init__(parent, backend_value)
            self._representative = _owned_engine_element(
                parent.quotient_source(), backend_value.lift()
            )

    def algebra_base_ring(self):
        r"""Return the selected coefficient ring of the dual-number algebra."""
        return self.base_ring()

    def __init__(self, engine, base, polynomial, defining_ideal, label) -> None:
        from sage_extensions.categories.modules.native_modules import (
            _NativeModuleBasis,
        )

        engine_map = engine.coerce_map_from(_engine_ring(polynomial))
        basis_labels = finite_ordered_set((0, 1))
        basis_source = base.free_module(basis_labels)

        def basis_image(index):
            value = engine.one() if index == 0 else engine.gen()
            return self._from_engine_element(value)

        def basis_coordinates(value):
            lift = _engine_element(self, self(value)).lift()
            return {
                index: _owned_engine_element(base, lift[index])
                for index in basis_labels
            }

        self._native_module_basis = _NativeModuleBasis(
            basis_source,
            basis_image,
            basis_coordinates,
        )

        def quotient_map():
            return _canonical_map(
                polynomial,
                self,
                engine_map,
            )

        self._quotient_source = polynomial
        self._quotient_defining_ideal = defining_ideal
        self._quotient_map_factory = quotient_map
        placements = [QuotientRings()]
        ring_placements = []
        if base in OwnedRings().Commutative():
            ring_placements.append(OwnedRings().Commutative())
        if base in OwnedRings().Noetherian():
            placements.append(OwnedRings().Noetherian())
            ring_placements.append(OwnedRings().Noetherian())
        if base in OwnedRings().Artinian():
            placements.append(OwnedRings().Artinian())
            ring_placements.append(OwnedRings().Artinian())
        if base in OwnedRings().Commutative().Local():
            local = OwnedRings().Commutative().Local()
            placements.append(local)
            ring_placements.append(local)
        _OwnedAlgebraParent.__init__(
            self,
            engine,
            base,
            (label,),
            categories=tuple(placements),
            ring_placement=lambda: tuple(ring_placements),
        )
        if base in OwnedRings().Commutative().Local():
            epsilon_bar = self._from_engine_element(engine.gen())
            residue = base.residue_field()
            residue_map = OwnedRings().Mor(self, residue)(
                lambda value: base.residue_map()(basis_coordinates(self(value))[0])
            )
            self._local_ring_construction = LocalRingConstruction(
                maximal_ideal_factory=lambda: _maximal_ideal_over_local_base(
                    self, base, (epsilon_bar,)
                ),
                residue_field=residue,
                residue_map=residue_map,
            )


def _dual_numbers(base_ring, name="epsilon"):
    r"""Return the dual-number algebra ``R[epsilon]/(epsilon^2)``."""
    base = _own_ring(base_ring)
    polynomial = base.polynomial_ring(name)
    engine_polynomial = _engine_ring(polynomial)
    epsilon = polynomial.algebra_generator(name)
    defining_ideal = polynomial.ideal(epsilon**2)
    quotient_engine = engine_polynomial.quotient(_engine_ideal(polynomial, defining_ideal))
    return _DualNumbersAlgebraParent(
        quotient_engine,
        base,
        polynomial,
        defining_ideal,
        name,
    )


__all__ = [
    "AdicCompletions",
    "IntegralPrimeSpectra",
    "DistinguishedOpenSubobjects",
    "GeneratedIdealView",
    "LocalizationRings",
    "PrimeLocalizations",
    "QuotientRings",
    "ZariskiClosedSubobjects",
    "Zp",
]
