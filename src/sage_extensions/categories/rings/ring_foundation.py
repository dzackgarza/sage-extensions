"""Owned scalar hierarchy and the boundary to Sage computation rings."""

from abc import ABCMeta
from collections.abc import Mapping
from functools import wraps

from sage.all import (
    GF as _SageGF,
)
from sage.all import (
    PolynomialRing as _SagePolynomialRing,
)
from sage.all import (
    ComplexField as _SageComplexField,
)
from sage.all import (
    Qp as _SageQp,
)
from sage.all import (
    RealField as _SageRealField,
)
from sage.all import (
    Zmod as _SageZmod,
)
from sage.all import (
    matrix as _SageMatrix,
)
from sage.arith.misc import (
    euler_phi as _engine_euler_phi,
)
from sage.arith.misc import (
    number_of_divisors as _engine_number_of_divisors,
)
from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.categories.fields import Fields as SageFields
from sage.categories.finite_fields import FiniteFields as SageFiniteFields
from sage.categories.map import Map
from sage.categories.morphism import Morphism, SetMorphism
from sage.categories.number_fields import NumberFields as SageNumberFields
from sage.categories.principal_ideal_domains import (
    PrincipalIdealDomains as SagePrincipalIdealDomains,
)
from sage.categories.rings import Rings as SageRings
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.latex import latex
from sage.misc.lazy_attribute import lazy_attribute
from sage.rings.abc import Order as SageNumberFieldOrder
from sage.rings.finite_rings.integer_mod_ring import IntegerModRing_generic
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.morphism import RingHomomorphism as SageRingHomomorphism
from sage.rings.infinity import Infinity as SageInfinity
from sage.rings.polynomial.multi_polynomial_ring_base import MPolynomialRing_base
from sage.rings.polynomial.polynomial_quotient_ring import PolynomialQuotientRing_generic
from sage.rings.polynomial.polynomial_ring import PolynomialRing_generic
from sage.rings.quotient_ring import QuotientRing_generic
from sage.rings.rational_field import QQ as SageQQ
from sage.rings.ring import Ring
from sage.structure.element import CommutativeRingElement, RingElement, parent as element_parent
from sage.structure.parent import Parent
from sage.rings.qqbar import AA as SageAA
from sage.rings.finite_rings.finite_field_constructor import GF as SageGF
from sage.structure.richcmp import op_EQ, op_GE, op_GT, op_LE, op_LT, op_NE, richcmp
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoryPacketMethods,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import (
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.magmas import Monoids
from sage_extensions.categories.rings.semirings import (
    OwnedRngs,
    OwnedSemirings,
    RingMorCategoryConstruction,
)
from sage_extensions.categories import sets as owned_sets
from sage_extensions.logic import AtomicProposition, Predicate, Propositions, conjunction, negation
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import RealizationHook, realize_owned_category, refine
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class _OwnedRingBootstrapParent(metaclass=ABCMeta):
    r"""Declared parent types admitted while their owned ring category is built.

    This is a construction-time type contract only. Category membership is
    the mathematical classification once Parent initialization finishes; this
    virtual base exists solely for the self-referential interval before that
    membership can be asked without circularity.
    """


if "Noetherian" not in all_axioms:
    all_axioms.add("Noetherian")
if "Artinian" not in all_axioms:
    all_axioms.add("Artinian")
if "Local" not in all_axioms:
    all_axioms.add("Local")
if "PrincipalIdeals" not in all_axioms:
    all_axioms.add("PrincipalIdeals")
if "Prime" not in all_axioms:
    all_axioms.add("Prime")
if "Nontrivial" not in all_axioms:
    all_axioms.add("Nontrivial")


class RngMorphism:
    r"""A rng morphism; additive and multiplicative behavior comes from the Mor graph."""

    def __init__(self, parent, function, *, engine_morphism=None) -> None:
        _ = engine_morphism
        super().__init__(parent, function)


class RingMorphism:
    r"""A unital ring morphism in the owned ring category."""

    def __init__(self, parent, function, *, engine_morphism=None) -> None:
        self._engine_morphism = engine_morphism
        self._preamble_is_identity = False
        super().__init__(parent, function)

    # Ring morphisms compare by their determining data (``_richcmp_`` below).
    # The pointwise ``OwnedSetMorphism.__eq__`` comes earlier in the MRO than
    # Sage's ``Element.__eq__``, which dispatches to ``_richcmp_``, and it is
    # undecided on every infinite ring; so equality is stated here.  The hash
    # stays the owned set-map hash of the parent, which equal maps share.
    def __eq__(self, other):
        return self._richcmp_(other, op_EQ)

    def __ne__(self, other):
        return self._richcmp_(other, op_NE)

    def __hash__(self) -> int:
        return hash(id(self.parent()))

    def _engine_morphism_crossing(self):
        r"""Return the private engine realization when one was selected.

        Protected ring-morphism realization endpoint under OWN-05--07. The
        representation is exposed only through the owner dispatcher below;
        ordinary mathematical consumers use this morphism itself.
        """
        assert self._engine_morphism is not None, (
            f"cannot compute with the ring morphism {self}: it has no computer-algebra model"
        )
        return self._engine_morphism

    def __mul__(self, other):
        # Any ring morphism composes here, including one whose Mor is a
        # subcategory's (a number-field embedding is a ring morphism).
        if not _is_ring_map_into(other, self.domain()):
            return NotImplemented
        if self._preamble_is_identity or (
            self._engine_morphism is not None and self._engine_is_identity()
        ):
            return other
        if isinstance(other, RingMorphism):
            if other._preamble_is_identity or (
                other._engine_morphism is not None and other._engine_is_identity()
            ):
                return self
        elif other.domain() is other.codomain() and other is other.parent().identity():
            return self
        return _ring_composite(self, other)

    def compose(self, before):
        result = self * before
        if result is NotImplemented:
            raise ValueError(
                f"cannot compose {self} after {before}: {before} ends at {before.codomain()}, but {self} "
                f"starts at {self.domain()}"
            )
        return result

    def as_algebra(self):
        r"""Return the codomain viewed as the algebra defined by this structure map."""
        from sage_extensions.categories.algebras.algebras import _own_algebra

        return _own_algebra(self)

    def is_group_algebra_augmentation(self) -> bool:
        r"""Return whether this map is the represented augmentation ``R[G] -> R``."""
        from sage_extensions.categories.functors.group_actions import (
            _is_augmentation_of_group_algebra,
        )

        return _is_augmentation_of_group_algebra(self)

    def is_group_algebra_subgroup_inclusion(self) -> bool:
        r"""Return whether this map is induced by a represented subgroup inclusion."""
        from sage_extensions.categories.functors.group_induction import (
            _is_group_algebra_map_of_subgroup_inclusion,
        )

        return _is_group_algebra_map_of_subgroup_inclusion(self)

    def is_identity(self):
        r"""Decide identity from the ring map's actual determining data.

        An elementwise map need not retain a native realization. In that
        case compare with the fixed Mor's identity; an unavailable equality
        decision remains a proposition.

        Unexecuted localization identity specimen::

            sage: from dzack_research.preamble.all import *
            sage: A = QQ['x']; x = A.algebra_generator('x')
            sage: B = A.localization(x)
            sage: f = B.Mor(B)(lambda element: element)
            sage: f.is_identity()
            True
            sage: (f*f).is_identity()
            True
        """
        if self.domain() is not self.codomain():
            return False
        if self._preamble_is_identity:
            return True
        if self._engine_morphism is not None:
            return self._engine_is_identity()
        return _ring_morphisms_equal(self, self.parent().identity())

    def _engine_is_identity(self) -> bool:
        r"""Ask only the selected private engine realization about identity."""
        if self._engine_morphism is None:
            return False
        return bool(self._engine_morphism.is_identity())

    def inverse(self):
        r"""Return the inverse ring map of this ring isomorphism.

        A map of fields is injective, so it is invertible exactly when it is
        surjective; the retained exact engine map decides that and supplies
        the inverse, which is again a map of fields.
        """
        if self._preamble_is_identity:
            return self
        domain = self.domain()
        match domain:
            case _ if domain in OwnedFields() and self._engine_morphism is not None:
                return self.codomain().Mor(domain)(self._engine_morphism.inverse())
            case _:
                return super().inverse()

    def restrict_along(self, embedding):
        r"""Return the automorphism ``tau`` of ``K`` with ``j tau = self j``, for ``j: K -> L``.

        ``self`` is an automorphism of ``L``.  The restriction is unique when
        it exists because ``j`` is injective, and it is found among the
        automorphisms of ``K`` by comparing values on the field generators.
        """
        field = embedding.domain()
        assert field in OwnedFields() and _is_finite_or_number_field(field), (
            f"cannot restrict {self} along {embedding}: restriction is computed only along a map out of a "
            f"finite or number field, but {field} is neither"
        )
        assert embedding.codomain() is self.domain() and self.domain() is self.codomain(), (
            f"cannot restrict {self} along {embedding}: {self} must be an automorphism of the codomain "
            f"{embedding.codomain()} of {embedding}"
        )
        generators = field.field_generators()
        restrictions = owned_sets.finite_ordered_set(tuple(
            candidate
            for candidate in field.Mor(field).embeddings()
            if all(
                embedding(candidate(generator)) == self(embedding(generator))
                for generator in generators
            )
        ))
        assert restrictions.cardinality() == 1, (
            f"the automorphism {self} does not restrict along {embedding} to an automorphism of {field}: "
            f"{restrictions.cardinality()} automorphisms of {field} are compatible with it"
        )
        return restrictions[0]

    def extensions_along(self, embedding, candidates):
        r"""Return the candidates ``sigma`` with ``sigma j = j self``, for ``j: K -> L``.

        ``self`` is an automorphism of ``K`` and each candidate a map out of
        ``L``; the condition is checked on the field generators of ``K``.
        """
        field = embedding.domain()
        assert field in OwnedFields() and _is_finite_or_number_field(field), (
            f"cannot extend {self} along {embedding}: extension is computed only along a map out of a "
            f"finite or number field, but {field} is neither"
        )
        generators = field.field_generators()
        return owned_sets.finite_ordered_set(tuple(
            candidate
            for candidate in candidates
            if all(
                candidate(embedding(generator)) == embedding(self(generator))
                for generator in generators
            )
        ))

    def _richcmp_(self, other, op):
        r"""Decide equality from represented universal/construction data.

        Sage's generic morphism comparison asks the domain for backend
        generators.  Owned localizations deliberately do not expose such a
        backend presentation: a map out of ``S^-1 R`` is determined instead by
        its restriction along ``R -> S^-1 R``.  Quotients are determined by
        precomposition with their quotient projection, while a framed algebra
        is determined by its scalar restriction and selected algebra-generator
        images.  Each of ``R -> S^-1 R``, the quotient projection and the map
        from the polynomial ring on the selected algebra generators is an
        epimorphism of rings owned by its constructor, so equality belongs here
        rather than at a downstream scheme/descent consumer.
        """
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        equal = _ring_morphisms_equal(self, other)
        return equal if op == op_EQ else negation(equal)

    def extension_of_ideal(self, ideal):
        r"""Return ``I S``, the ideal of the codomain generated by the images of ``I``.

        The extension of an ideal along ``f: R -> S`` is generated by the
        images of any generating set of ``I``, because the ideal they generate
        already contains every image.  So this needs nothing of ``f`` beyond
        its values, and the localization of an ideal is the case where ``f``
        inverts a submonoid.

        For the retained completion map of a Noetherian source, flatness
        also transports the ideal's presented inclusion. A different map
        into that same completed ring need not be flat, so that construction
        is selected only for the actual canonical completion arrow.
        """

        domain = self.domain()
        assert ideal.ring() is domain, (
            f"cannot extend {ideal} along {self}: it is an ideal of {ideal.ring()}, not of {domain}"
        )
        codomain = self.codomain()
        from sage_extensions.categories.rings.commutative_algebra import (
            AdicCompletions,
        )

        if (
            codomain in AdicCompletions()
            and domain in OwnedRings().Noetherian()
            and self is codomain.completion_map()
        ):
            from sage_extensions.categories.rings.commutative_ideals import (
                _flat_extension_commutative_ideal,
            )

            return _flat_extension_commutative_ideal(ideal, self)
        return codomain.ideal(*(self(generator) for generator in ideal.ideal_generators()))

    def contraction_of_ideal(self, ideal):
        r"""Return ``f^{-1}(J)``, the contraction of an ideal of the codomain.

        Along a quotient map ``R -> R/I`` the preimage of ``J`` is generated by
        ``I`` together with lifts of generators of ``J``: an element lands in
        ``J`` exactly when it differs from such a lift by something in ``I``.
        That is the case a closed subscheme is written in, and taking ``J`` to
        be zero recovers the kernel.

        Along a localization map contraction is saturation, supplied by the
        ideal owner. These formulas apply to the canonical maps, not to an
        arbitrary map with the same endpoints. General preimage ideals need
        their membership presentation; finite generators require a further
        algorithm (Atiyah--Macdonald, Proposition 3.11).
        A retained Sage ring homomorphism supplies its documented
        ``inverse_image`` algorithm on exact computation-ring ideals.

        Unexecuted saturation specimen::

            sage: from dzack_research.preamble.all import *
            sage: A = QQ['x']; x = A.algebra_generator('x')
            sage: S = A.localization(x)
            sage: f = S.localization_map()
            sage: f.contraction_of_ideal(S.ideal(S(x))) == A.ideal(A.one())
            True
            sage: f.contraction_of_ideal(S.ideal(S.zero())) == A.ideal(A.zero())
            True
            sage: Q = A.quotient_ring(A.ideal(x*x))
            sage: collapse = A.Mor(Q)({'x': Q.zero()})
            sage: collapse.contraction_of_ideal(Q.ideal(Q.zero())) == A.ideal(x)
            True
            sage: Q.quotient_map().contraction_of_ideal(Q.ideal(Q.zero())) == A.ideal(x*x)
            True
        """

        from sage_extensions.categories.rings.commutative_algebra import (
            QuotientRings,
        )

        domain = self.domain()
        codomain = self.codomain()
        assert ideal.ring() is codomain, (
            f"cannot contract {ideal} along {self}: it is an ideal of {ideal.ring()}, not of {codomain}"
        )
        if self.is_identity() is True:
            return ideal
        match codomain:
            case _ if codomain in LocalizationRings() and self is codomain.localization_map():
                return ideal.contraction_from_localization()
            case _ if (
                codomain in QuotientRings()
                and codomain.quotient_source() is domain
                and self is codomain.quotient_map()
            ):
                return domain.ideal(
                    *codomain.defining_ideal().ideal_generators(),
                    *(generator.lift() for generator in ideal.ideal_generators()),
                )
            case _ if (
                isinstance(self._engine_morphism, SageRingHomomorphism)
                and domain not in LocalizationRings()
                and codomain not in LocalizationRings()
            ):
                from sage_extensions.categories.rings.commutative_ideals import (
                    _engine_commutative_ideal,
                )

                source_engine = _engine_ring(domain)
                target_engine = _engine_ring(codomain)
                assert (
                    self._engine_morphism.domain() is source_engine
                    and self._engine_morphism.codomain() is target_engine
                ), "ideal preimage requires the retained ring map's exact computation endpoints"
                # Sage RingHomomorphism.inverse_image owns elimination of
                # the graph ideal; see sage/rings/morphism.pyx. Both ideal
                # lattices here belong to the actual computation rings.
                represented = _engine_commutative_ideal(ideal)
                assert represented.ring() is target_engine, (
                    "ideal preimage requires an ideal of the retained target computation ring"
                )
                preimage = self._engine_morphism.inverse_image(represented)
                assert preimage.ring() is source_engine, (
                    "the computed ideal preimage must belong to the retained source computation ring"
                )
                return domain.ideal(
                    *(_owned_engine_element(domain, generator) for generator in preimage.gens())
                )
            case _:
                assert False, (
                    f"contraction of {ideal} along {self} requires a general preimage-ideal "
                    "construction; available algorithms use canonical localization or quotient maps, "
                    "or a retained Sage ring homomorphism with exact ideal realizations"
                )

    def kernel(self):
        r"""Return the kernel ideal ``f^{-1}(0)`` of this ring morphism.

        A ring morphism ``R -> End_R(M)`` is the scalar action that makes ``M``
        an ``R``-module, and ``rho(r) = 0`` says exactly that ``r`` kills
        ``M``, so its kernel is ``Ann_R(M)``.  The module is the endomorphism
        Mor-object's own domain, so nothing has to be carried on the morphism
        for it to be found.
        """
        from sage_extensions.categories.group.additive_mors import (
            AdditiveEndomorphismRings,
        )
        from sage_extensions.categories.modules.pure.modules import Modules

        codomain = self.codomain()
        if codomain in AdditiveEndomorphismRings(codomain.base_ring()):
            module = codomain.domain()
            if (
                module is codomain.codomain()
                and module in Modules(self.domain())
                and module.scalar_action() is self
            ):
                return module.annihilator()
            assert (
                module is codomain.codomain()
                and module in Modules(self.domain())
                and module.scalar_action() is self
            ), (
                f"cannot compute the kernel of {self}: the kernel of a map into End({module}) is computed "
                f"here only when {self} is the scalar action of {self.domain()} on {module}"
            )
        return self.contraction_of_ideal(codomain.ideal(codomain.zero()))

    def is_injective(self):
        r"""Decide ``ker f = 0`` for ``f: R -> S`` from the category of ``R`` and the characteristic of ``S``.

        Out of a field the kernel is an ideal, so it is ``0`` or ``R``, and it
        is ``R`` exactly when ``1_S = f(1) = 0``: ``f`` is injective exactly
        when ``1_S`` is not zero.

        Out of an order ``O`` (``ZZ`` among them), ``f`` is injective exactly
        when ``char S = 0``.  A positive characteristic ``n`` puts ``n`` in
        the kernel.  Conversely, a nonzero ``a in O`` is integral, so its
        minimal polynomial over ``QQ`` has integer coefficients and a nonzero
        constant term ``c``; ``c`` lies in ``aO``, so ``f(a) = 0`` forces
        ``c 1_S = 0`` and ``char S`` positive.

        Any other domain takes the set-level answer.
        """
        domain = self.domain()
        codomain = self.codomain()
        match domain:
            case _ if domain in OwnedFields():
                return not codomain.one().is_zero()
            case _ if domain in OwnedOrders():
                return codomain.characteristic().is_zero()
            case _:
                return super().is_injective()


def _selected_engine_ring_morphism(morphism):
    r"""Return a retained private ring-map realization, or None.

    Protected ring-morphism contract under OWN-05--07. The permitted external
    caller role is a computation adapter that must preserve the exact native
    coefficient map selected when this owned ring morphism was built; scheme
    coordinate pullback is such an adapter. The raw map may be used only inside
    that adapter and mathematical values are raised through owned endpoints.
    Reconstructible maps need no crossing and return None here.
    """
    if element_parent(morphism) is not OwnedRings().Mor(
        morphism.domain(), morphism.codomain()
    ):
        return None
    return morphism._engine_morphism


def _ringlike_mor_element(parent, datum, provider_type):
    r"""Admit one rng/ring arrow at its fixed-Mor owner."""
    if isinstance(datum, provider_type):
        if datum.domain() is not parent.domain() or datum.codomain() is not parent.codomain():
            raise ValueError(
                f"cannot view {datum} as an element of Mor({parent.domain()}, {parent.codomain()}): it is a "
                f"morphism {datum.domain()} -> {datum.codomain()}"
            )
        if datum.parent() is parent:
            return datum
        raise TypeError(f"{datum} belongs to another ring Mor; apply the functor between the categories")
    if isinstance(datum, Mapping):
        from sage_extensions.categories.algebras.algebras import (
            _engine_algebra_morphism_from_generator_images,
        )

        engine_morphism = _engine_algebra_morphism_from_generator_images(
            parent.domain(),
            parent.codomain(),
            datum,
        )
        return _ringlike_mor_from_engine(parent, engine_morphism)
    if isinstance(datum, Map):
        raise TypeError(f"{datum} is an arrow of another Mor; native ring computations use the protected engine crossing")
    if element_parent(datum) is parent.codomain() and _is_number_field(parent.domain()):
        # A number field is QQ(theta) for its primitive element theta, so a
        # ring map out of it is the image of theta; out of QQ it is unique.
        engine_domain = _engine_ring(parent.domain())
        engine_codomain = _engine_ring(parent.codomain())
        match engine_domain:
            case _ if engine_domain is SageQQ:
                engine_morphism = engine_domain.hom(engine_codomain)
            case _:
                engine_morphism = engine_domain.hom(
                    [_engine_element(parent.codomain(), datum)], engine_codomain
                )
        return _ringlike_mor_from_engine(parent, engine_morphism)
    if callable(datum):
        return parent.elementwise(datum)
    raise TypeError(
        f"cannot build a morphism {parent.domain()} -> {parent.codomain()} from {datum!r}: give "
        "the images of the ring generators or a map on elements"
    )


def _ringlike_mor_from_engine(parent, datum):
    r"""Raise a selected native ring computation at the ring-Mor owner's exact endpoints.

    Protected engine crossing for ring structure maps and algebra/scheme
    adapters; native maps are not public arrow-constructor data.
    """
    source_engine = _engine_ring(parent.domain())
    target_engine = _engine_ring(parent.codomain())

    def engine_endpoint(ring):
        return _engine_ring(ring) if ring in OwnedRings() else ring

    if engine_endpoint(datum.domain()) is not source_engine:
        raise ValueError(
            f"cannot view {datum} as an element of Mor({parent.domain()}, {parent.codomain()}): "
            f"its domain is {datum.domain()}"
        )
    if engine_endpoint(datum.codomain()) is not target_engine:
        raise ValueError(
            f"cannot view {datum} as an element of Mor({parent.domain()}, {parent.codomain()}): "
            f"its codomain is {datum.codomain()}"
        )
    return parent.element_class(
        parent,
        lambda element: _owned_engine_element(
            parent.codomain(), datum(_engine_element(parent.domain(), element))
        ),
        engine_morphism=datum,
    )

def _engine_ring_value(ring, value):
    """Lower an owned or already-engine ring element to the selected engine."""
    from sage.categories.rings import Rings as SageRings
    from sage.structure.element import parent as element_parent

    source = _own_ring(ring)
    engine = _engine_ring(source)
    value_parent = element_parent(value)
    if value_parent is engine or value_parent in SageRings():
        return engine(value)
    return engine(_engine_element(source, source(value)))


def _ringlike_mor_identity(mor):
    """Identity of a fixed ring-like Mor, retaining its identity datum."""
    if mor.domain() is not mor.codomain():
        raise ValueError(
            f"the identity morphism exists only on Mor(R, R), but this is Mor({mor.domain()}, {mor.codomain()})"
        )
    identity = mor.elementwise(lambda element: element)
    identity._preamble_is_identity = True
    return identity


class RngMor(CategoricalMor):
    r"""The owned set ``Hom_Rng(A,B)`` of maps preserving sum and product."""

    ElementMethods = RngMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def __call__(self, datum):
        return CategoricalMor.__call__(self, datum)

    def _from_engine_morphism(self, datum):
        return _ringlike_mor_from_engine(self, datum)

    def _element_constructor_(self, datum):
        return _ringlike_mor_element(self, datum, RngMorphism)

    def elementwise(self, function):
        if isinstance(function, Map):
            return self(function)
        return self.element_class(self, function)

    def _elementwise_with_engine(self, function, engine_morphism):
        r"""Construct an elementwise map retaining one private engine realization."""
        return self.element_class(
            self,
            function,
            engine_morphism=engine_morphism,
        )

    @object_level
    def identity(self):
        return _ringlike_mor_identity(self)

    def _repr_(self):
        return f"Mor_Ring({self.domain()}, {self.codomain()})"


def _is_ring_map_into(candidate, target) -> bool:
    r"""Whether ``candidate`` is a ring morphism ending at ``target``.

    RingMorphism composition calls this protected admission predicate on its
    right operand. Its actual ordinary RingMor membership supplies unitality;
    ring endpoints alone do not upgrade a set, magma or nonunital rng map.
    Native engine maps first enter through the owned RingMor constructor.
    """
    return (
        isinstance(candidate, Map)
        and candidate.codomain() is target
        and candidate.domain() in OwnedRings()
        and candidate in OwnedRings().Mor(candidate.domain(), target)
    )


def _ring_composite(second, first):
    r"""``second o first`` in the category of rings, evaluated elementwise.

    Every specialized ring morphism (field embeddings, order embeddings) is a
    ring morphism, so any composable pair has this composite; a
    specialization composes on its own data only when both factors are of its
    kind.
    """
    # The composite is a morphism of rings; the domain's own ``Mor`` may be a
    # more structured homset (algebra maps out of a polynomial ring), which
    # the composite need not belong to.
    composite = _ring_mor_category(first.domain(), second.codomain())

    def function(element):
        return second(first(element))

    # When both factors retain exact engine maps the composite retains their
    # engine composite, so it stays invertible and comparable on the engine.
    first_engine = _selected_engine_ring_morphism(first)
    second_engine = _selected_engine_ring_morphism(second)
    match (first_engine, second_engine):
        case (None, _) | (_, None):
            return composite.elementwise(function)
        case _ if first_engine.codomain() is second_engine.domain():
            return composite._elementwise_with_engine(function, second_engine * first_engine)
        case _:
            return composite.elementwise(function)


def _ring_mor_category(domain, codomain) -> RingMor:
    r"""Build ``Mor_Ring(domain, codomain)`` from its owned Mor family."""
    return RingMorCategoryConstruction(OwnedRings()).Of(domain, codomain)


def _ring_morphism_with_engine(domain, codomain, function, engine_morphism):
    r"""Construct an owned ring morphism retaining one private engine map.

    Protected ring-Mor construction contract under OWN-05--07. Permitted
    external caller roles are commutative-algebra and scheme base-change
    adapters that have already selected an exact engine map realizing the
    supplied owned element function. The raw map is retained by the ring-Mor
    owner and is never mathematical output.
    """
    return domain.Mor(codomain, category=OwnedRings())._elementwise_with_engine(function, engine_morphism)


def _is_number_field(ring) -> bool:
    r"""Whether ``ring`` is a number field, a finite extension of ``QQ``."""
    from sage_extensions.categories.rings.number_fields import OwnedNumberFields

    return ring in OwnedNumberFields()


def _is_finite_or_number_field(field) -> bool:
    r"""Whether ``field`` is a finite field or a number field.

    These fields are finitely generated over their prime field by generators
    the session lists (:meth:`field_generators`), so a map out of one is
    determined by finitely many values.
    """
    return field in OwnedFields() and (
        field in owned_sets.FiniteSets() or _is_number_field(field)
    )


def _native_field_generators(engine):
    r"""Engine generators over the prime field, including each relative tower level."""
    match engine:
        case _ if engine is SageQQ:
            return (engine.one(),)
        case _ if engine in SageFiniteFields():
            return tuple(engine.gens())
        case _:
            return tuple(engine.gens()) + tuple(
                engine(generator)
                for generator in _native_field_generators(engine.base_field())
            )


def _field_generators(field):
    r"""A finite set of generators of a finite or number field over its prime field.

    A map of fields fixes the prime field, so two maps out of the field agree
    when they agree on these generators.
    """
    assert _is_finite_or_number_field(field), (
        f"cannot list field generators of {field}: this computation requires a represented finite "
        "field or number field, and no such generator computation is supplied here"
    )
    return owned_sets.finite_ordered_set(tuple(
        _owned_engine_element(field, generator)
        for generator in _native_field_generators(_engine_ring(field))
    ))


def _ring_morphisms_equal(left, right):
    r"""Return ``True``, ``False`` or the proposition ``equal(f, g)`` from represented determining data.

    Each case names, for the domain's category, the epimorphism or the finite
    generating family on which two maps out of it are compared (``DEV-52``).
    """
    if left is right:
        return True
    if left.domain() is not right.domain() or left.codomain() is not right.codomain():
        return False

    from sage_extensions.categories.rings.commutative_algebra import (
        QuotientRings,
    )

    domain = left.domain()
    match domain:
        case _ if domain in PrimeFields():
            # An existing unital map from a prime field is uniquely determined
            # by 1, including when the field has a quotient or localization
            # presentation.  No source transport or engine is needed.
            return True
        case _ if domain in LocalizationRings():
            source_map = domain.localization_map()
            return _ring_morphisms_equal(left * source_map, right * source_map)
        case _ if domain in QuotientRings():
            quotient_map = domain.quotient_map()
            return _ring_morphisms_equal(left * quotient_map, right * quotient_map)
        case _ if domain is _owned_integers():
            # A unital map out of Z is uniquely determined by 1.
            return True
        case _ if _is_finite_or_number_field(domain):
            # A map of fields fixes the prime field, so it is determined by its
            # values on the field generators over the prime field, finitely
            # many for a finite or a number field.
            return conjunction(
                left(generator) == right(generator)
                for generator in domain.field_generators()
            )
        case _ if domain.is_framed_algebra():
            labels = domain.algebra_generating_set()
            if not labels.cardinality().is_finite():
                return AtomicProposition("equal", left, right)
            on_generators = conjunction(
                left(domain.algebra_generator(label)) == right(domain.algebra_generator(label))
                for label in labels
            )
            if on_generators is False:
                return False
            structure_map = domain.algebra_structure_morphism()
            if structure_map.domain() is domain:
                return AtomicProposition("equal", left, right)
            return conjunction(
                (
                    on_generators,
                    _ring_morphisms_equal(left * structure_map, right * structure_map),
                )
            )
        case _:
            return _engine_ring_morphisms_equal(left, right)


def _engine_ring_morphisms_equal(left, right):
    r"""Compare two maps through their retained exact engine maps, else return the proposition ``equal(f, g)``.

    The identity retains no engine map; it equals an engine-backed map
    exactly when that engine map is the identity.
    """
    left_engine = left._engine_morphism
    right_engine = right._engine_morphism
    match (left_engine, right_engine):
        case (None, None) if left._preamble_is_identity and right._preamble_is_identity:
            return True
        case (None, None):
            return AtomicProposition("equal", left, right)
        case (None, _) if left._preamble_is_identity:
            return right._engine_is_identity()
        case (_, None) if right._preamble_is_identity:
            return left._engine_is_identity()
        case (None, _) | (_, None):
            return AtomicProposition("equal", left, right)
        case _:
            return bool(left_engine == right_engine)



class RingMor(CategoricalMor):
    r"""The owned set ``Hom_Ring(A,B)`` generated from semiring and rng Mors."""

    ElementMethods = RingMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def __call__(self, datum):
        return CategoricalMor.__call__(self, datum)

    def _from_engine_morphism(self, datum):
        return _ringlike_mor_from_engine(self, datum)

    def _element_constructor_(self, datum):
        return _ringlike_mor_element(self, datum, RingMorphism)

    def elementwise(self, function):
        if isinstance(function, Map):
            return self(function)
        return self.element_class(self, function)

    def _elementwise_with_engine(self, function, engine_morphism):
        return self.element_class(
            self, function, engine_morphism=engine_morphism
        )

    @object_level
    def identity(self):
        return _ringlike_mor_identity(self)

    def embeddings(self):
        r"""The elements of ``Mor(K, L)`` for fields ``K`` and ``L``, in the engine's deterministic order.

        Every ring map between fields is injective, so these are the
        embeddings of ``K`` into ``L``.
        """
        domain = self.domain()
        codomain = self.codomain()
        assert domain in OwnedFields() and codomain in OwnedFields(), (
            f"cannot enumerate the embeddings in {self}: embeddings are enumerated between fields, "
            f"but {domain} -> {codomain} is not a pair of fields"
        )
        return owned_sets.finite_ordered_set(tuple(
            self._from_engine_morphism(engine_embedding)
            for engine_embedding in _engine_ring(domain).embeddings(_engine_ring(codomain))
        ))

    def _repr_(self):
        return f"Mor_Ring({self.domain()}, {self.codomain()})"

class PredicateSubrings(OwnedCategory):
    def an_object(self):
        r"""The integers inside the rationals, cut out by integrality."""
        rationals = _owned_rationals()
        return rationals.predicate_subring(
            lambda element: element.denominator() == 1,
            "z is an integer",
        )

    def super_categories(self):
        return [OwnedRings()]

    class ParentMethods:
        def ambient_ring(self):
            return self._ambient_ring

        def defining_predicate(self):
            return self._predicate

        def _cardinality_decision(self):
            r"""Count the represented subring, or use its characteristic-zero injection.

            A decided predicate on a supplied finite ambient enumeration
            gives the exact finite count. A unital subring of a countably
            infinite characteristic-zero ring contains the integers, so it
            is countably infinite. Neither finite placement nor a missing
            characteristic computation supplies an enumeration or a value.
            """
            from sage_extensions.categories.sets.cardinals import aleph0, cardinal

            ambient = self.ambient_ring()
            ambient_size = ambient._cardinality_decision()
            if ambient_size is None:
                return super()._cardinality_decision()
            ambient_size = cardinal(ambient_size)
            if (ambient_size == cardinal(1)) is True:
                # The sole ambient point is both ring constants, retained
                # by the defining unital-subring datum.
                return cardinal(1)
            if not ambient_size.expression().is_normal_form():
                return None
            if ambient_size.is_finite():
                if ambient in owned_sets.EnumeratedSets():
                    points = ambient
                elif ambient not in LocalizationRings():
                    engine = ambient._selected_engine_ring()
                    if engine is None or engine is ambient:
                        return None
                    points = (
                        _owned_engine_element(ambient, point) for point in engine
                    )
                else:
                    return None
                count = 0
                for point in points:
                    member = self.defining_predicate()(point)
                    if member is True:
                        count += 1
                    elif member is not False:
                        return None
                return cardinal(count)
            if ambient_size.is_countably_infinite():
                characteristic = ambient._characteristic_decision()
                if characteristic is not None and (characteristic == 0) is True:
                    return aleph0
            return super()._cardinality_decision()

        def __contains__(self, element):
            from sage.structure.element import parent as element_parent

            if element_parent(element) is self:
                return True
            if element not in self._ambient_ring:
                return False
            candidate = self._ambient_ring(element)
            answer = self._predicate(candidate)
            assert answer is True or answer is False, (
                f"cannot decide whether {candidate} lies in {self}: the defining condition "
                f"'{self._description}' is undecided on it"
            )
            return answer

        def _element_constructor_(self, element):
            from sage.structure.element import parent as element_parent

            from sage_extensions.categories.modules.pure.modules import Modules

            source = element_parent(element)
            if source is self:
                return element
            if source is not self and source in Modules(self.base_ring()) and source.unformed_module() is self:
                return source._element_of_unformed_module(element)
            if element not in self._ambient_ring:
                raise ValueError(
                    f"{element} is not in {self}: it is not even an element of the ring {self._ambient_ring} "
                    "this subring lies in"
                )
            candidate = self._ambient_ring(element)
            if candidate not in self:
                raise ValueError(
                    f"{candidate} is not in {self}: it does not satisfy '{self._description}'"
                )
            return self.element_class(self, _engine_element(self._ambient_ring, candidate))

        def one(self):
            return self._one

        def zero(self):
            return self._zero

        def inclusion(self):
            return self.Mor(self._ambient_ring, category=OwnedRings())(self._element_in_larger_ring)

        def _repr_(self):
            return f"{{z in {self._ambient_ring} : {self._description}}}"


class LocalizationRings(OwnedCategory):
    r"""Commutative localizations carrying their selected source and submonoid."""

    def an_object(self):
        r"""The integers with 2 inverted."""
        return _owned_integers().localization(2)

    class ElementMethods(CommutativeRingElement):
        r"""A represented fraction ``a/s`` in ``S^{-1}R``."""

        def __init__(self, parent, numerator, denominator) -> None:
            self._numerator = parent.localization_source()(numerator)
            self._denominator = parent.localization_source()(denominator)
            super().__init__(parent)

        def numerator(self):
            return self._numerator

        def denominator(self):
            return self._denominator

        def _add_(self, other):
            return self.parent().fraction(
                self.numerator() * other.denominator() + other.numerator() * self.denominator(),
                self.denominator() * other.denominator(),
            )

        def _mul_(self, other):
            return self.parent().fraction(
                self.numerator() * other.numerator(),
                self.denominator() * other.denominator(),
            )

        def _unit_inverse_decision(self):
            r"""Return the inverse ``s/a`` of a unit ``a/s``.

            ``a/s`` is a unit exactly when ``(a)`` meets ``S``, that is when
            ``a`` lies in the saturation of ``S``; the denominators admitted by
            :meth:`fraction` are that saturation, so ``s/a`` is a fraction of
            this ring and ``(a/s)(s/a) = 1``.
            """
            parent = self.parent()
            match self.is_unit():
                case True:
                    return parent.fraction(self.denominator(), self.numerator())
                case False:
                    raise ZeroDivisionError(f"{self} is not a unit of {parent}")
                case _:
                    return None

        def _unit_decision(self):
            r"""Return whether ``a/s`` is invertible in ``S^{-1}R``.

            The denominator is already a unit, so ``a/s`` is a unit exactly
            when ``a`` is an admissible denominator. Both questions therefore
            use the same source-ring predicate: ``(a)`` meets ``S``. A
            computation model may invert more elements and cannot decide
            this predicate merely by its own unit test.
            """
            return self.parent()._valid_denominator(self.numerator())

        __truediv__ = Monoids.ElementMethods.divide_by_unit

        def _neg_(self):
            return self.parent().fraction(
                -self.numerator(),
                self.denominator(),
            )

        def equality_status(self, other):
            if element_parent(other) is not self.parent():
                return False
            return self.parent()._fraction_equality_status(self, other)

        def _richcmp_(self, other, op):
            if op not in (op_EQ, op_NE):
                return NotImplemented
            status = self.equality_status(other)
            match status:
                case _ if status in Propositions:
                    return status if op == op_EQ else negation(status)
                case _:
                    return status if op == op_EQ else not bool(status)

        def _repr_(self):
            if (self.denominator() == self.parent().localization_source().one()) is True:
                return repr(self.numerator())
            return f"({self.numerator()})/({self.denominator()})"

    def super_categories(self):
        from sage_extensions.categories.group.magmas import AdditiveGroups

        return [OwnedRings().Commutative(), AdditiveGroups().AdditiveCommutative()]

    class Local(CategoryWithAxiom):
        r"""Local rings retaining their selected localization source and submonoid."""

        def an_object(self):
            r"""The localization of the integers at all nonzero elements."""
            return _owned_integers().fraction_field_localization()

        class ParentMethods:
            @cached_method
            def source_residue_map(self):
                r"""Return ``R -> kappa(m)`` through this local localization ``S^-1 R``."""
                return self.residue_map() * self.localization_map()

    class ParentMethods:
        _derived_construction_parameters = frozenset({"base_ring"})

        def base_ring(self):
            r"""The retained scalar base of this localization as a ring object.

            Localization category placement can be deferred until its native
            regular module is installed. In that phase the algebra category
            that normally supplies ``base_ring`` is deliberately absent, so
            derive the same value from the retained source algebra instead of
            accidentally treating the localization as an algebra over itself.
            A source with no selected scalar algebra remains self-based.
            """
            algebra_source = getattr(self, "algebra_source", None)
            if algebra_source is not None:
                return algebra_source.base_ring()
            return self

        def _cardinality_decision(self):
            r"""Supply the cardinality for a zero source or an integral-domain source.

            If ``0 in S`` then ``S^-1 R`` is the zero ring.  Otherwise the
            canonical map ``R -> S^-1 R`` is injective. A finite domain is a
            field, so every element of ``S`` is already a unit and this map
            is an isomorphism. For infinite ``R``, fraction representatives
            give ``|S^-1 R| <= |R x S| <= |R x R| = |R|``. Thus either case
            gives ``|S^-1 R| = |R|``.
            """
            source = self.localization_source()
            if (source.one() == source.zero()) is True:
                from sage_extensions.categories.sets.cardinals import (
                    Cardinalities,
                )

                return Cardinalities().one()
            match source in OwnedIntegralDomains():
                case True:
                    from sage_extensions.categories.rings.commutative_algebra import (
                        _submonoid_contains_zero_in_domain,
                    )
                    from sage_extensions.categories.sets.cardinals import (
                        Cardinalities,
                    )

                    contains_zero = _submonoid_contains_zero_in_domain(
                        source,
                        self.localization_submonoid(),
                    )
                    match contains_zero:
                        case False:
                            return source._cardinality_decision()
                        case True:
                            return Cardinalities().one()
                        case _:
                            return super()._cardinality_decision()
                case False:
                    return super()._cardinality_decision()

        def _source_is_polynomial_ring_over_field(self):
            r"""Whether the localized ring is a symmetric algebra ``Sym(V)`` over a field."""
            from sage_extensions.categories.algebras.free_algebras import SymmetricAlgebras

            ring = self.localization_source()
            base = ring.base_ring()
            return base in OwnedFields() and ring in SymmetricAlgebras(base)

        def _inverts_only_monomial_terms(self):
            r"""Whether ``S`` is generated by terms ``c x^a`` of a polynomial ring over a field."""
            ring = self.localization_source()
            return self._source_is_polynomial_ring_over_field() and all(
                _monomial_term_variables(ring, element) is not None
                for element in self.inverted_elements()
            )

        def inverted_submonoid_meets(self, ideal):
            r"""Decide ``I intersect S != empty`` for this localization ``S^-1 R``.

            For a prime complement this means a generator of I lies outside
            the prime.  For the nonzero elements of a domain it means I is
            nonzero.  For finitely generated S, putting f equal to the product
            of its generators gives I intersect S nonempty exactly when
            ``1 in I : f^infinity``: every monomial in these generators divides
            a sufficiently large power of f, and f itself belongs to S.
            """
            from sage.misc.misc_c import prod

            from sage_extensions.categories.rings.commutative_algebra import (
                PrimeLocalizations,
            )

            ring = self.localization_source()
            match self:
                case _ if self in PrimeLocalizations():
                    prime = self.localized_prime()
                    return negation(conjunction(
                        prime.contains_ambient_element(generator)
                        for generator in ideal.ideal_generators()
                    ))
                case _ if self._has_selected_nonzero_element_submonoid():
                    return negation(conjunction(
                        generator == ring.zero()
                        for generator in ideal.ideal_generators()
                    ))
                case _:
                    if self.localization_submonoid()._selected_representation_kind() != "generators":
                        return AtomicProposition("inverted_submonoid_meets", self, ideal)
                    element = prod(self.inverted_elements(), ring.one())
                    match tuple(ideal.ideal_generators()):
                        case (generator,) if self._inverts_only_monomial_terms():
                            # The variables are primes of K[x_1..x_n], so the
                            # divisors of a monomial are its submonomials up to a
                            # unit: (d) meets S iff d is a term c x^a whose
                            # variables all divide f.
                            support = _monomial_term_variables(ring, generator)
                            if support is None:
                                return False
                            return support <= _monomial_term_variables(ring, element)
                        case (generator,) if self._source_is_polynomial_ring_over_field():
                            # K[x_1..x_n] is factorial (Lang, Algebra, IV.2.3), and a
                            # prime factor of d occurs in d at most deg(d) times, so
                            # some monomial in S lies in (d) iff d | f^deg(d).
                            if (generator == ring.zero()) is True:
                                return False
                            return generator.divides(element ** generator.degree())
                        case _:
                            pass
                    saturated = ideal._ideal_saturation_decision(ring.ideal(element))
                    if saturated is None:
                        return AtomicProposition("inverted_submonoid_meets", self, ideal)
                    return saturated.contains_ambient_element(ring.one())

        def __init__(
            self,
            source,
            submonoid,
            _engine_ring=None,
            _engine_source_decoder=None,
            _engine_source_encoder=None,
            *,
            algebra_source=None,
            **rest,
        ) -> None:
            self._localization_source = source
            self._localization_submonoid = submonoid
            self._localization_engine_source_decoder = _engine_source_decoder
            self._localization_engine_source_encoder = _engine_source_encoder
            self._preamble_engine_ring = _engine_ring
            from sage_extensions.categories.algebras.algebras import Algebras
            from sage_extensions.owned_category import owned_category_join

            coefficient_base = (
                algebra_source.base_ring()
                if algebra_source is not None
                else source.base_ring()
            )
            algebra = (
                Algebras(coefficient_base)
                .Associative()
                .Unital()
                .Commutative()
            )
            rest["category"] = owned_category_join((rest["category"], algebra))
            super().__init__(
                base_ring=coefficient_base,
                _engine_product=lambda left, right: LocalizationRings.ElementMethods._mul_(left, right),
                _engine_scalar_action=lambda scalar, element: LocalizationRings.ElementMethods._mul_(self(scalar), self(element)),
                _engine_unit=lambda algebra: LocalizationRings.ParentMethods.one(algebra),
                **rest,
            )

        def _selected_engine_ring(self):
            r"""Return this localization's retained private realization, or ``None``.

            The element arithmetic of this category asks for this realization
            to compute the inverse of a unit whose membership in the actual
            localization has been established. The realization itself need
            not reflect the unit predicate. The inherited ring-realization
            contract also permits optional cardinality and selected-presentation
            computation suppliers to retain absence. The required
            ``_engine_ring`` dispatcher asserts at that boundary. This
            model may be larger than the actual localization; it supplies
            no replacement for the source/submonoid mathematics.
            """
            return self._preamble_engine_ring

        @cached_method
        def localization_functor(self):
            r"""Return the canonical module-localization functor along this ring localization."""
            from sage_extensions.categories.functors.module_localization import (
                ModuleLocalizationFunctor,
            )

            return ModuleLocalizationFunctor(self)

        def localize_module(self, module):
            r"""Return ``S^{-1}M`` through this localization's canonical functor."""

            if module.base_ring() is not self.localization_source():
                raise ValueError(
                    f"cannot localize {module} at {self}: it is a module over {module.base_ring()}, but the "
                    f"localization is of {self.localization_source()}"
                )
            return self.localization_functor()(module)

        @cached_method
        def _normalization_data(self):
            r"""Transport a retained finite normalization to this localization.

            The selected computation currently requires finitely many
            inverted elements, an ordered finite component family, a chosen finite
            normalization-module presentation over the source, and decided
            component-survival tests. It retains the source localization,
            actual component maps, and the localized unit and cokernel.
            No finite normalization is inferred for an arbitrary source.
            """
            from sage_extensions.categories.modules.pure.modules import (
                ModulesWithChosenFinitePresentation,
            )
            from sage_extensions.categories.rings.commutative_algebra import (
                _localized_affine_normalization_data,
            )
            from sage_extensions.categories.sets.finite_ordered_sets import FiniteOrderedSets

            if self.localization_submonoid()._selected_representation_kind() != "generators":
                return None
            source = self.localization_source()
            data = source._normalization_data()
            if data is None:
                return None
            if (data.normalization_module in ModulesWithChosenFinitePresentation(source)) is not True:
                return None
            if (data.components.index_set() in FiniteOrderedSets()) is not True:
                return None
            return _localized_affine_normalization_data(self, data)

        def _normality_decision(self):
            r"""Read normality when the retained finite normalization is localized."""
            data = self._normalization_data()
            if data is not None:
                return data.is_normal
            return super()._normality_decision()

        def _valid_denominator(self, denominator):
            r"""Return whether the source element becomes a unit, without forcing a predicate.

            Private localization-owner contract. Fraction construction,
            represented membership, and the numerator unit predicate call
            this with an element of the actual source ring. The result is
            ``True``, ``False``, or an owned proposition. A source unit or a
            proved member of ``S`` is sufficient; the general criterion is
            ``(denominator) intersect S != empty``. Predicate membership alone
            need not decide membership in the saturation of ``S``.
            """
            source = self.localization_source()
            if (denominator == source.one()) is True:
                return True
            if (denominator == -source.one()) is True:
                return True
            submonoid = self.localization_submonoid()
            structure = submonoid._structure_data()
            match structure.get("kind"):
                case "prime_complement":
                    prime = structure["prime_ideal"]
                    return negation(prime.contains_ambient_element(denominator))
                case "nonzero_elements":
                    return negation(denominator == source.zero())
                case _:
                    pass
            if submonoid._selected_representation_kind() == "predicate":
                if submonoid.defining_predicate()(denominator) is True:
                    return True
                return AtomicProposition("is_unit", self.fraction(denominator))
            if any((denominator == generator) is True for generator in submonoid.monoid_generators()):
                return True
            return self.inverted_submonoid_meets(source.ideal(denominator))

        def fraction(self, numerator, denominator=None):
            r"""Construct ``a/s`` after admitting ``s`` through the selected submonoid.

            Arithmetic and private engine crossings use this same constructor.
            There is no trusted spelling that can manufacture a localization
            element with a denominator outside the represented saturation of
            the selected multiplicative system.
            """
            source = self.localization_source()
            numerator = source(numerator)
            denominator = source.one() if denominator is None else source(denominator)
            match self._valid_denominator(denominator):
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"cannot use {denominator} as a denominator in {self}: its image does not become a unit"
                    )
                case _:
                    raise ValueError(
                        f"cannot use {denominator} as a denominator in {self}: it is not known whether its image "
                        "becomes a unit"
                    )
            return self.element_class(self, numerator, denominator)

        def _element_constructor_(self, value):
            from sage.structure.element import parent as element_parent

            from sage_extensions.categories.modules.pure.modules import Modules

            source = element_parent(value)
            if source is not self and source in Modules(self.base_ring()) and source.unformed_module() is self:
                return source._element_of_unformed_module(value)
            if source is self:
                return value
            if isinstance(value, tuple) and len(value) == 2:
                return self.fraction(value[0], value[1])
            return self.fraction(value)

        def __call__(self, value):
            return self._element_constructor_(value)

        def is_parent_of(self, value):
            r"""Return the owned membership predicate in the represented localization.

            A pair requests its stated numerator and denominator. For a value
            of the actual ``Frac(R)``, an exact source presentation ``a/b``
            is checked through the canonical map ``R -> Frac(R)``. It belongs
            to ``S^-1 R`` exactly when ``a`` lies in ``S^-1(b)``, equivalently
            when ``((b):(a))`` meets ``S``. This does not require the stated
            ``b`` itself to become a unit and does not select a new denominator
            witness. The constructor ``fraction(a, b)`` still requires its
            stated denominator to be admitted. The membership computation is the existing
            localized-ideal membership operation, which retains an undecided
            proposition when the source ideal computation is unavailable.

            This selected route uses the existing fraction-field and canonical
            map computations of ``R``; their construction frontier remains.
            Unrecognized endpoints and undecided comparisons return the
            actual membership proposition of this localization.
            A larger computation field alone gives no membership answer.
            """
            from sage_extensions.categories.modules.pure.modules import Modules

            parent = element_parent(value)
            if parent is self:
                return True
            if (
                isinstance(parent, Parent)
                and parent in Modules(self.base_ring())
                and parent.unformed_module() is self
            ):
                return True
            source = self.localization_source()
            if isinstance(value, tuple) and len(value) == 2:
                numerator, denominator = value
                numerator_status = source.is_parent_of(numerator)
                denominator_status = source.is_parent_of(denominator)
                if numerator_status is False or denominator_status is False:
                    return False
                if numerator_status is not True or denominator_status is not True:
                    return AtomicProposition("is_parent_of", self, value)
                return self._valid_denominator(source(denominator))
            source_status = source.is_parent_of(value)
            if source_status is True:
                return True
            if not isinstance(parent, Parent) or parent not in OwnedRings():
                if source_status is False:
                    return False
                return AtomicProposition("is_parent_of", self, value)
            if (
                source not in OwnedIntegralDomains()
                or parent is not source.fraction_field()
            ):
                return AtomicProposition("is_parent_of", self, value)
            numerator = value.numerator()
            denominator = value.denominator()
            if (
                source.is_parent_of(numerator) is not True
                or source.is_parent_of(denominator) is not True
            ):
                return AtomicProposition("is_parent_of", self, value)
            numerator = source(numerator)
            denominator = source(denominator)
            if (denominator == source.zero()) is not False:
                return AtomicProposition("is_parent_of", self, value)
            comparison = source.fraction_field_map()
            if (comparison(numerator) == value * comparison(denominator)) is not True:
                return AtomicProposition("is_parent_of", self, value)
            return source.ideal(denominator).extension_to_localization(
                self
            ).contains_ambient_element(self.localization_map()(numerator))

        def __contains__(self, value):
            r"""Use the owned membership predicate at Python's Boolean boundary."""
            return self.is_parent_of(value)

        def _inverse_variable_engine_cover(self):
            r"""Return the current cover admitted by the inverse-variable decoder.

            Private localization-owner contract. The only callers are this
            owner's element decoder and exact-coefficient capability check.
            The source, inverted family and native engine are fixed defining
            data. Return the engine's cover when its variables consist of
            the source variables followed by the represented inverses;
            ``None`` means that this particular crossing is not selected.
            Other existing element-decoder cases remain available.
            """
            engine = self._preamble_engine_ring
            if not isinstance(engine, QuotientRing_generic):
                return None
            source_engine = _engine_ring(self.localization_source())
            if not (
                isinstance(source_engine, QuotientRing_generic)
                or self._localization_engine_source_encoder is not None
            ):
                return None
            engine_cover = engine.cover_ring()
            source_cover = (
                source_engine.cover_ring()
                if isinstance(source_engine, QuotientRing_generic)
                else source_engine
            )
            source_names = tuple(source_cover.variable_names())
            inverted = tuple(self.inverted_elements())
            engine_names = tuple(engine_cover.variable_names())
            if (
                engine_names[: len(source_names)] == source_names
                and len(engine_names) == len(source_names) + len(inverted)
                and all(
                    name.startswith("localization_inverse_")
                    for name in engine_names[len(source_names) :]
                )
            ):
                return engine_cover
            return None

        def _inverse_of_bottom_numerator(self, generator):
            r"""The inverse ``1/m`` of the bottom numerator ``m`` of a generator ``g``.

            Private decoder contract for the inverse-variable realization.  In
            a tower ``L_k -> ... -> L_0`` write ``g = n_1/d_1`` with
            ``n_1, d_1`` in ``L_{k-1}``, then ``n_1 = n_2/d_2`` one level down,
            and so on to ``m`` in the bottom ring.  Then ``g = m e`` with
            ``e = (...(1/d_j).../d_2)/d_1`` a unit of the source, and the
            auxiliary variable inverting ``m`` is ``e/g`` here.  For a one-step
            localization ``m = g`` and ``e = 1``.
            """
            from sage_extensions.categories.rings.commutative_algebra import (
                PrimeLocalizations,
            )

            def numerator_and_unit(ring, element):
                if ring not in LocalizationRings() or ring in PrimeLocalizations():
                    return ring.one()
                numerator, denominator = ring.localization_fraction_data(element)
                return ring.fraction(
                    numerator_and_unit(ring.localization_source(), numerator),
                    denominator,
                )

            source = self.localization_source()
            return self.fraction(numerator_and_unit(source, generator), generator)

        def _from_engine_element(self, value):
            engine = self._preamble_engine_ring
            assert engine is not None, (
                f"cannot convert {value} into the localization {self}: it has no computer-algebra model"
            )
            represented = engine(value)
            source = self.localization_source()
            source_engine = _engine_ring(source)
            decoder = self._localization_engine_source_decoder
            if decoder is not None:
                return self.fraction(
                    decoder(represented.numerator()),
                    decoder(represented.denominator()),
                )

            # A localization of a quotient is realized privately by the
            # standard finite presentation
            # ``P[u_i]/(I, u_i f_i - 1)``.  Decode a polynomial representative
            # by sending the original variables through ``P -> P/I`` and each
            # auxiliary variable to the represented inverse of its selected
            # denominator.  This is exactly the universal localization map.
            if self._inverse_variable_engine_cover() is not None:
                source_cover = (
                    source_engine.cover_ring()
                    if isinstance(source_engine, QuotientRing_generic)
                    else source_engine
                )
                source_names = tuple(source_cover.variable_names())
                inverses = tuple(
                    self._inverse_of_bottom_numerator(generator)
                    for generator in self.inverted_elements()
                )
                result = self.zero()
                for exponents, coefficient in represented.lift().dict().items():
                    source_monomial = source_cover(coefficient)
                    for position, exponent in enumerate(exponents[: len(source_names)]):
                        source_monomial *= source_cover.gen(position) ** int(exponent)
                    term = self.fraction(
                        _owned_engine_element(source, source_engine(source_monomial))
                    )
                    for position, exponent in enumerate(exponents[len(source_names) :]):
                        if exponent:
                            term *= inverses[position] ** int(exponent)
                    result += term
                return result
            return self.fraction(
                _owned_engine_element(source, source_engine(represented.numerator())),
                _owned_engine_element(source, source_engine(represented.denominator())),
            )

        def _engine_element(self, value):
            engine = self._preamble_engine_ring
            assert engine is not None, (
                f"cannot compute with {value} in the localization {self}: it has no computer-algebra model"
            )
            element = self(value)
            encoder = self._localization_engine_source_encoder
            if encoder is not None:
                return encoder(element.numerator()) / encoder(element.denominator())
            numerator = _engine_element(self.localization_source(), element.numerator())
            denominator = _engine_element(self.localization_source(), element.denominator())
            source_engine = _engine_ring(self.localization_source())
            source_map = engine.coerce_map_from(source_engine)
            if source_map is not None:
                return source_map(numerator) / source_map(denominator)
            from sage_extensions.categories.rings.commutative_algebra import (
                QuotientRings,
            )

            assert self.localization_source() in QuotientRings(), (
                "a localization engine without a source coercion is represented here "
                "only for a quotient source with canonical polynomial lifts"
            )
            return engine(numerator.lift()) / engine(denominator.lift())

        def _has_selected_exact_coefficient_presentation(self) -> bool:
            r"""Whether the current inverse-variable quotient is an exact cover.

            This implements the inherited ring-owner contract for module
            algorithms. Only a finite-generator localization using its
            admitted polynomial quotient crossing and source encoding is
            selected. For ``L=S^-1(P/I)``, the existing realization is
            ``P[u]/(I,u_i f_i-1)``. Its descent sends ``u_i`` to ``1/f_i``;
            descent after the selected coefficient lift is the identity of L.
            Prime and fraction-field models, flattened localization towers,
            decoder overrides and all-unit source-engine reuse do not supply
            this capability. Their existing element crossings are unchanged.
            """
            from sage_extensions.categories.rings.commutative_algebra import (
                QuotientRings,
            )

            if self.localization_submonoid()._selected_representation_kind() != "generators":
                return False
            source = self.localization_source()
            if (
                source in LocalizationRings()
                or self._localization_engine_source_decoder is not None
                or (
                    source not in QuotientRings()
                    and self._localization_engine_source_encoder is None
                )
            ):
                return False
            cover = self._inverse_variable_engine_cover()
            return (
                isinstance(cover, (MPolynomialRing_base, PolynomialRing_generic))
                and self._preamble_engine_ring is not _engine_ring(source)
            )

        def _exact_coefficient_presentation_ring(self):
            if self._has_selected_exact_coefficient_presentation():
                engine_cover = self._preamble_engine_ring.cover_ring()
                # This selected localization backend is a flattened
                # polynomial cover. Its owned presentation is determined by
                # the retained coefficient ring and ordered variable labels;
                # do not adopt the auxiliary Sage parent as a second ring.
                return _own_ring(engine_cover.base_ring()).polynomial_ring(
                    tuple(engine_cover.variable_names())
                )
            return super()._exact_coefficient_presentation_ring()

        def _exact_coefficient_presentation_relations(self):
            if self._has_selected_exact_coefficient_presentation():
                cover = self._exact_coefficient_presentation_ring()
                return owned_sets.finite_ordered_set(tuple(
                    _owned_engine_element(cover, relation)
                    for relation in self._preamble_engine_ring.defining_ideal().gens()
                ))
            return super()._exact_coefficient_presentation_relations()

        def _lift_coefficient_to_presentation(self, value):
            if self._has_selected_exact_coefficient_presentation():
                cover = self._exact_coefficient_presentation_ring()
                represented = self._preamble_engine_ring(self._engine_element(value))
                return _owned_engine_element(cover, represented.lift())
            return super()._lift_coefficient_to_presentation(value)

        def _descend_coefficient_from_presentation(self, value):
            if self._has_selected_exact_coefficient_presentation():
                cover = self._exact_coefficient_presentation_ring()
                represented = self._preamble_engine_ring(_engine_element(cover, value))
                return self._from_engine_element(represented)
            return super()._descend_coefficient_from_presentation(value)

        def zero(self):
            return self.fraction(self.localization_source().zero())

        def one(self):
            return self.fraction(self.localization_source().one())

        def _fraction_equality_status(self, left, right):
            r"""Compare ring fractions through localization of the actual regular module.

            The rank-one source coordinate sends ``a/s`` to ``(a*1_R)/s``
            in ``S^-1(R.regular_module())``. This preserves and reflects
            equality. The module-localization owner supplies annihilator,
            finite-orbit, and free-coordinate computations and retains any
            undecided proposition. Both images use its ordinary fraction
            constructor, including denominator admission.
            """
            source = self.localization_source()
            left_product = left.numerator() * right.denominator()
            right_product = right.numerator() * left.denominator()
            # Use the owned additive operations rather than Python subtraction.
            # In particular, represented quotient classes implement addition and
            # negation directly, while Sage's inherited binary-subtraction
            # dispatch need not recognize their common owned parent.
            difference = source(left_product + (-right_product))
            if (difference == source.zero()) is True:
                return True
            if source in OwnedIntegralDomains():
                # In a domain, a/s = b/t exactly when u(at - bs) = 0 for some u
                # in S (Mathlib IsLocalization.eq_iff_exists,
                # Localization/Defs.lean), so exactly when at = bs or 0 lies in
                # S.  A product of nonzero elements is nonzero, so 0 lies in a
                # monoid generated by a set only when a generator is 0.
                submonoid = self.localization_submonoid()
                match submonoid._structure_data().get("kind"), submonoid._selected_representation_kind():
                    case "nonzero_elements" | "prime_complement", _:
                        return difference == source.zero()
                    case _, "predicate":
                        return submonoid.defining_predicate()(source.zero())
                    case _:
                        return any(
                            (generator == source.zero()) is True
                            for generator in submonoid.monoid_generators()
                        )
            regular = source.regular_module()
            (label,) = tuple(regular.module_generating_set())
            generator = regular.module_generator(label)
            localized = self.localization_functor()(regular)
            left_image = localized.fraction(
                regular.scalar_multiple(left.numerator(), generator),
                left.denominator(),
            )
            right_image = localized.fraction(
                regular.scalar_multiple(right.numerator(), generator),
                right.denominator(),
            )
            return left_image.equality_status(right_image)

        def _repr_(self):
            # (R-{0})^-1 R is Frac(R), and is named as the fraction field.
            source = self.localization_source()
            submonoid = self.localization_submonoid()
            match submonoid._structure_data().get("kind"):
                case "nonzero_elements":
                    return f"Fraction Field of {source}"
                case _:
                    return f"Localization of {source} at {submonoid}"

        def localization_source(self):
            return self._localization_source

        def localization_submonoid(self):
            return self._localization_submonoid

        def _field_decision(self):
            r"""Inverting finitely many elements of a finite free ZZ-algebra gives no field.

            Finite generation as a ZZ-module supplies finite generation as a
            ZZ-algebra, and adjoining finitely many inverses preserves finite
            type. If the localization is nonzero, torsion-freeness over ZZ
            makes its canonical ZZ map injective: an equation ``n/1 = 0`` for
            nonzero n would give ``n*s = 0`` for some s in the submonoid,
            forcing s = 0 and hence the zero localization. But a field of
            finite type over the Jacobson domain ZZ cannot contain ZZ
            (Stacks, 00G4 and 0CY7). The zero localization is not a field either.

            This uses the source's finite-free property and the selected
            finite generating presentation of the submonoid. It selects no
            basis, computes no rank, and does not read the possibly larger
            ring computation model. Other cases keep the inherited predicate.
            """
            from sage_extensions.categories.modules.pure.modules import Modules

            if (
                self.localization_submonoid()._selected_representation_kind() == "generators"
                and self.localization_source() in Modules(_owned_integers()).Free().FinitelyGenerated()
            ):
                return False
            return super()._field_decision()

        def is_fraction_field_localization(self):
            r"""Whether the canonical localization realizes its source's fraction field.

            A localization of a domain is its fraction field exactly when it
            is a field. In that case its nonzero source elements stay nonzero
            and become invertible, and every target element is a source
            fraction. The chosen submonoid need not be presented as all the
            nonzero elements: localizing a domain at its zero prime has the
            same property. Undecided domain or field predicates are retained.

            This mathematical predicate does not supply the separate selected
            realization used by the fraction-field comparison methods.
            """
            source_is_domain = self.localization_source().is_integral_domain()
            if source_is_domain is False:
                return False
            return conjunction((source_is_domain, self.is_field()))

        def _has_selected_nonzero_element_submonoid(self) -> bool:
            r"""Return whether the selected submonoid is the nonzero elements.

            Owner: LocalizationRings.ParentMethods. Permitted callers are
            this owner's submonoid-intersection and fraction-field realization
            and comparison methods, and the CommutativeIdeals contraction
            adapter. The input is this exact owned localization. The Boolean
            result reads its retained construction tag: True supplies the
            selected nonzero-element submonoid of its domain source; False
            says only that this presentation was not selected. It neither
            decides the mathematical fraction-field predicate nor supplies
            an absent computation realization.
            """
            return (
                self.localization_submonoid()._structure_data().get("kind")
                == "nonzero_elements"
            )

        def inverted_elements(self):
            return self.localization_submonoid().monoid_generators()

        def inverted_element(self):
            r"""Return the selected singleton generator ``f`` of this localization.

            Every element of ``R[1/f]`` admits an expression ``a/f^n``.
            Its stored fraction may use any denominator whose image is a unit,
            however: in ``ZZ[1/6]``, the represented denominator of ``1/2``
            need not be a power of ``6``. This accessor selects no rewriting
            or exponent. A localization at several selected generators can
            also be presented by their product, but this accessor does not
            replace that family with a new singleton generator.
            """
            inverted = self.inverted_elements()
            match inverted.cardinality() == 1:
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"{self} inverts {inverted.cardinality()} elements, but the inverted element is defined only "
                        "for a localization R[1/f] at a single element f"
                    )
            return inverted[0]

        @cached_method(key=lambda self, source_ring: id(source_ring))
        def principal_localization_comparison(self, source_ring):
            r"""Compare a finite localization tower with ``source_ring[1/f]``.

            Every layer must retain a finite family of inverted elements.
            In a principal localization, ``a/s`` is associated to ``a``;
            localizing at it therefore adds its numerator to the product
            inverted in the original source. Both inverse maps come from
            localization's universal property. Reference: Mathlib,
            ``IsLocalization.Away.mul'`` and ``Away.mul_of_associated`` in
            ``Mathlib/RingTheory/Localization/Away/Basic.lean``.

            Unexecuted iterated-localization specimen::

                sage: from dzack_research.preamble.all import *
                sage: A = QQ['x']; x = A.algebra_generator('x')
                sage: B = A.localization(x)
                sage: C = B.localization(B(A.one()-x))
                sage: comparison = C.principal_localization_comparison(A)
                sage: comparison.codomain() is A.localization(x*(A.one()-x))
                True
                sage: element = C.fraction(B.one(), B(A.one()-x))
                sage: comparison.inverse()(comparison(element)) == element
                True
            """
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _isomorphism_from_known_inverse_pair,
            )

            layers = []
            current = self
            while current is not source_ring:
                if current not in LocalizationRings():
                    raise ValueError("the requested source is not an ancestor in this localization tower")
                layers.append(current)
                current = current.localization_source()
            product = source_ring.one()
            flattened = source_ring
            forward = source_ring.Mor(source_ring).identity()
            reverse = forward
            source_map = forward
            for layer in reversed(layers):
                generators = layer.inverted_elements()
                assert generators.cardinality().is_finite() is True, (
                    "a principal localization comparison requires finite chosen generator families"
                )
                for generator in generators:
                    value = forward(generator)
                    numerator = value if flattened is source_ring else flattened.localization_fraction_data(value)[0]
                    product *= numerator
                target = source_ring.localization(product)
                to_target = target.localization_map()
                if flattened is not source_ring:
                    to_target = flattened.induced_morphism(to_target)
                forward = layer.induced_morphism(to_target * forward)
                source_map = layer.localization_map() * source_map
                reverse = target.induced_morphism(source_map)
                flattened = target
            return _isomorphism_from_known_inverse_pair(
                forward, reverse, base_category=OwnedRings().Commutative(),
            )

        def quotient_contraction_map(self, quotient):
            r"""The canonical injection R/I -> (S^-1 R)/J, with I contracted from J.

            The exact selected quotient must have this localization as its
            source. Extension of its contracted ideal is J (Stacks, 02C9),
            and quotient commutes with localization (00CT). Hence this map
            is injective and presents the target as a localization of its
            retained domain. It need not be an isomorphism.

            Contraction is computed when this construction is requested;
            neither the source localization nor the quotient is reconstructed.
            """
            morphism = self._quotient_contraction_map_decision(quotient)
            assert morphism is not None, (
                "the canonical contraction map requires an exact source-ideal contraction in the selected representation"
            )
            return morphism

        @cached_method
        def _quotient_contraction_map_decision(self, quotient):
            r"""Protected canonical-map result, or None at the computation frontier.

            Owner: LocalizationRings.ParentMethods. Permitted callers are
            quotient_contraction_map, this owner's finite comparison, and
            the QuotientRings finiteness hook. The input is an exact quotient
            of this localization. The output is the canonical owned ring
            arrow from its contracted source quotient to that same input,
            or None when the ideal owner has no selected contraction result.
            """
            from sage_extensions.categories.rings.commutative_algebra import QuotientRings

            if quotient not in QuotientRings() or quotient.quotient_source() is not self:
                raise ValueError(
                    f"the contraction comparison from {self} requires its exact selected quotient, not {quotient}"
                )
            contracted = quotient.defining_ideal()._localization_contraction_decision()
            if contracted is None:
                return None
            source_quotient = contracted.quotient_ring()
            localization_map = self.localization_map()
            quotient_map = quotient.quotient_map()

            def image(element):
                return quotient_map(localization_map(source_quotient(element).lift()))

            return OwnedRings().Mor(source_quotient, quotient)(image)

        @cached_method
        def _finite_quotient_contraction_isomorphism(self, quotient):
            r"""Protected exact finite comparison, or None when it is unavailable.

            Owner: LocalizationRings.ParentMethods. The permitted callers
            are quotient_contraction_isomorphism and the QuotientRings finite
            computation adapters. The input is an owned quotient with this
            exact localization as source. The result is an owned ring-core
            isomorphism from quotient_contraction_map(quotient).domain() to
            that exact quotient, retaining the same forward arrow.

            The contraction is S-saturated, so multiplication by each image
            of S is injective on the contracted quotient B. When B is finite
            as a set, multiplication is surjective, hence that image is a
            unit. The inverse sends the class of a/s to [a] [s]^-1. No
            enumeration or property of the target quotient is used to prove
            this. Finiteness alone does not supply a computation engine.
            """
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                _isomorphism_from_known_inverse_pair,
            )

            forward = self._quotient_contraction_map_decision(quotient)
            if forward is None:
                return None
            source_quotient = forward.domain()
            if source_quotient.is_finite() is not True:
                return None
            source_projection = source_quotient.quotient_map()
            zero_quotient = (source_quotient.one() == source_quotient.zero()) is True

            def inverse_image(element):
                if zero_quotient:
                    return source_quotient.zero()
                numerator, denominator = self.localization_fraction_data(
                    quotient(element).lift()
                )
                return source_projection(numerator) * source_projection(
                    denominator
                ).inverse_of_unit()

            inverse = OwnedRings().Mor(quotient, source_quotient)(inverse_image)
            return _isomorphism_from_known_inverse_pair(
                forward, inverse, base_category=OwnedRings()
            )

        def quotient_contraction_isomorphism(self, quotient):
            r"""Return the retained ring isomorphism when the contracted quotient is finite.

            The canonical injection is invertible precisely when its domain
            already inverts S. Finite cardinality proves this sufficient case;
            an unavailable finite computation is not proof that the map is
            noninvertible for an infinite domain.
            """
            comparison = self._finite_quotient_contraction_isomorphism(quotient)
            assert comparison is not None, (
                "the selected contraction-isomorphism computation requires a contracted quotient known to be finite"
            )
            return comparison

        def induced_morphism(self, morphism):
            r"""Return the unique ``S^{-1}R -> T`` extending ``g: R -> T``.

            The hypothesis is that ``g`` carries every element of ``S`` to a
            unit. For a selected generating family it suffices to establish
            that hypothesis on its generators. A predicate presentation of
            ``S`` supplies no such family or general unit-image decision.

            Retained canonical data also establish concrete predicate cases:
            this localization's own map induces its identity; a quotient map
            ``R -> R/p`` induces ``R_p -> R/p`` when that quotient is a field;
            and canonical maps between prime localizations use their existing
            prime-containment construction. Every map to the zero ring
            carries all of ``S`` to units. Other predicate cases require a
            selected proof of the global unit-image hypothesis.

            Once that hypothesis is established, the unique arrow sends
            ``a/s`` to ``g(a)g(s)^-1``. This is independent of the represented
            fraction. Merely attempting inverses at encountered denominators
            would not establish the existence of that ring arrow.
            """
            from sage_extensions.categories.rings.commutative_algebra import (
                QuotientRings,
            )

            source = self.localization_source()
            match morphism.domain() is source:
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"a map out of {self} is induced from a ring morphism out of {source}, but {morphism} starts "
                        f"at {morphism.domain()}"
                    )

            target = morphism.codomain()
            if target is self and morphism is self.localization_map():
                return OwnedRings().Mor(self, self).identity()
            if (target.one() == target.zero()) is True:
                return self._induced_morphism_from_unit_images(morphism)

            submonoid = self.localization_submonoid()
            match submonoid._selected_representation_kind():
                case "generators":
                    for inverted in self.inverted_elements():
                        match morphism(inverted).is_unit():
                            case True:
                                pass
                            case False:
                                raise ValueError(
                                    f"{morphism} does not carry {inverted} to a unit, so it does not "
                                    f"factor through {self}"
                                )
                            case _:
                                assert False, (
                                    f"invertibility of the image of {inverted} under {morphism} is unresolved; "
                                    f"constructing the induced map from {self} requires that unit-image hypothesis"
                                )
                    return self._induced_morphism_from_unit_images(morphism)
                case "predicate":
                    pass
                case representation:
                    assert False, (
                        f"the selected submonoid representation {representation!r} supplies no unit-image computation"
                    )

            structure = submonoid._structure_data()
            if (
                target in LocalizationRings()
                and target.localization_source() is source
                and morphism is target.localization_map()
            ):
                if target.localization_submonoid() is submonoid:
                    return self._induced_morphism_from_unit_images(morphism)
                if (
                    structure.get("kind") == "prime_complement"
                    and target.localization_submonoid()._structure_data().get("kind") == "prime_complement"
                ):
                    return self.restriction_to(target)

            if (
                structure.get("kind") == "prime_complement"
                and target in QuotientRings()
                and target.quotient_source() is source
                and morphism is target.quotient_map()
                and (target.defining_ideal() == structure["prime_ideal"]) is True
            ):
                match target.is_field():
                    case True:
                        return self._induced_morphism_from_unit_images(morphism)
                    case False:
                        raise ValueError(
                            f"the quotient {target} is not a field, so its quotient map does not invert "
                            f"the complement of {structure['prime_ideal']}"
                        )
                    case _:
                        assert False, (
                            f"whether the quotient {target} is a field is unresolved; inducing its quotient "
                            f"map from {self} requires that field hypothesis"
                        )

            assert False, (
                f"the predicate presentation of {submonoid} selects no generating family or unit-image proof "
                f"for {morphism}; constructing a map from {self} requires every element of that submonoid "
                "to have a unit image"
            )

        def _induced_morphism_from_unit_images(self, morphism):
            r"""Construct the localization arrow after its unit-image premise is established.

            Owner: LocalizationRings.ParentMethods. Permitted callers are
            induced_morphism, the PrimeLocalizations local residue-map
            supplier, the QuotientRings total-quotient-map supplier after
            contracting a localized ideal, the maximal adic-localization
            comparison, and the adic-completion factory's maximal-prime case.

            The inputs are this exact localization ``L = S^-1 R`` and an owned
            ring morphism ``g: R -> T`` with this literal source. Each caller
            must establish ``g(S)`` lies in the units of ``T`` from its retained
            defining data: generator images or canonical maps at the public
            ingress; nonzero images in ``Frac(R/p)`` for the residue supplier;
            regular images in the total quotient ring of an S-saturated
            contraction; or the complement of a proved maximal adic ideal.
            A predicate or successful inversions of some denominators alone
            is not that global premise.

            The result is the owned ring map ``L -> T`` whose composite with
            ``R -> L`` is exactly ``g``. This is the single fraction evaluator
            for these callers; it does not infer or store a new premise.
            """
            assert morphism.domain() is self.localization_source(), (
                "an induced localization map must retain the exact localization source"
            )

            def image(element):
                fraction = self(element)
                return morphism(fraction.numerator()) * morphism(
                    fraction.denominator()
                ).inverse_of_unit()

            # The universal map is defined on the actual localization. Its
            # larger fraction-field computation model need not admit this
            # map: a residue or component map can kill elements that become
            # invertible in that model. The owned fraction formula is exact.
            return OwnedRings().Mor(self, morphism.codomain())(image)

        @cached_method
        def localization_map(self):
            r"""Return the canonical map ``R -> S^-1 R`` derived from this localization datum."""
            source = self.localization_source()
            return source.Mor(self, category=OwnedRings())(
                lambda element: self.fraction(element),
            )

        def restriction_to(self, target):
            r"""Return the unique map ``S^{-1}R -> T^{-1}R`` commuting with the maps from ``R``.

            Localization is universal among ring maps out of ``R`` that invert
            ``S``.  So whenever ``T^{-1}R`` already inverts every element of
            ``S``, exactly one map ``S^{-1}R -> T^{-1}R`` respects the two maps
            from ``R``, and it sends ``a/s`` to ``a`` times the inverse of ``s``.
            Uniqueness is what makes these maps compose: for ``S`` inside ``T``
            inside ``U`` the composite of the two restrictions is the single
            restriction from ``S`` to ``U``.

            On spectra this is the inclusion of distinguished opens
            ``D(fg) <= D(f)``, so sheaf restriction on an affine scheme is this
            map and nothing further.  Taking ``T`` to be the complement of a
            prime gives the map from a section to its germ.

            The same open arises the other way, by localizing the chart
            ``S^{-1}R`` itself at ``g``.  Then the target's source is this ring
            rather than ``R``, and the map over it is that localization's own
            map, which the two constructions of ``D(fg)`` share.

            Between two prime localizations the containment ``S <= T`` is
            ``R \\ q <= R \\ p``, that is ``p <= q``, so ``R_q -> R_p`` exists
            exactly when ``p`` generalizes ``q``: the germ at a point maps
            to the germ at any point whose closure contains it. These
            presentations do not select finite generating sets, so the
            containment is decided on the primes rather than on inverted
            elements.
            """

            from sage_extensions.categories.rings.commutative_algebra import (
                PrimeLocalizations,
            )

            match target in LocalizationRings():
                case True:
                    pass
                case False:
                    raise TypeError(
                        f"a map {self} -> {target} over {self.localization_source()} needs a localization of that ring "
                        f"as target, but {target} is not a localization"
                    )
            if target.localization_source() is self:
                # The overlap was built by localizing this chart, so the map
                # over it is that localization's own map: it is already the
                # unique map out of this ring inverting what the target adds.
                return target.localization_map()
            match target.localization_source() is self.localization_source():
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"{self} and {target} localize different rings, so no map over the source exists"
                    )
            if self in PrimeLocalizations():
                match target in PrimeLocalizations():
                    case True:
                        pass
                    case False:
                        raise ValueError(
                            f"{self} inverts the complement of the prime {self.localized_prime()}, whose presentation "
                            f"has no chosen finite generating family; this selected restriction construction to {target} "
                            "requires a prime localization as target"
                        )
                match conjunction(
                    self.localized_prime().contains_ambient_element(generator)
                    for generator in target.localized_prime().ideal_generators()
                ):
                    case True:
                        pass
                    case False:
                        raise ValueError(
                            f"{target.localized_prime()} is not contained in {self.localized_prime()}, "
                            f"so {target} does not invert everything {self} inverts and the universal "
                            "property of localization gives no map between them"
                        )
                    case _:
                        assert False, (
                            f"the containment of {target.localized_prime()} in {self.localized_prime()} "
                            f"is unresolved; constructing the selected restriction {self} -> {target} "
                            "requires that containment to be established"
                        )
            else:
                for inverted in self.inverted_elements():
                    match target(inverted).is_unit():
                        case True:
                            pass
                        case False:
                            raise ValueError(
                                f"{target} does not invert {inverted}, so the universal "
                                f"property of localization gives no map from {self}"
                            )
                        case _:
                            assert False, (
                                f"invertibility of {inverted} in {target} is unresolved; constructing the selected "
                                f"restriction from {self} requires that unit-image hypothesis to be established"
                            )

            def image(element):
                numerator = target(element.numerator())
                denominator = target(element.denominator())
                return numerator * denominator.inverse_of_unit()

            return OwnedRings().Mor(self, target)(image)

        def localization_fraction_data(self, element):
            r"""Return one represented fraction ``(r,s)`` for ``element=r/s``."""
            value = self(element)
            source = self.localization_source()
            return source(value.numerator()), source(value.denominator())


class _PredicateSubringParent(Parent):
    @lazy_attribute
    def Element(self):
        return _PredicateSubringElement

    def __init__(self, ambient_ring, predicate, description, category):
        SageObject.__init__(self)
        from sage_extensions.owned_category import owned_category_join

        if ambient_ring not in SageRings() and ambient_ring not in OwnedRings():
            raise TypeError(f"{ambient_ring} is not a ring")
        ambient_ring = _own_ring(ambient_ring)
        # A subring is a ring with an inclusion as additional data: the
        # category of its objects is the rings (OWN-15, ARC-07).
        self._constructing_category = OwnedRings()
        self._ambient_ring = ambient_ring
        self._predicate = predicate
        self._description = description
        commutative_rings = OwnedRings().Commutative()
        # A subring of a commutative ring is commutative: the ambient ring's
        # placement decides it, never a computed answer.
        self._preamble_is_commutative = category.is_subcategory(commutative_rings) or ambient_ring in commutative_rings
        self._one = ambient_ring.one()
        self._zero = ambient_ring.zero()
        # The predicate subring is not yet a Parent with a category.  Its
        # algebra/category placement cannot take this partially initialized
        # object as the scalar ring: doing so recursively constructs
        # Algebras(self) before self has a subcategory_class.
        base = _owned_integers()
        from sage_extensions.categories.algebras.algebras import Algebras

        algebra = Algebras(base).Associative().Unital()
        from sage_extensions.categories.group.magmas import AdditiveGroups

        # Predicate subrings are a separate concrete ring owner, not an
        # _OwnedRingParent. Give their defining abelian-group structure the
        # same initial-placement guarantee, before Parent.__init__ invokes
        # the regular-module construction hooks below.
        placements = [category, AdditiveGroups().AdditiveCommutative()]
        match self._preamble_is_commutative:
            case True:
                from sage_extensions.categories.modules.pure.modules import (
                    FinitelyGeneratedFreeModules,
                )

                placements.append(algebra.Commutative())
            case False:
                placements.append(algebra)
        Parent.__init__(self, base=base, category=owned_category_join(tuple(placements)))
        realize_owned_category(self)
        # A predicate-subring datum asserts closure and the ring constants.
        # Refute a decided false constant, but do not treat an undecided
        # predicate as false. Constants are supplied by those defining laws.
        assert predicate(self._one) is not False and predicate(self._zero) is not False, (
            f"the subset of {ambient_ring} defined by '{description}' is not a unital subring: "
            "the condition fails on 0 or on 1"
        )
        self._one = self.element_class(self, _engine_element(ambient_ring, self._one))
        self._zero = self.element_class(self, _engine_element(ambient_ring, self._zero))
        from sage_extensions.categories.algebras.algebras import (
            _algebra_from_native_ring,
        )

        _algebra_from_native_ring(self, lambda left, right: self(left * right), self._one,
            lambda scalar, element: self(self(scalar) * self(element)))

    def _commutativity_decision(self):
        if self._preamble_is_commutative:
            return True
        return AtomicProposition("is_commutative", self)

    def __call__(self, element):
        r"""Construct an element of the predicate subring directly."""
        return self._element_constructor_(element)

    def _element_constructor_(self, element):
        return PredicateSubrings.ParentMethods._element_constructor_(self, element)

    def _from_engine_element(self, element):
        r"""Cross a computation in the larger ring back into this subring."""
        candidate = _owned_engine_element(self._ambient_ring, element)
        if (candidate == self._ambient_ring.zero()) is True:
            return self._zero
        if (candidate == self._ambient_ring.one()) is True:
            return self._one
        return self(candidate)

    def _element_in_larger_ring(self, element):
        r"""Raise this subring's stored computation in its exact larger ring."""
        native = self._engine_element(element)
        return _owned_engine_element(self._ambient_ring, native)

    def _engine_element(self, element):
        return self(element)._backend()

    def _selected_engine_ring(self):
        r"""Return the ambient ring's selected computation realization."""
        return _engine_ring(self._ambient_ring)

    def __contains__(self, element):
        return PredicateSubrings.ParentMethods.__contains__(self, element)


_OwnedRingBootstrapParent.register(_PredicateSubringParent)


def _predicate_subring(ambient_ring, predicate, description, category=None):
    from sage_extensions.owned_category import owned_category_join

    placement = PredicateSubrings()
    if category is not None:
        placement = owned_category_join((placement, category))
    return _PredicateSubringParent(
        ambient_ring,
        predicate,
        description,
        placement,
    )


class LocalRingConstruction:
    r"""The selected maximal ideal and residue quotient data of a local ring.

    A construction owner may supply a value or a fixed zero-argument factory
    for each datum. The factories return an owned maximal ideal, its owned
    residue field, and an owned quotient map from the same local ring, with
    that ideal as kernel. The accessors cache their results independently;
    requesting the maximal ideal need not compute a residue field.
    """

    def __init__(
        self,
        maximal_ideal=None,
        residue_field=None,
        residue_map=None,
        *,
        maximal_ideal_factory=None,
        residue_field_factory=None,
        residue_map_factory=None,
    ) -> None:
        for name, value, factory in (
            ("maximal ideal", maximal_ideal, maximal_ideal_factory),
            ("residue field", residue_field, residue_field_factory),
            ("residue map", residue_map, residue_map_factory),
        ):
            if value is not None and factory is not None:
                raise ValueError(f"the selected {name} needs one value or factory, not both")
        if maximal_ideal is None and maximal_ideal_factory is None:
            raise ValueError("a local-ring construction needs its maximal ideal or a factory for it")
        if residue_field is None and residue_field_factory is None:
            raise ValueError("a local-ring construction needs its residue field or a factory for it")
        self._maximal_ideal = maximal_ideal
        self._residue_field = residue_field
        self._residue_map = residue_map
        self._maximal_ideal_factory = maximal_ideal_factory
        self._residue_field_factory = residue_field_factory
        self._residue_map_factory = residue_map_factory

    @cached_method
    def maximal_ideal(self):
        if self._maximal_ideal_factory is not None:
            return self._maximal_ideal_factory()
        return self._maximal_ideal

    @cached_method
    def residue_field(self):
        if self._residue_field_factory is not None:
            return self._residue_field_factory()
        return self._residue_field

    @cached_method
    def residue_map(self):
        if self._residue_map_factory is not None:
            return self._residue_map_factory()
        return self._residue_map


def _install_local_ring_construction(ring, maximal_ideal, residue_field, residue_map=None):
    r"""Install the selected local-ring quotient datum on ``ring`` exactly once."""
    if maximal_ideal.ring() is not ring:
        raise ValueError(
            f"cannot make {ring} a local ring with maximal ideal {maximal_ideal}: that is an ideal of "
            f"{maximal_ideal.ring()}"
        )
    if residue_map is not None:
        if residue_map.domain() is not ring or residue_map.codomain() is not residue_field:
            raise ValueError(
                f"the residue map of the local ring {ring} must be {ring} -> {residue_field}, but {residue_map} "
                f"is a map {residue_map.domain()} -> {residue_map.codomain()}"
            )
    construction = LocalRingConstruction(maximal_ideal, residue_field, residue_map)
    existing = ring._selected_local_ring_construction()
    if existing is not None:
        if (
            existing.maximal_ideal() is not maximal_ideal
            or existing.residue_field() is not residue_field
            or existing.residue_map() is not residue_map
        ):
            raise ValueError(
                f"{ring} is already a local ring with maximal ideal {existing.maximal_ideal()} and residue field "
                f"{existing.residue_field()}; it cannot also have maximal ideal {maximal_ideal} and residue field "
                f"{residue_field}"
            )
        return ring
    ring._local_ring_construction = construction
    return ring


class OwnedRings(CategoryPacketMethods, OwnedCategory):
    """Unital rings whose notebook-facing ring interface is owned here."""

    _MorCategory = RingMorCategoryConstruction

    def an_object(self):
        r"""The integers, the initial object of this category."""
        return _owned_integers()

    def super_categories(self):
        from sage_extensions.categories.group.magmas import AdditiveGroups

        return [OwnedSemirings(), OwnedRngs(), AdditiveGroups().AdditiveCommutative()]

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a ring morphism needs a ring as domain and codomain, but got {domain} and {codomain}"
            )
        return _ring_mor_category(domain, codomain)

    def product(self, factors):
        r"""``prod_{i in I} R_i``, the product of an indexed family of rings, with its projections.

        The product of rings is the product of underlying sets with
        coordinatewise operations (Mathlib ``Pi.ring``).  The family is taken
        over its index set (``CON-15``); a bare sequence is the family on the
        canonical labels.  Equal families give one ring.
        """
        return self._categorical_product_construction(factors).object()

    def _categorical_product(self, left, right):
        return self.product((left, right))

    def _categorical_product_construction(self, factors):
        r"""The product ring with its discrete diagram and universal cone of projections.

        A cone with legs ``f_i: A -> R_i`` factors through the product by
        ``a |-> (f_i(a))_i``, the unique ring map with those components.
        """
        from sage_extensions.categories.abstract_categories.products import (
            SelectedLimitConstruction,
            _discrete_diagram,
            _finite_factor_family,
        )

        family = _finite_factor_family(factors, name="Product factors")
        assert all(factor in self for factor in family), (
            f"a product of rings is a product of objects of {self}, but not every factor of {family} is a ring"
        )
        product = _product_ring_of_family(family)
        diagram = _discrete_diagram(family, self)
        universal_cone = diagram.ProductCones().cone(
            product, lambda index: _product_ring_projection(product, family, index.value())
        )

        def factorizer(cone):
            apex = cone.apex()
            legs = {label: cone.structure_morphism(diagram.domain()(label)) for label in family.index_set()}
            apex_map = OwnedRings().Mor(apex, product)(
                lambda element: _product_ring_element(
                    product, family, {label: legs[label](element) for label in family.index_set()}
                )
            )
            return diagram.Cones().Mor(cone, universal_cone)._from_commuting_apex_map(apex_map)

        return SelectedLimitConstruction(diagram, universal_cone, factorizer)

    # Functors out of rings, sited on their domain.

    def center_functor(self):
        r"""Return ``Z : Core(Ring) -> CRing``."""
        return RingCenterFunctor()

    class SubcategoryMethods:
        def Division(self):
            r"""Return this category with the axiom that every nonzero element is a unit."""
            return self._with_axiom("Division")

        def NoZeroDivisors(self):
            r"""Return this category with the axiom ``xy = 0  =>  x = 0 or y = 0``."""
            return self._with_axiom("NoZeroDivisors")

        def Noetherian(self):
            r"""Return this category with the ascending chain condition on left ideals."""
            return self._with_axiom("Noetherian")

        def Artinian(self):
            r"""Return this category with the descending chain condition on left ideals."""
            return self._with_axiom("Artinian")

        def Nontrivial(self):
            r"""Return this category with the axiom ``1 != 0`` (Mathlib ``Nontrivial``)."""
            return self._with_axiom("Nontrivial")

    class Nontrivial(CategoryWithAxiom):
        r"""Nontrivial rings: ``1 != 0``, so every ring except the zero ring (Mathlib ``Nontrivial``)."""

        @classmethod
        def _repr_object_names(cls):
            return "nontrivial rings"

        def an_object(self):
            r"""The integers."""
            return _owned_integers()

    class Division(CategoryWithAxiom):
        r"""Nontrivial rings in which every nonzero element is a unit."""

        @classmethod
        def _repr_object_names(cls):
            return "division rings"

        def an_object(self):
            r"""The field of two elements."""
            return GF(2)

        def extra_super_categories(self):
            r"""A division ring is nontrivial and has no zero divisors."""
            return [OwnedRings().NoZeroDivisors(), OwnedRings().Nontrivial()]

        class ElementMethods:
            def _unit_decision(self):
                r"""Unit status is the negation of the possibly undecided zero equality."""
                return negation(self == self.parent().zero())

        class Commutative(CategoryWithAxiom):
            r"""Fields: nontrivial commutative rings in which every nonzero element is a unit.

            Fields are a full subcategory of rings, so a map of fields is a
            ring map and this category inherits the ring ``Mor``.
            """

            @classmethod
            def _repr_object_names(cls):
                return "fields"

            def an_object(self):
                r"""The field of two elements."""
                return GF(2)

            def extra_super_categories(self):
                r"""A field has ideals ``0`` and itself and is complete for ``(0)``.

                Its unique maximal ideal is zero, so its maximal-adic
                completion is the field itself.
                """
                return [
                    OwnedRings().Commutative().PrincipalIdeals(),
                    OwnedRings().Artinian(),
                    OwnedRings().Commutative().Local().Complete(),
                ]

            class SubcategoryMethods:
                def Prime(self):
                    r"""Return this category with the axiom of having no proper subfield."""
                    return self._with_axiom("Prime")

            class Prime(CategoryWithAxiom):
                r"""Prime fields: \(\mathbf F_p\) and \(\mathbb Q\), the fields with no proper subfield."""

                @classmethod
                def _repr_object_names(cls):
                    return "prime fields"

                def an_object(self):
                    r"""The field of two elements."""
                    return self(2)

                def _call_(self, characteristic):
                    r"""Return the prime field of characteristic zero or a positive prime.

                    Characteristic zero selects the owned rational field;
                    characteristic ``p`` selects the existing field ``GF(p)``.
                    The input is a characteristic, not a finite-field order.
                    """
                    integers = _owned_integers()
                    selected = _owned_engine_element(
                        integers, _engine_numeral(integers, characteristic)
                    )
                    if selected.is_zero() is True:
                        return _owned_rationals()
                    if (selected < integers.zero()) is True:
                        raise ValueError(
                            f"a prime field has characteristic zero or a positive prime, but got {selected}"
                        )
                    match selected.is_prime():
                        case True:
                            return GF(selected)
                        case False:
                            raise ValueError(
                                f"a prime field has characteristic zero or a positive prime, but got {selected}"
                            )
                        case _:
                            assert False, (
                                f"constructing the prime field of characteristic {selected} requires its "
                                "primality to be established"
                            )

            class Finite(CategoryWithAxiom):
                r"""Finite fields ``F_q``: a field whose underlying set is finite.

                The element operations below are those of the cyclic group
                ``F_q^x`` and of squares in ``F_q``; each is computed by the
                field's private realization (``OWN-06``) and raised back.
                """

                @classmethod
                def _repr_object_names(cls):
                    return "finite fields"

                def an_object(self):
                    r"""The field with four elements."""
                    return GF(4)

                class ElementMethods:
                    def multiplicative_order(self):
                        r"""The order of this nonzero element in the group ``F_q^x``."""
                        field = self.parent()
                        assert (self == field.zero()) is not True, (
                            f"0 has no multiplicative order in {field}: it is not in the group of units"
                        )
                        return _owned_engine_element(
                            _owned_integers(),
                            SageZZ(_engine_element(field, self).multiplicative_order()),
                        )

                    @RealizationHook
                    def _squareness_decision(self):
                        r"""Whether ``y^2 = self`` for some ``y`` in ``F_q``, decided by the realization."""
                        return bool(_engine_element(self.parent(), self).is_square())

                    def sqrt(self):
                        r"""A ``y`` in ``F_q`` with ``y^2 = self``, chosen by the realization."""
                        field = self.parent()
                        assert self.is_square() is True, (
                            f"{self} has no square root in {field}: it is not a square there"
                        )
                        return _owned_engine_element(field, _engine_element(field, self).sqrt())

            class ParentMethods:
                def _krull_dimension_decision(self):
                    r"""``0``: the only prime ideal of a field is ``(0)``."""
                    return _owned_integers().zero()

                def field_generators(self):
                    r"""Return the selected finite generators over the prime field.

                    The current computation covers represented finite fields
                    and number fields, including the levels of a relative
                    tower. These elements determine every unital field map;
                    arbitrary fields need not have a finite generating set.
                    """
                    return _field_generators(self)

                def exact_embeddings(self, codomain):
                    r"""Enumerate the supplied exact field embeddings into ``codomain``.

                    Field embeddings are the unital ring maps, independently
                    of any additional coefficient-algebra presentation. The
                    existing ring-Mor computation supplies a finite ordered
                    enumeration in its supported realization cases; this does
                    not assert that every pair of fields has finitely many
                    embeddings or an available enumeration.
                    """
                    return OwnedRings().Mor(self, codomain).embeddings()

                def first_exact_embedding(self, codomain):
                    r"""Choose the first embedding in the supplied finite enumeration.

                    The selected enumeration fixes the order; the fields
                    themselves do not have a canonical first embedding.
                    """
                    embeddings = self.exact_embeddings(codomain)
                    if (embeddings.cardinality() == 0) is True:
                        raise ValueError(f"{self} has no embedding into {codomain}")
                    return embeddings[0]

                def absolute_galois_group(self):
                    r"""Return the absolute Galois group ``G_K`` of this field ``K``.

                    The group is the existing profinite owner; this field method is
                    only the mathematical construction site and creates no parallel
                    realization. That owner retains the selected algebraic closure
                    and base embedding. Its existing closure and exact-embedding
                    computations determine the available realization cases; the
                    general group is defined without a finite-field or number-field
                    hypothesis.
                    """
                    from sage_extensions.categories.group.profinite.absolute_galois_group import (
                        AbsoluteGaloisGroup,
                    )

                    return AbsoluteGaloisGroup(self)

    class NoZeroDivisors(CategoryWithAxiom):
        r"""Rings in which ``xy = 0`` forces ``x = 0`` or ``y = 0``.

        This axiom allows the zero ring. Nontriviality is the separate
        ``Nontrivial`` axiom, and commutativity is not assumed.
        """

        @classmethod
        def _repr_object_names(cls):
            return "rings without zero divisors"

        def an_object(self):
            r"""The integers."""
            return _owned_integers()

        class ParentMethods:
            def _reducedness_decision(self):
                r"""The zero-product axiom excludes nonzero positive-power nilpotents.

                Induction on the positive exponent proves the assertion
                without commutativity or nontriviality; the zero ring also
                satisfies it. This supplies the inherited nonunital-semiring
                predicate and needs no ideal or radical computation.
                """
                return True

        class Nontrivial(CategoryWithAxiom):
            r"""Nontrivial rings without zero divisors, with no commutativity assumption."""

            @classmethod
            def _repr_object_names(cls):
                return "nontrivial rings without zero divisors"

            def an_object(self):
                r"""The integers, whose zero and one are distinct."""
                return _owned_integers()

            class ParentMethods:
                @cached_method
                def nonzero_multiplicative_submonoid(self):
                    r"""Return the multiplicative submonoid ``R - {0}`` of this ring.

                    Nontriviality puts one in this subset; the zero-product
                    axiom makes it closed under multiplication. A ring map
                    restricts to these submonoids only when it preserves
                    nonzero elements.
                    """
                    from sage_extensions.categories.rings.commutative_algebra import (
                        _nonzero_element_submonoid,
                    )

                    return _nonzero_element_submonoid(self)

        class Commutative(CategoryWithAxiom):
            r"""Commutative rings satisfying the zero-product axiom.

            This intersection still allows the zero ring. Integral domains
            are its existing ``Nontrivial`` refinement; nonzero denominators
            and fraction fields require that additional hypothesis.
            """

            @classmethod
            def _repr_object_names(cls):
                return "commutative rings without zero divisors"

            def an_object(self):
                r"""The integers."""
                return _owned_integers()

            class Nontrivial(CategoryWithAxiom):
                r"""Integral domains: nonzero commutative rings without zero divisors.

                The inherited arrows remain all unital ring maps. The
                fraction-field operations below construct objects and their
                canonical injections; they do not assert a functor on every
                domain map, since a noninjective map need not extend to
                fraction fields.
                """

                @classmethod
                def _repr_object_names(cls):
                    return "integral domains"

                def an_object(self):
                    r"""The integers."""
                    return _owned_integers()

                class ParentMethods:
                    def fractional_ideal(self, *module_generators):
                        r"""Return the fractional ideal spanned by the stated elements of ``Frac(self)``."""
                        from sage_extensions.categories.modules.fractional_ideals import (
                            _fractional_ideal,
                        )

                        if len(module_generators) == 1 and isinstance(
                            module_generators[0], (tuple, list)
                        ):
                            module_generators = tuple(module_generators[0])
                        return _fractional_ideal(self, tuple(module_generators))

                    @cached_method
                    def fraction_field_localization(self):
                        r"""Return the target of the localization ``(R-{0})^-1 R``.

                        For a field the target is this same field. Otherwise
                        the localization owner retains the source and the
                        nonzero submonoid; the localization is a field.
                        """
                        from sage_extensions.categories.rings.commutative_algebra import (
                            _localization_at_submonoid,
                        )

                        if self in OwnedRings().Division().Commutative():
                            return self
                        return _localization_at_submonoid(
                            self,
                            self.nonzero_multiplicative_submonoid(),
                        )

                    @cached_method
                    def fraction_field_map(self):
                        r"""Return the localization map ``R -> Frac(R)``.

                        Scalar extension along it is the generic fibre: its
                        kernel on a module is exactly the torsion submodule.
                        An ideal extends to the unit ideal exactly when it
                        is nonzero. The source is nontrivial, so ``R-{0}``
                        contains the multiplicative identity.
                        """
                        if self in OwnedRings().Division().Commutative():
                            return OwnedRings().Mor(self, self).identity()
                        field = self.fraction_field()
                        localization = self.fraction_field_localization()
                        if field is localization:
                            return localization.localization_map()
                        from sage_extensions.categories.rings.commutative_algebra import (
                            _canonical_map,
                        )

                        return _canonical_map(self, field)

                    def fraction_field(self):
                        r"""``Frac(D)``: the localization ``(D-{0})^{-1} D``, one field per ``D``.

                        Where the construction of ``D`` already holds the field it
                        generates, that field is ``Frac(D)`` (``ARC-10``):

                        - ``ZZ``: ``QQ``, the named construction ``Frac(ZZ)``;
                        - an order ``O`` of a number field ``K``: ``K = O (x) QQ``
                          (Neukirch I §12, ``OwnedOrders``);
                        - a localization ``S^{-1} R`` of a domain ``R``:
                          ``Frac(R)`` (Mathlib
                          ``IsFractionRing.isFractionRing_of_isDomain_of_isLocalization``).

                        Otherwise it is :meth:`fraction_field_localization`.
                        """
                        if self in OwnedRings().Division().Commutative():
                            return self
                        match self:
                            case _ if self is _owned_integers():
                                return _owned_rationals()
                            case _ if self in OwnedOrders():
                                return _owned_engine_ring(_engine_ring(self).number_field())
                            case _ if self in LocalizationRings():
                                source = self.localization_source()
                                assert source in OwnedIntegralDomains(), (
                                    f"Frac({self}) is Frac({source}) only when {source} is an "
                                    f"integral domain, but {source} is only known to be in "
                                    f"{source.category()}"
                                )
                                return source.fraction_field()
                            case _:
                                return self.fraction_field_localization()

    class Noetherian(CategoryWithAxiom):
        r"""Rings satisfying the ascending chain condition on left ideals.

        Following Mathlib's ``IsNoetherianRing R = IsNoetherian R R``,
        this says that the left regular module is Noetherian, equivalently
        every left ideal is finitely generated. In the commutative case
        this is the usual Noetherian condition. The property admits the
        zero ring and supplies no chosen ideal generators or right-module
        Noetherian hypothesis.
        """

        @classmethod
        def _repr_object_names(cls):
            return "noetherian rings"

        def an_object(self):
            r"""The integers."""
            return _owned_integers()

    class Artinian(CategoryWithAxiom):
        r"""Left Artinian rings: the descending chain condition on left ideals.

        The left regular module is Artinian (Mathlib ``IsArtinianRing R``).
        In the commutative case this is the usual Artinian condition. The
        zero ring is allowed; no right-module condition or selected
        composition series is part of this axiom.
        """

        @classmethod
        def _repr_object_names(cls):
            return "artinian rings"

        def an_object(self):
            r"""The field of two elements: a field is artinian."""
            return GF(2)

        def extra_super_categories(self):
            r"""Hopkins–Levitzki: a left Artinian unital ring is left Noetherian."""
            return [OwnedRings().Noetherian()]

    class Commutative(CategoryWithAxiom):
        r"""Commutative unital rings in the owned mathematical graph."""

        @classmethod
        def _repr_object_names(cls):
            return "commutative rings"

        def an_object(self):
            r"""The integers."""
            return _owned_integers()

        class SubcategoryMethods:
            @cached_method
            def prime_spectrum_functor(self):
                r"""The contravariant prime-spectrum functor to topological spaces."""
                from sage_extensions.categories.rings.commutative_algebra import (
                    _PrimeSpectrumFunctor,
                )

                return _PrimeSpectrumFunctor(self)

            def Local(self):
                r"""Return this category with the axiom of a unique maximal ideal."""
                return self._with_axiom("Local")

            def PrincipalIdeals(self):
                r"""Return this category with the axiom that every ideal is principal."""
                return self._with_axiom("PrincipalIdeals")

        class Local(CategoryWithAxiom):
            r"""Local rings: one maximal ideal."""

            @classmethod
            def _repr_object_names(cls):
                return "local rings"

            def an_object(self):
                r"""The integers localized at the prime (2)."""
                return _owned_integers().localize_at_prime(2)

            def extra_super_categories(self):
                r"""A local ring has ``1 != 0`` (Mathlib ``IsLocalRing.toNontrivial``)."""
                return [OwnedRings().Nontrivial()]

            class SubcategoryMethods:
                def Complete(self):
                    r"""Return the complete-local refinement."""
                    return self._with_axiom("Complete")

            class ParentMethods:
                @cached_method
                def local_ring_construction(self):
                    r"""Return the fixed local quotient, with the canonical field default.

                    Explicitly supplied local data keep their exact ideal,
                    residue field and map. Without such data, a field has
                    canonical residue field itself and quotient map the ring
                    identity. Its zero maximal ideal is computed independently
                    on demand, so reading the field or map needs no ideal
                    computation.
                    """
                    construction = self._selected_local_ring_construction()
                    if construction is None and self in OwnedRings().Division().Commutative():
                        construction = LocalRingConstruction(
                            maximal_ideal_factory=lambda: self.ideal(self.zero()),
                            residue_field=self,
                            residue_map_factory=lambda: OwnedRings().Mor(self, self).identity(),
                        )
                    assert construction is not None, (
                        f"the local ring {self} has no selected maximal-ideal and residue-field data"
                    )
                    return construction

                def maximal_ideal(self):
                    return self.local_ring_construction().maximal_ideal()

                def residue_field(self):
                    return self.local_ring_construction().residue_field()

                def residue_map(self):
                    r"""Return the selected local quotient map ``R -> kappa(m)``."""
                    selected = self.local_ring_construction().residue_map()
                    assert selected is not None, (
                        f"the residue map R -> R/m of the local ring {self} is missing"
                    )
                    return selected

                def _field_decision(self):
                    r"""A local ring is a field exactly when its maximal ideal is zero."""
                    construction = self._selected_local_ring_construction()
                    if construction is None:
                        return super()._field_decision()
                    from sage_extensions.categories.rings.commutative_ideals import (
                        CommutativeIdeals,
                    )

                    maximal_ideal = construction.maximal_ideal()
                    if maximal_ideal not in CommutativeIdeals(self):
                        return super()._field_decision()
                    return maximal_ideal.is_zero()

            class Complete(CategoryWithAxiom):
                r"""Complete local rings: complete and separated for the maximal-ideal topology."""

                @classmethod
                def _repr_object_names(cls):
                    return "complete local rings"

                def an_object(self):
                    r"""The 2-adic integers: complete, and local because (2) is maximal."""
                    return _owned_integers().adic_completion(2)

                def extra_super_categories(self):
                    r"""The maximal ideal supplies a canonical complete adic structure.

                    An independently chosen ideal of definition is retained
                    when supplied; it need not be the maximal ideal.
                    """
                    return [OwnedAdicallyCompleteRings()]

                class ParentMethods:
                    @RealizationHook
                    def _selected_adic_defining_ideal(self):
                        r"""Supply the canonical maximal-adic datum to ``ideal_of_definition``.

                        An owned realization's explicit selected-ideal
                        supplier takes precedence over this default.
                        """
                        return self.maximal_ideal()

        class PrincipalIdeals(CategoryWithAxiom):
            r"""Principal ideal rings: every ideal is principal (Mathlib's ``IsPrincipalIdealRing``)."""

            @classmethod
            def _repr_object_names(cls):
                return "principal ideal rings"

            def an_object(self):
                r"""The integers."""
                return _owned_integers()

            def extra_super_categories(self):
                r"""A principal ideal is finitely generated."""
                return [OwnedRings().Noetherian()]

        class ParentMethods:
            @RealizationHook
            def _nilradical_decision(self):
                r"""Supply the common nonunital-semiring nilradical from this ideal owner."""
                return self.ideal(self.zero()).radical()

            def affine_equation_family(self, relative_variables, equations):
                r"""Return ``Spec(self[x]/I) -> Spec(self)`` for the stated equations.

                This construction needs a commutative unital coefficient
                ring; no additional choice of an algebra structure is used.
                """
                from sage_extensions.categories.schemes.families import (
                    _relative_affine_family,
                )

                return _relative_affine_family(self, relative_variables, equations)

            @RealizationHook
            def _reducedness_decision(self) -> bool | Predicate:
                r"""Return whether this commutative ring has zero nilradical."""
                zero_ideal = self.ideal(self.zero())
                return self.nilradical() == zero_ideal

            @RealizationHook
            def _normality_decision(self):
                r"""Protected normality decision, whose only caller is is_normal.

                Owned realizations and more specific categories may decide the
                local-normal-domain predicate. Otherwise retain that proposition;
                no computed normalization or finite presentation is presumed.
                """
                return AtomicProposition("is_normal", self)

            def is_normal(self):
                r"""Whether every prime localization is a normal domain.

                This is the definition for a general commutative ring
                (Stacks, Section 10.37, Definition 10.37.11). Normal domains
                are integrally closed in their fraction fields. The zero ring
                has no prime ideals; fields already satisfy the definition.
                """
                if (self.one() == self.zero()) is True:
                    return True
                if self in OwnedRings().Division().Commutative():
                    return True
                return self._normality_decision()

            @RealizationHook
            def _normalization_data(self):
                r"""A retained normalization construction, or no selected computation.

                Protected computation contract for ``normalization``,
                ``normalization_map``, ``normalization_components``,
                ``conductor_ideal`` and this ring's coefficient-dependent
                ``delta_invariant``, for the finite-localization producer
                reading its source's retained data, and for
                ``LocalizationRings._normality_decision``. The convention is
                ``A -> A_red -> B``, where ``B`` is the integral closure of
                ``A_red`` in its total quotient ring in the represented case
                of finitely many minimal primes (Stacks, Tag 035P).

                A producer retains those two maps, their composite, the
                normalized component domains and maps, and an actual module
                ``N`` realizing ``Res_nu(B)``. The map ``A -> N`` sends one
                to the unit; its cokernel is ``B/image(A)`` as an A-module.
                Any coefficient field map used for delta is retained data.
                A bare ring does not select such a field.

                Finite component data do not assert that ``B`` is a finite
                A-module. Only a producer establishing that stronger
                hypothesis may supply finite presentation or finite-algebra
                placement. The default provides neither a computation nor
                a finiteness assertion.
                """
                return None

            @cached_method
            def normalization_map(self):
                r"""Return the retained ``A -> A_red -> normalization(A_red)``.

                Its kernel is the nilradical. It is injective for reduced
                input, and is finite only under an additional finiteness
                hypothesis on the normalization. This convention differs
                from taking the integral closure of a nonreduced ``A`` in
                its own total quotient ring.
                """
                data = self._normalization_data()
                assert data is not None, (
                    f"no normalization construction with its component and module data is represented for {self}"
                )
                return data.normalization_map

            @cached_method
            def normalization(self):
                r"""Return the target of this ring's retained normalization map."""
                return self.normalization_map().codomain()

            def normalization_components(self):
                r"""Return the retained normalized components and their maps from A.

                The selected finite family consists of triples
                ``(minimal_prime_of_A, normal_component, A_to_component)``.
                The construction retains their projections from the common
                normalization target as well. No finite enumeration is
                inferred for an arbitrary commutative ring.
                """
                data = self._normalization_data()
                assert data is not None, (
                    f"no normalized component construction is represented for {self}"
                )
                return data.components

            @cached_method
            def conductor_ideal(self):
                r"""Return ``Ann_A(B/image(A))`` for the retained normalization.

                Equivalently this is ``{a : nu(a) B <= image(nu)}``, an ideal
                of the original ``A``. Under the reduction convention it
                contains the nilradical; for reduced input it is the usual
                conductor ``(A :_A B)``.
                """
                data = self._normalization_data()
                assert data is not None, (
                    f"no normalization quotient module is represented for {self}"
                )
                return data.normalization_cokernel.annihilator()

            @cached_method
            def delta_invariant(self, base_field_map=None):
                r"""Return the retained coefficient dimension of ``B/image(A)``.

                The normalization construction retains an actual field map
                ``c:k -> A`` on this commutative ring, independently of an
                ambient algebra base. With no argument this is
                ``dim_k(Res_c(B/image(A)))``, including an infinite dimension when
                the module owner represents it. For reduced input the quotient is
                the usual ``B/A``. A quotient's immediate algebra base may be its
                polynomial presentation ring; it does not replace this chosen ``k``.

                An optional actual ``base_field_map:F -> k`` asks for a second
                scalar restriction, hence dimension for the composite ``F -> k -> A``.
                For example a one-dimensional quotient over a quadratic field over
                QQ has dimension two along that supplied field inclusion. Both maps
                and the module are retained by the restriction constructors. No
                factorization of an arbitrary map ``F -> A`` is guessed, and a
                dimension algorithm for every alternate field is not presumed.
                """
                data = self._normalization_data()
                assert data is not None, (
                    f"no normalization construction with a coefficient action is represented for {self}"
                )
                coefficient_map = data.coefficient_map
                assert coefficient_map is not None, (
                    f"the normalization of {self} has no retained coefficient field map"
                )
                field = _owned_ring(coefficient_map.domain())
                assert (
                    field in OwnedFields()
                    and coefficient_map.codomain() is self
                    and coefficient_map in OwnedRings().Mor(field, self)
                ), (
                    f"delta for {self} requires its retained unital ring map from an actual field"
                )
                quotient = data.normalization_cokernel.restrict_scalars(coefficient_map)
                if base_field_map is not None:
                    alternate_field = _owned_ring(base_field_map.domain())
                    assert (
                        alternate_field in OwnedFields()
                        and base_field_map.codomain() is field
                        and base_field_map in OwnedRings().Mor(alternate_field, field)
                    ), f"the alternate coefficient map must be an actual field map into {field}"
                    quotient = quotient.restrict_scalars(base_field_map)
                return quotient.dimension()

            @RealizationHook
            def _krull_dimension_decision(self):
                r"""Supply the common prime-chain dimension from the selected ring model.

                The inherited krull_dimension operation calls this hook.
                More specific categories and owned realizations retain their
                selected computations. This default keeps the existing exact
                ring-engine route, including its explicit availability frontier.
                """
                assert (self.one() == self.zero()) is not True, (
                    "the empty prime spectrum has Krull dimension -infinity; "
                    "an owned extended-dimension representation is not yet supplied"
                )
                return _engine_krull_dimension(self)

            @cached_method(key=lambda self, base_ring: id(_own_ring(base_ring)))
            def as_algebra_over(self, base_ring):
                r"""Read this ring through its selected canonical coefficient map.

                A commutative target makes any unital map from a
                commutative coefficient ring central. The selected scalar
                tower, the identity, and the unique integer map supply such
                maps without a foreign realization. A native coercion is
                used only when its two parents realize the actual endpoints;
                a larger computation model supplies no coefficient action
                on a proper subring. Use an explicit central ring map and
                its ``as_algebra`` operation to select another action.
                """
                base = _own_ring(base_ring)
                from sage_extensions.categories.algebras.algebras import (
                    Algebras,
                )

                if base not in OwnedRings().Commutative():
                    raise TypeError(
                        f"an algebra over {base} requires a commutative coefficient ring"
                    )
                selected = Algebras(base).Associative().Unital().Commutative()
                if self.base_ring() is base and self in selected:
                    return self
                if base is self:
                    return OwnedRings().Mor(self, self).identity().as_algebra()
                if base is _owned_integers():
                    return self.as_ZZ_algebra()

                current = self
                coefficient_map = OwnedRings().Mor(self, self).identity()
                seen = set()
                while id(current) not in seen:
                    seen.add(id(current))
                    current_base = current.base_ring()
                    if current_base is current or current_base not in OwnedRings():
                        break
                    current_algebras = Algebras(current_base).Associative().Unital().Commutative()
                    if current not in current_algebras:
                        break
                    selected_map = current.algebra_structure_morphism()
                    assert selected_map.domain() is current_base and selected_map.codomain() is current, (
                        "the selected coefficient map of a commutative algebra must retain "
                        "its literal coefficient and algebra endpoints"
                    )
                    coefficient_map = coefficient_map * selected_map
                    if current_base is base:
                        return coefficient_map.as_algebra()
                    current = current_base

                engine = self._selected_engine_ring()
                base_engine = base._selected_engine_ring()
                assert engine is not None and base_engine is not None, (
                    f"no canonical coefficient map {base} -> {self} is supplied by the retained "
                    "scalar tower or exact native endpoints; state the chosen ring map and use its as_algebra"
                )
                engine_map = engine.coerce_map_from(base_engine)
                if engine_map is None:
                    raise ValueError(
                        f"no canonical coefficient map {base} -> {self} is supplied by the retained "
                        "scalar tower or exact native realization; an explicit ring map may state another action"
                    )
                return OwnedRings().Mor(base, self)._from_engine_morphism(engine_map).as_algebra()

            def affine_spectrum(self, base_ring=None):
                r"""Return the affine scheme represented by this commutative ring or algebra."""
                from sage_extensions.categories.schemes.schemes import (
                    _affine_spectrum,
                )

                return _affine_spectrum(self, base_ring=base_ring)

            @RealizationHook
            def _ideal_generated_by(self, generators):
                r"""Supply the inherited two-sided ideal from owned commutative-ideal data.

                The common rng-ideal constructor is the caller;
                its tuple consists of elements of this exact ring. The result
                retains the ordinary ideal's inclusion in this ring's regular
                module. Commutativity makes every ordinary ideal two-sided.

                In a localization every denominator is a unit, so
                ``(a_1/s_1, ..., a_r/s_r)`` is the extension of the source ideal
                ``(a_1, ..., a_r)`` along ``R -> S^{-1}R``.  Saying it that way
                is what makes the result an ideal like any other: it arrives as
                a submodule of the regular module of ``S^{-1}R``, carrying the
                sum, product, intersection, colon, contraction and membership
                operations, and it asks the source for a numerator rather than a
                fraction field, so a localization of a ring that has none is
                built the same way.
                """
                from sage_extensions.categories.rings.commutative_ideals import (
                    _commutative_ideal,
                )

                if self in LocalizationRings():
                    source = self.localization_source()
                    numerators = tuple(
                        self.localization_fraction_data(generator)[0]
                        for generator in generators
                    )
                    return source.ideal(*numerators).extension_to_localization(self)
                return _commutative_ideal(self, generators)

            @RealizationHook
            def _quotient_ring_construction(self, ideal):
                r"""Supply the common ring quotient from its owned commutative ideal.

                The inherited quotient_ring operation is the caller. Its
                represented ideal or generator input is interpreted by the
                existing ideal owner in this exact ring. Every such ideal is
                two-sided, so the quotient retains this ring as its source
                and its actual kernel and canonical projection.
                """
                from sage_extensions.categories.rings.commutative_algebra import (
                    _owned_ideal,
                    _quotient_ring,
                )

                return _quotient_ring(self, _owned_ideal(self, ideal))

            def localization(self, *elements):
                from sage_extensions.categories.rings.commutative_algebra import (
                    _localization,
                )

                return _localization(self, *elements)

            def localize_at_prime(self, prime):
                from sage_extensions.categories.rings.commutative_algebra import (
                    _prime_localization_from_input,
                )

                return _prime_localization_from_input(self, prime)

            def residue_field_at(self, ideal):
                r"""Return the residue field ``R/m`` at a represented maximal ideal ``m``."""
                from sage_extensions.categories.rings.commutative_algebra import (
                    _residue_field_at,
                )

                return _residue_field_at(self, ideal)

            @RealizationHook
            def _dual_numbers_construction(self, name):
                r"""Supply the inherited semiring dual numbers from the retained quotient.

                The common semiring dual_numbers operation is the caller.
                The existing commutative-algebra constructor retains its
                actual coefficient ring, quotient source, defining ideal,
                parameter and selected rank-two module coordinates.
                """
                from sage_extensions.categories.rings.commutative_algebra import (
                    _dual_numbers,
                )

                return _dual_numbers(self, name=name)

            @RealizationHook
            def _adic_completion_construction(self, ideal, precision):
                r"""Supply the common ring completion from its selected adic construction.

                The inherited adic_completion operation is the caller. The
                existing commutative construction keeps its source, defining
                ideal, completion map and quotient projections, with only
                the completeness refinements its represented case proves.
                """
                from sage_extensions.categories.rings.commutative_algebra import (
                    AdicCompletions,
                )

                return AdicCompletions()(self, ideal, precision=precision)

            @cached_method
            def spectrum(self):
                from sage_extensions.categories.rings.commutative_algebra import (
                    PrimeSpectra,
                    IntegralPrimeSpectra,
                    _PrimeSpectrumTopologyData,
                )
                from sage_extensions.owned_category import _object_of, owned_category_join

                return _object_of(
                    owned_category_join((PrimeSpectra(), IntegralPrimeSpectra()))
                    if self in OwnedIntegralDomains() else PrimeSpectra(),
                    ring=self,
                    topology_data=_PrimeSpectrumTopologyData(self),
                )

            @RealizationHook
            def _finite_irreducible_components(self):
                r"""Protected finite component-ring computation, or None.

                Only irreducible_components calls this hook. An owned ring
                realization may retain a finite set of component domains R/p
                for its minimal primes, including their selected presentations.
                These are the same ring-valued objects represented by the
                public operation's general image of the minimal-prime locus.
                The separately named irreducible_component_locus consists of
                closed subsets of the prime spectrum.
                """
                return None

            @cached_method
            def irreducible_components(self):
                r"""The component domains ``R/p`` indexed by the minimal primes.

                A selected finite computation retains its quotient-ring
                presentations. Otherwise this is the image of the full
                minimal-prime locus under ``p |-> R/p``; no finite generation
                or enumeration of prime ideals is inferred. Evaluation at a
                particular prime still requires that ideal-subset quotient
                construction to be represented. The closed subsets ``V(p)``
                themselves are returned by irreducible_component_locus.
                """
                components = self._finite_irreducible_components()
                if components is not None:
                    return components
                # A selected finite minimal-prime family already determines
                # the actual component rings R/p. Do not discard this finite
                # construction merely because no separate component hook was
                # installed; each quotient keeps the literal source R.
                minimal = self._finite_minimal_primes()
                if minimal is not None:
                    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

                    return finite_ordered_set(tuple(self.quotient_ring(prime) for prime in minimal))
                from sage_extensions.categories.sets.set_categories import Sets

                return Sets().image_set(
                    lambda minimal_prime: self.quotient_ring(minimal_prime),
                    self.minimal_prime_locus(),
                )

            @RealizationHook
            def _total_quotient_map_decision(self):
                r"""Protected selected regular-element localization map, or None.

                Only total_quotient_map calls this hook. An owned realization
                or more specific category returns an owned ring morphism from
                this exact ring to its total quotient ring, retaining the
                canonical injection and its target together. It must establish
                the hypotheses of its localization computation; a product of
                component fields requires the corresponding finite reduced case.
                """
                return None

            @cached_method
            def total_quotient_map(self):
                r"""The canonical injection into the localization at all regular elements."""
                if (self.one() == self.zero()) is True:
                    return OwnedRings().Mor(self, self).identity()
                if self.is_finite() is True:
                    # Multiplication by a regular element is injective on
                    # this finite set, hence surjective; every regular
                    # element is already a unit, including in nonreduced rings.
                    return OwnedRings().Mor(self, self).identity()
                if self in OwnedIntegralDomains():
                    return self.fraction_field_map()
                morphism = self._total_quotient_map_decision()
                assert morphism is not None, (
                    f"the total quotient ring of {self} is defined, but no regular-element localization "
                    "computation is available for this ring"
                )
                return morphism

            def total_quotient_ring(self):
                r"""Return ``Q(R) = S^{-1}R`` for ``S`` the regular elements of ``R``.

                Inverting every non-zerodivisor is the largest localization that
                stays injective on ``R``, which is what a Cartier divisor and a
                rational function are stated in.  Over an integral domain the
                regular elements are exactly the nonzero ones, so ``Q(R)`` is
                the fraction field.
                """

                return self.total_quotient_map().codomain()

        class ElementMethods:
            def _regularity_decision(self):
                r"""Supply the magma regularity predicate by ring ideal computations.

                Multiplication by ``r`` is injective exactly when nothing
                nonzero is killed by it, that is when the colon ideal
                ``(0 : r)`` is zero.  Over a domain that reduces to being
                nonzero, which is a theorem about domains rather than a second
                definition. In the zero ring its sole element is regular,
                since its multiplication map on the singleton is injective.
                """

                ring = self.parent()
                if (ring.one() == ring.zero()) is True:
                    return True
                if ring in OwnedIntegralDomains():
                    return negation(self.is_zero())
                zero_ideal = ring.ideal(ring.zero())
                return zero_ideal.colon(ring.ideal(self)) == zero_ideal

    class ParentMethods:
        def __iter__(self):
            r"""Enumerate the points of a finite owned ring through its selected engine.

            Ring adjunction syntax is implemented by ``__getitem__`` and is
            not an enumeration protocol. For a finite ring, the selected
            engine already enumerates the underlying points; expose those
            points as owned elements instead of allowing Python's sequence
            fallback to repeatedly return the ring itself.
            """
            from sage_extensions.categories.sets.set_categories import FiniteSets

            if self not in FiniteSets():
                raise TypeError(f"cannot enumerate {self}: it is not placed among finite sets")
            engine = self._selected_engine_ring()
            if engine is None or engine is self:
                raise TypeError(f"cannot enumerate {self}: no selected finite engine enumeration is available")
            return iter(_owned_engine_element(self, point) for point in engine)

        @cached_method
        def as_ZZ_algebra(self):
            r"""Read this unital ring with its unique central integer action.

            The map sends ``n`` to ``n*1``. Its nonnegative part is the
            existing initial semiring map, and additive inverses determine
            its values on negative integers. This applies to noncommutative
            rings and the zero ring, without a centre computation or a
            selected foreign engine. An existing selected ZZ-algebra keeps
            its literal parent and scalar data.
            """
            from sage_extensions.categories.algebras.algebras import Algebras

            integers = _owned_integers()
            if self.base_ring() is integers and self in Algebras(integers).Associative().Unital():
                return self
            natural_map = OwnedSemirings().initial_morphism(self)

            def image(integer):
                value = int(integer)
                return natural_map(value) if value >= 0 else -natural_map(-value)

            return OwnedRings().Mor(integers, self)(image).as_algebra()

        def _integral_domain_decision(self):
            return AtomicProposition("is_integral_domain", self)

        def is_integral_domain(self):
            r"""Return whether this is a nonzero commutative ring without zero divisors."""
            match self:
                case _ if self in OwnedIntegralDomains():
                    return True
                case _ if self in OwnedRings().NoZeroDivisors().Commutative():
                    return negation(self.one() == self.zero())
                case _:
                    return self._integral_domain_decision()

        def is_noetherian(self):
            r"""Return whether the left regular module is Noetherian."""
            return True if self in OwnedRings().Noetherian() else AtomicProposition("is_noetherian", self)

        def is_artinian(self):
            r"""Return whether the left regular module is Artinian."""
            return True if self in OwnedRings().Artinian() else AtomicProposition("is_artinian", self)

        def is_local(self):
            return True if self in OwnedRings().Commutative().Local() else AtomicProposition("is_local", self)

        def _field_decision(self):
            return AtomicProposition("is_field", self)

        def is_field(self):
            match self:
                case _ if self in OwnedRings().Division().Commutative():
                    return True
                case _:
                    return self._field_decision()

        def _selected_local_ring_construction(self):
            r"""Return selected local-ring quotient data, or ``None``.

            Protected ring-construction contract under OWN-05. The callers
            are the local-ring datum accessor, the local field decision,
            and the local-ring installation adapter. A construction owner returns
            a ``LocalRingConstruction`` for this exact ring: its selected
            maximal ideal, the owned residue field, and its quotient map when
            selected. The local field decision uses the ideal's zero predicate
            only when that datum is an owned commutative ideal.
            Fixed factories may compute these data independently on demand.
            ``None`` means no such datum is selected; it does not deny locality.
            Native/completed parents retain installed values, while a prime
            localization supplies its actual source-quotient construction.
            """
            return None

        def _selected_engine_ring(self):
            r"""Return the private computation parent selected for this ring.

            Protected ring-realization contract under OWN-05--07. Permitted
            callers are the ring owner's lowering/raising dispatchers,
            ring-local computation adapters, and the existing cardinality
            and selected-presentation field-rank/Smith computation suppliers.
            The canonical coefficient-map selector and scalar-action algebra
            view constructor may retain this optional realization as well.
            These optional suppliers retain ``None`` when a construction
            has no selected model; required engine computations enter through
            ``_engine_ring``, which asserts at that frontier. No model is
            queried to infer a mathematical category. A ring with no separate foreign
            realization computes in its owned parent itself; engine-backed
            constructions override this method at their construction owner.
            Raw computation parents never leave those adapters.
            """
            return self

        def _engine_element(self, element):
            r"""Lower an owned element for a self-realized ring adapter."""
            return self(element)

        def _from_engine_element(self, element):
            r"""Raise a self-realized computation value into this ring."""
            return self(element)

        def _fresh_free_module_on(self, labels, **options):
            r"""Return the free ``R``-module on ``labels``, for this ring ``R``.

            A ring that is also a free module over a smaller base -- a number
            field over the rationals, an order over the integers -- is still
            the ring its modules are over here; the free modules over the
            smaller base are asked of that base.
            """
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                _fresh_free_module_on,
            )

            return _fresh_free_module_on(
                self,
                labels,
                **options,
            )

        def free_module(self, rank_or_index_set):
            r"""Return the canonical free module over this ring on the stated labels."""
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                _module_generating_set,
                _owned_free_module_on,
            )

            return _owned_free_module_on(
                self,
                _module_generating_set(rank_or_index_set),
            )

        def polynomial_ring(self, variables):
            r"""``R[S]``, the polynomial ring over this ring on the set ``S`` of variables.

            ``variables`` is a string of comma-separated names, a tuple of
            names, or a set; ``R[S]`` is ``Sym_R(F_R(S))``, one object for
            ``(R, S)``.
            """
            from sage_extensions.categories.algebras.free_algebras import (
                _polynomial_ring,
            )

            return _polynomial_ring(self, variables)

        @RealizationHook
        def _quotient_ring_construction(self, ideal):
            r"""Protected selected quotient by a two-sided ideal, or None.

            Only quotient_ring calls this hook. Its ideal or represented
            generator input is interpreted in this exact ring. A supplier
            retains the two-sided ideal, the quotient ring and its canonical
            source map with that kernel. An arbitrary left ideal does not
            suffice. None means that no such quotient construction is
            represented; no smaller mathematical input domain is inferred.
            """
            return None

        def quotient_ring(self, ideal):
            r"""Return the unital quotient ring by the specified two-sided ideal.

            The additive quotient carries multiplication because the ideal
            absorbs multiplication from both sides. Its canonical map has
            this exact source and the given ideal as kernel; commutativity
            is unnecessary. Selected generator input denotes its generated
            two-sided ideal. A mere left ideal does not define a quotient ring.
            """
            result = self._quotient_ring_construction(ideal)
            assert result is not None, (
                f"the quotient ring of {self} by a two-sided ideal is defined, "
                "but this exact ideal and canonical-map construction is not represented"
            )
            return result

        @RealizationHook
        def _adic_completion_construction(self, ideal, precision):
            r"""Protected selected inverse limit of the quotients ``R/I^n``, or None.

            Only adic_completion calls this hook. The input is a represented
            two-sided ideal (or its generator input) of this exact ring and
            the requested computation precision. A supplier retains the
            source, ideal, canonical completion map and quotient projections.
            Completeness for the extended ideal is a separate assertion;
            it is not inferred for arbitrary infinitely generated ideals.
            None supplies no selected inverse-limit computation.
            """
            return None

        def adic_completion(self, ideal, precision=20):
            r"""Return ``lim_n R/I^n`` for the specified two-sided ideal.

            Every transition and source map is a unital ring map; this
            definition needs no commutativity. Precision selects computation
            data for that limit. Identifying its inverse-limit topology with
            the topology of the extended ideal requires further hypotheses;
            the returned construction carries only established refinements.
            """
            result = self._adic_completion_construction(ideal, precision)
            assert result is not None, (
                f"the adic inverse limit of {self} is defined for a two-sided "
                "ideal, but this source, ideal and completion-map construction is not represented"
            )
            return result

        def laurent_polynomial_ring(self, *args, **kwargs):
            r"""Return the Laurent polynomial ring over this ring with the stated variables."""
            from sage_extensions.categories.algebras.free_algebras import (
                _laurent_polynomial_ring,
            )

            return _laurent_polynomial_ring(self, *args, **kwargs)

        def power_series_ring(self, *args, **kwargs):
            r"""Return the formal power-series ring over this ring."""
            from sage_extensions.categories.rings.commutative_algebra import (
                FormalPowerSeriesRings,
            )

            return FormalPowerSeriesRings(self)(*args, **kwargs)

        def matrix_space(self, nrows, ncols=None):
            r"""Return the finite matrix Mor over this ring, as an algebra when square."""
            from sage_extensions.categories.algebras.algebras import (
                _require_matrix_algebra,
            )
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                _matrix_space,
            )

            return _require_matrix_algebra(_matrix_space(self, nrows, ncols))

        def formal_spectrum(self, ideal_of_definition):
            r"""Return ``Spf(self, ideal_of_definition)``."""
            from sage_extensions.categories.schemes.formal_schemes import (
                FormalSpectrum,
            )

            return FormalSpectrum(self, ideal_of_definition)

        def cyclic_cover_presentation(self, branch_coefficient, degree):
            r"""Return ``self[z]/(z^degree - branch_coefficient)``."""
            from sage_extensions.categories.algebras.cyclic_cover_algebras import (
                _cyclic_cover_presentation,
            )

            return _cyclic_cover_presentation(self, branch_coefficient, degree)

        def __pow__(self, exponent):
            r"""Return the free module ``R^n`` through the owned module constructor."""

            return self.free_module(exponent)

        @cached_method
        def regular_module(self):
            r"""Return ``{}_R R``, the rank-one left regular module.

            The ring remains the scalar object; the module is the canonical
            free rank-one object on which ``r`` acts by left multiplication.
            If this ring already carries that canonical finite-free module
            structure, the regular module is the ring itself; otherwise it is
            the canonical rank-one based free module over this ring.
            """
            from sage_extensions.categories.modules.pure.modules import (
                FinitelyGeneratedFreeModules,
            )

            if self in FinitelyGeneratedFreeModules(self):
                return self
            return self.free_module(1)

        @cached_method
        def regular_module_isomorphism(self):
            r"""Return the additive isomorphism ``{}_R R -> R``, ``r e_0 |-> r``.

            It sends the module generator ``e_0`` of :meth:`regular_module` to
            ``1`` and intertwines the scalar action with left multiplication,
            ``r (s e_0) |-> r s``.  When the regular module is the ring itself
            it is the identity.
            """
            from sage_extensions.categories.group.magmas import AdditiveGroups

            module = self.regular_module()
            morphisms = AdditiveGroups().AdditiveCommutative().Mor(module, self)
            match module is self:
                case True:
                    return morphisms.elementwise(lambda element: element)
                case False:
                    label = next(iter(module.module_generating_set()))
                    return morphisms.elementwise(
                        lambda element: self(module.framing_morphism().lift(element)(label))
                    )

        def _module_basis_along(self, ring_map):
            r"""A basis of ``Res_f(S)`` over ``R`` for ``f = ring_map: R -> S = self``, or ``None``.

            Protected ring contract (``OWN-05``).  Purpose: restriction of
            scalars frames ``Res_f(M)`` by the products ``s_i m_j`` of a basis
            ``(s_i)`` of ``S`` over ``R`` along ``f`` with a framing ``(m_j)`` of
            ``M`` over ``S``.  ``Res_f(S)`` is itself the object under
            construction there, so it has no public framing to ask; the basis
            comes from how ``S`` is realized, which only ``S`` may read.

            Implementers are ring owners: this default, and the owners whose
            realization supplies a basis along a coefficient map
            (``QuotientRings``, ``OwnedNumberFields``).  Callers are
            ``_restricted_scalars_view`` and ``RestrictedScalarsModules``.

            The result is a ``_NativeModuleBasis``.  Its source is a free
            ``R``-module ``F_R(I)`` with a chosen basis, ``image(i)`` is
            ``s_i`` in ``S``, and ``coordinates(s)`` is the finitely supported
            ``{i: c_i}`` with ``c_i`` in ``R`` and ``s = sum_i f(c_i) s_i``,
            unique for each ``s``.  ``None`` states that no basis along this
            ``f`` is selected, never that ``Res_f(S)`` is not free.

            The default is the basis of ``S`` as an ``R``-algebra framed over
            ``R``, when ``f`` is its structure morphism ``R -> Z(S) -> S``.
            """
            from sage_extensions.categories.algebras.algebras import Algebras
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                FramedFreeModules,
            )
            from sage_extensions.categories.modules.native_modules import (
                _NativeModuleBasis,
            )

            scalars = _owned_ring(ring_map.domain())
            native_basis = self._native_module_basis
            if (
                native_basis is not None
                and native_basis.is_basis()
                and self.base_ring() is scalars
                and native_basis.source().base_ring() is scalars
            ):
                # A unital map out of a prime field (or Z) is unique. This
                # lets native polynomial/number-field bases answer during
                # Parent construction without recursively asking for the
                # algebra structure map whose selected resolution is not yet
                # installed.
                if scalars in PrimeFields() or scalars is _owned_integers():
                    return native_basis
                associative_unital = Algebras(scalars).Associative().Unital()
                if not (
                    self.has_selected_resolution(associative_unital)
                    or self.has_selected_resolution(associative_unital.Commutative())
                ):
                    return None
                structure = self.algebra_structure_morphism()
                center = structure.codomain()
                coefficient_map = structure if center is self else center.inclusion() * structure
                if _ring_morphisms_equal(ring_map, coefficient_map):
                    # The native ring owner may have selected a module basis
                    # independently of its algebra-generator resolution.
                    # Prefer that actual F_R(I) -> S framing here; an algebra
                    # resolution's source is a free algebra, not a module
                    # basis and cannot be used as the restricted-scalar frame.
                    return native_basis
            associative_unital = Algebras(scalars).Associative().Unital()
            algebra_resolution_selected = (
                self.has_selected_resolution(associative_unital)
                or self.has_selected_resolution(associative_unital.Commutative())
            )
            match (
                self.base_ring() is scalars
                and self in FramedFreeModules(scalars)
                and self in associative_unital
                and algebra_resolution_selected
            ):
                case False:
                    return None
            structure = self.algebra_structure_morphism()
            center = structure.codomain()
            coefficient_map = structure if center is self else center.inclusion() * structure
            match _ring_morphisms_equal(ring_map, coefficient_map):
                case True:
                    framing = self.framing_morphism()

                    def coordinates(element):
                        vector = framing.lift(element)
                        return {label: vector(label) for label in vector.support().domain()}

                    return _NativeModuleBasis(self.framing_source(), self.module_generator, coordinates)
                case _:
                    return None

        def __getitem__(self, names):
            r"""Use standard polynomial/algebraic adjunction syntax on an owned ring."""
            from sage_extensions.categories.algebras.group_algebras import (
                _group_algebra,
            )
            from sage_extensions.categories.group.groups import OwnedGroups

            match names:
                case str():
                    return self.polynomial_ring(names)
                case _ if names in OwnedGroups():
                    return _group_algebra(self, names)
                case tuple() if all(isinstance(part, str) for part in names):
                    return self.polynomial_ring(names)
                case list():
                    result = _own_if_ring(_engine_ring(self)[names])
                case _ if names in self:
                    return self
                case _:
                    result = _own_if_ring(_engine_ring(self)[names])

            if result not in OwnedRings():
                return result
            return result

        def predicate_subring(self, predicate, description, category=None):
            r"""Return the represented subring of elements satisfying ``predicate``."""
            return _predicate_subring(self, predicate, description, category)

        @object_level
        def Mor(self, codomain, category=None):
            rings = OwnedRings()
            if category is None:
                # ``A.Mor(B) := A.ambient_category().Mor(A, B)`` (``ARC-07``).
                return super().Mor(codomain)
            if isinstance(category, OwnedCategory) and category.is_subcategory(rings):
                return rings.Mor(self, codomain)
            # A Sage category here is not a mathematical request: it is Sage's
            # coercion machinery asking for somewhere to keep a conversion map,
            # naming its own `SetsWithPartialMaps`.  `SageHom` would check that
            # this owned ring lies in that Sage category, which it does not and
            # need not (`ARC-00`).  Build the Mor directly at the engine
            # boundary instead, without the membership check.
            from sage.categories.homset import Homset as SageHomset

            return SageHomset(self, codomain, category=category, check=False)

        def _Hom_(self, codomain, category=None):
            rings = OwnedRings()
            if codomain not in rings:
                raise TypeError(
                    f"Mor({self}, {codomain}) in the category of rings needs a ring as codomain, but {codomain} is not a ring"
                )
            if category is not None and not category.is_subcategory(rings):
                raise TypeError(
                    f"{category} is not a subcategory of rings, so Mor({self}, {codomain}) cannot be formed in it"
                )
            return rings.Mor(self, codomain)

        @RealizationHook
        def _cardinality_decision(self):
            r"""Return the exact represented cardinal of the underlying set."""
            from sage_extensions.categories.sets.cardinals import (
                aleph0,
                cardinal,
            )

            engine = self._selected_engine_ring()
            if isinstance(engine, QuotientRing_generic) and engine.defining_ideal().is_one():
                return cardinal(1)
            category = self.category()
            match category:
                case _ if category.is_subcategory(owned_sets.FiniteSets()):
                    from sage.rings.integer_ring import ZZ as SageZZ

                    engine = self._selected_engine_ring()
                    if engine is None or engine is self:
                        # A finite ring can be realized on its own module
                        # data. Its inherited cardinality is this operation,
                        # so only a distinct selected engine supplies a
                        # native count here.
                        return super()._cardinality_decision()
                    integers = _owned_integers()
                    return cardinal(
                        _owned_engine_element(
                            integers,
                            SageZZ(engine.cardinality()),
                        )
                    )
                case _ if category.is_subcategory(owned_sets.CountablyInfiniteSets()):
                    return aleph0
                case _:
                    # No size placement on the ring: its underlying set may still be
                    # constructed at a lower level, as M_n(R) is the free module R^(n^2).
                    return super()._cardinality_decision()

        def _has_selected_exact_coefficient_presentation(self) -> bool:
            r"""Return whether this ring carries a nontrivial selected exact presentation.

            Module algorithms use this capability without knowing which higher
            mathematical structure supplied the presentation.
            """
            return False

        def _exact_coefficient_presentation_ring(self):
            r"""Return the owned ring in which coefficient computations are lifted."""
            return self

        def _exact_coefficient_presentation_relations(self):
            r"""Return the selected coefficient relations in the computation ring."""

            return owned_sets.finite_ordered_set(())

        def _lift_coefficient_to_presentation(self, value):
            return self(value)

        def _descend_coefficient_from_presentation(self, value):
            return self(value)

        def is_central(self, element):
            r"""Return whether ``element`` commutes with every element of this ring.

            In a framed algebra it is enough to commute with the selected
            algebra generators: scalar coefficients are central and the
            commuting relation is preserved by sums and products.  In an
            endomorphism algebra a map ``r id`` represented in that exact
            algebra's scalar action is central because every admitted ``h``
            satisfies ``h(r x) = r h(x)``. A scalar map for a stronger module
            theory does not establish centrality in a weaker additive End.
            """
            match element in self:
                case False:
                    return False
                case True:
                    element = self(element)

            from sage_extensions.categories.algebras.algebras import Algebras

            match self:
                case _ if self in OwnedRings().Commutative():
                    return True
                case _ if self in Algebras(self.base_ring()) and self.is_framed_algebra():
                    labels = self.algebra_generating_set()
                    if not labels.cardinality().is_finite():
                        return AtomicProposition("is_central", self, element)
                    return conjunction(
                        element * self.algebra_generator(label)
                        == self.algebra_generator(label) * element
                        for label in labels
                    )
                case _:
                    from sage_extensions.categories.group.additive_mors import (
                        AdditiveEndomorphismRings,
                        _scalar_identity_coefficient,
                    )

                    match self:
                        case _ if self in AdditiveEndomorphismRings(self.base_ring()) and _scalar_identity_coefficient(element, self) is not None:
                            return True
                        case _:
                            assert False, (
                                f"centrality is defined for every element of {self}, but the current preamble "
                                "computes it only for commutative rings, framed algebras, and represented scalar "
                                "endomorphisms"
                            )

        @cached_method
        def ring_center(self):
            r"""Return the centre ``Z(R)`` as a predicate-defined subring."""
            if self in OwnedRings().Commutative():
                return self
            return self.predicate_subring(
                self.is_central,
                "z commutes with every element",
                OwnedRings().Commutative(),
            )


class OwnedOrderedRings(OwnedCategory):
    r"""Rings with a chosen total order compatible with the operations.

    A ring can support several orders (a real quadratic field has two), so
    the order is a chosen datum.
    """

    def an_object(self):
        r"""The integers with their usual order."""
        return _owned_integers()

    def super_categories(self):
        return [OwnedRings()]

    class ElementMethods:
        def __abs__(self):
            zero = self.parent().zero()
            return self if self >= zero else -self


def OwnedIntegralDomains():
    r"""The nontrivial commutative rings satisfying the zero-product axiom."""
    return OwnedRings().Commutative().NoZeroDivisors().Nontrivial()


def OwnedPrincipalIdealDomains():
    r"""The integral domains in which every ideal is principal."""
    return OwnedIntegralDomains().PrincipalIdeals()


def _engine_krull_dimension(ring):
    engine = _engine_ring(ring)
    assert engine is not ring, (
        f"no exact Krull-dimension algorithm is selected for the retained realization of {ring}"
    )
    return _krull_dimension_of_engine(engine)


def _krull_dimension_of_engine(engine):
    r"""The Krull dimension of a Sage computation ring, as an owned integer.

    ``OWN-06`` adapter.  Sage answers ``krull_dimension`` itself on every
    engine but one: the generic quotient ``S/I`` of a multivariate polynomial
    ring falls to the ``CommutativeRings`` default, which raises.  There
    ``dim S/I = dim I``, the dimension Singular computes for ``I`` (TRAPS.md).
    A nonzero quotient of a principal ideal domain ``D/(d)`` has dimension
    zero for nonzero, nonunit ``d``, and the dimension of ``D`` for ``d = 0``.
    The empty spectrum has dimension -infinity (Stacks, Tags 0055 and 00KD),
    for which this finite-integer adapter provides no owned representation.
    A univariate quotient ``K[x]/(f)`` answers its own.
    """
    assert (engine.one() == engine.zero()) is not True, (
        "the empty prime spectrum has Krull dimension -infinity; "
        "an owned extended-dimension representation is not yet supplied"
    )
    match engine:
        case PolynomialQuotientRing_generic():
            dimension = engine.krull_dimension()
        case QuotientRing_generic():
            cover = engine.cover_ring()
            defining = engine.defining_ideal()
            match cover in SagePrincipalIdealDomains(), defining.is_zero():
                case (True, True):
                    dimension = cover.krull_dimension()
                case (True, False):
                    dimension = SageZZ.zero()
                case _:
                    dimension = defining.dimension()
        case _:
            dimension = engine.krull_dimension()
    assert dimension not in (SageInfinity, -SageInfinity) and dimension >= 0, (
        "this Krull dimension requires an owned extended-dimension representation; "
        "the selected adapter currently represents finite nonnegative dimensions"
    )
    return _owned_engine_element(SageZZ, SageZZ(dimension))


def OwnedNoetherianRings():
    r"""The session shorthand for commutative Noetherian rings."""
    return OwnedRings().Commutative().Noetherian()


def OwnedArtinianRings():
    r"""The session shorthand for commutative Artinian rings."""
    return OwnedRings().Commutative().Artinian()


def OwnedLocalRings():
    r"""``OwnedRings().Commutative().Local()``, the session name for local rings."""
    return OwnedRings().Commutative().Local()


class OwnedAdicallyCompleteRings(OwnedCategory):
    r"""Commutative rings with a chosen ideal of definition for which they are adically complete.

    The ideal is a chosen datum: every ring is complete for its zero ideal.
    The inherited arrows are unital ring maps; no continuity condition is
    imposed on this category's ``Mor``.
    """

    def an_object(self):
        r"""The 2-adic integers, complete for the ideal (2)."""
        return _owned_integers().adic_completion(2)

    def super_categories(self):
        return [OwnedRings().Commutative()]

    class ParentMethods:
        def is_adically_complete(self):
            r"""Return the completeness supplied by this chosen adic structure."""
            return True

        @RealizationHook
        def _selected_adic_defining_ideal(self):
            r"""Supply the selected defining ideal of this exact ring, or ``None``.

            Only ``ideal_of_definition`` calls this protected datum supplier.
            A complete-local category supplies its actual maximal ideal by
            default. An owned completion realization supplies the extension
            of its fixed source ideal along its fixed completion map, using
            the existing cached ideal-extension construction. These are
            evaluations of already selected data, not choices of topology
            made by this accessor. An explicit supplier takes precedence
            over the complete-local default; its ``None`` means that its
            selected datum is unavailable, never that the maximal ideal
            should be substituted.
            """
            return None

        def ideal_of_definition(self):
            r"""Return the selected defining ideal as an owned ideal of ``self``."""
            from sage_extensions.categories.rings.commutative_ideals import (
                CommutativeIdeals,
            )

            selected = self._selected_adic_defining_ideal()
            assert selected is not None, (
                f"the selected adic structure of {self} has no supplied defining ideal"
            )
            assert selected in CommutativeIdeals(self) and selected.ring() is self, (
                f"the defining ideal of the selected adic structure of {self} must be "
                f"an owned ideal of that ring, but the supplied datum is {selected}"
            )
            return selected


def OwnedCompleteLocalRings():
    r"""``OwnedRings().Commutative().Local().Complete()``, the session name for complete local rings."""
    return OwnedRings().Commutative().Local().Complete()


def OwnedDivisionRings():
    r"""``OwnedRings().Division()``, the session name for division rings."""
    return OwnedRings().Division()


def OwnedFields():
    r"""``OwnedRings().Division().Commutative()``, the session name for fields."""
    return OwnedRings().Division().Commutative()


class OwnedOrders(CategoryPacketMethods, OwnedCategory):
    r"""Orders: integral domains finitely generated as ``ZZ``-modules (Neukirch I §12).

    The number field is ``Frac(O) = O (x) QQ``, determined by the ring, and
    the category is the intersection of its two declared supercategories:
    finite generation is the module axiom on the ring as a ``ZZ``-algebra.
    The class is the home of the operations of orders (their embeddings, the
    adjunction with number fields, maximality); it adds no condition.
    """

    class _MorCategory(MorCategoryConstruction):
        def fixed_category_class(self):
            from sage_extensions.categories.rings.embeddings import OrderMor

            return OrderMor

    def an_object(self):
        r"""The integers, the ring of integers of the rationals."""
        return _owned_integers()

    def super_categories(self):
        from sage_extensions.categories.algebras.algebras import Algebras

        return [
            Algebras(_owned_integers()).Associative().Unital().Commutative().FinitelyGenerated(),
            OwnedIntegralDomains().Noetherian(),
        ]

    def fraction_field_adjunction(self):
        r"""Return ``Frac -| O`` from orders to number fields."""
        from sage_extensions.categories.functors.orders_number_fields import (
            _order_number_field_adjunction,
        )

        return _order_number_field_adjunction()

    @cached_method(key=lambda self, domain, codomain: (id(domain), id(codomain)))
    def Mor(self, domain, codomain):
        r"""Return the exact embedding Mor between two represented orders."""
        if domain not in self or codomain not in self:
            raise TypeError(
                f"an embedding of orders needs an order as domain and codomain, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    class ParentMethods:
        @object_level
        def Mor(self, codomain, category=None):
            orders = OwnedOrders()
            if codomain in orders and (
                category is None
                or (
                    isinstance(category, OwnedCategory)
                    and category.is_subcategory(orders)
                )
            ):
                return orders.Mor(self, codomain)
            return super().Mor(codomain, category=category)

        def _Hom_(self, codomain, category=None):
            orders = OwnedOrders()
            if codomain in orders and (
                category is None
                or (
                    isinstance(category, OwnedCategory)
                    and category.is_subcategory(orders)
                )
            ):
                return orders.Mor(self, codomain)
            return super()._Hom_(codomain, category=category)

        def is_maximal(self) -> bool:
            r"""Return whether this is the maximal order of its fraction field."""
            engine = _engine_ring(self)
            if engine is SageZZ:
                return True
            return bool(engine.is_maximal())


def PrimeFields():
    r"""``OwnedRings().Division().Commutative().Prime()``, the session name for prime fields."""
    return OwnedRings().Division().Commutative().Prime()


def _center_transport_of_ring_isomorphism(morphism):
    r"""Restrict one ring isomorphism direction to represented centers."""
    source = morphism.domain()
    target = morphism.codomain()
    source_center = source.ring_center()
    target_center = target.ring_center()

    def ambient_source(element):
        if source_center is source:
            return source(element)
        return source_center.inclusion()(element)

    return source_center.Mor(target_center)(
        lambda element: target_center(morphism(ambient_source(element))),
    )


class RingCenterFunctor(Functor):
    r"""The ring center functor on the maximal subgroupoid of owned rings.

    A general ring morphism need not preserve centers.  An isomorphism does:
    if ``f : R -> S`` is invertible, ``z`` commutes with every element of
    ``R``, and ``s in S``, then writing ``s=f(r)`` gives
    ``f(z)s=f(zr)=f(rz)=sf(z)``.  Thus the center construction is functorial
    exactly on the core without a generator or surjectivity heuristic.
    """

    def __init__(self) -> None:
        core = OwnedRings().Core()
        super().__init__(core, CommutativeRings())

    def _apply_object(self, ring):
        return ring.ring_center()

    def _apply_morphism(self, isomorphism):
        return _center_transport_of_ring_isomorphism(isomorphism.forward())

    def _repr_(self):
        return "Ring center functor Core(Ring) -> CRing"


class OwnedCategoryOverBaseRing(CategoryPacketMethods, OwnedParameterizedCategory):
    r"""A category over a ring, normalized to the session's owned ring."""

    def parameter_category(self):
        r"""Return the mathematical domain of the base-ring parameter."""
        return OwnedRings()

    @classmethod
    def an_instance(cls):
        r"""Return this category over the rational numbers.

        Sage's ``Category_over_base.an_instance`` (category_types.py) returns
        ``cls(QQ)``; here ``QQ`` is the owned rational field.
        """
        return cls(_owned_rationals())

    @staticmethod
    def __classcall__(cls, base_ring, *args, **kwargs):
        # During construction of an engine-backed owned ring, ``self`` already
        # exists and already carries its engine, but ``Parent.__init__`` has not
        # yet installed its category.  A self-referential placement such as
        # ``Algebras(R).Associative().Unital().Commutative()`` must therefore accept that constructing
        # parent directly rather than asking category membership of an object
        # whose category is precisely what is being built.
        match base_ring:
            case _OwnedRingBootstrapParent():
                pass
            case _:
                base_ring = _owned_ring(base_ring)
        return OwnedParameterizedCategory.__classcall__(
            cls,
            base_ring,
            *args,
            **kwargs,
        )

    def __init__(self, base_ring) -> None:
        match base_ring:
            case _OwnedRingBootstrapParent():
                # The host type is itself the owned-ring construction.  During
                # its bootstrap the category being built is precisely what
                # will establish ``base_ring in OwnedRings()``; asking that
                # membership here would make the declaration depend on its
                # own result.  Fix the parameter and construct the category
                # without re-asking the theorem under construction.
                self._owned_parameter = base_ring
                OwnedCategory.__init__(self)
            case _:
                OwnedParameterizedCategory.__init__(self, base_ring)

    def base_ring(self):
        return self.base()

def _cross_engine_ring_value(value):
    r"""Cross a private engine-ring value back into the owned universe when possible."""
    parent = element_parent(value)
    if parent in SageRings():
        return _owned_engine_element(parent, value)
    return value


class OwnedFactorization(SageObject):
    r"""A finite factorization retaining its unit and factor multiplicities."""

    def __init__(self, parent, unit, factors) -> None:
        self._parent = parent
        self._unit = _owned_engine_element(parent, unit)
        engine_pairs = tuple(factors)
        owned_factors = tuple(
            _owned_engine_element(parent, factor) for factor, _multiplicity in engine_pairs
        )
        indices = owned_sets.finite_ordered_set(owned_factors)
        multiplicities = {
            factor: _owned_engine_element(SageZZ, SageZZ(multiplicity))
            for factor, (_engine_factor, multiplicity) in zip(
                owned_factors, engine_pairs, strict=True
            )
        }
        self._factors = owned_sets.finite_indexed_family(
            indices,
            multiplicities.__getitem__,
            name=f"Factor multiplicities in {parent}",
        )

    def parent_ring(self):
        return self._parent

    def unit(self):
        return self._unit

    def factor_multiplicities(self):
        return self._factors

    def cardinality(self):
        return self._factors.cardinality()

    def items(self):
        return self._factors.items()

    def reconstruct(self):
        product = self.unit()
        for factor, multiplicity in self.items():
            product = product * factor ** int(multiplicity)
        return product

    def _repr_(self):
        return f"Factorization of an element of {self.parent_ring()}"


def _proper_restriction_base_ring(ring):
    r"""Return the next proper scalar base in the represented ring tower.

    A represented ring keeps its distinguished construction base through
    ``base_ring()``.  When that base is the ring itself, the canonical map
    from the initial ring still makes every module or algebra over it a module
    or algebra over ``ZZ``.  The integers are the terminal case and therefore
    have no proper restriction base.

    The engine test is essential while ``ZZ`` itself is being constructed:
    asking ``_owned_integers()`` again before its cache entry exists would
    recursively start a second construction of the same parent.
    """
    base = ring.base_ring()
    if base is None:
        return None if _engine_ring(ring) is SageZZ else _owned_integers()
    if base is not ring:
        return _owned_ring(base)
    if _engine_ring(ring) is SageZZ:
        return None
    return _owned_integers()


def _engine_multiplicative_generator(engine):
    r"""Return the selected engine's multiplicative generator at the private boundary."""
    return engine.multiplicative_generator()



def _owned_monomial_text(variable_names, exponent):
    # A univariate engine polynomial keys its terms by an integer exponent, a
    # multivariate one by an exponent vector (Sage's ETuple), including a
    # multivariate ring in one variable; the key's representation decides.
    from sage.rings.polynomial.polydict import ETuple

    match exponent:
        case ETuple():
            powers = tuple(exponent)
        case _:
            powers = (exponent,)
    factors = []
    for variable, power in zip(variable_names, powers, strict=False):
        power = int(power)
        if power == 0:
            continue
        factors.append(variable if power == 1 else f"{variable}^{power}")
    return "*".join(factors) or "1"


def _owned_polynomial_text(parent, backend_value) -> str:
    r"""A polynomial written as Sage writes it: terms in descending term order.

    Sage's reference is ``PolyDict.poly_repr`` (``sage/rings/polynomial/
    polydict.pyx``), which sorts the exponents by the ring's
    ``term_order().sortkey`` in reverse; a univariate polynomial is written by
    descending degree.  Engine-convention dispatch (``OWN-06``): a
    multivariate engine ring carries a term order, a univariate one does not.
    Each term is written as ``Polynomial._repr`` (``sage/rings/polynomial/
    polynomial_element.pyx``) writes it, and ``+ -`` is written ``-``.
    """
    base = parent.base_ring()
    variables = tuple(parent.variable_names())
    engine = backend_value.parent()
    match engine:
        case MPolynomialRing_base():
            sortkey = engine.term_order().sortkey
        case _:
            sortkey = None
    atomic = engine.base_ring()._repr_option("element_is_atomic")
    coefficients = backend_value.dict()
    terms = []
    for exponent in sorted(coefficients, key=sortkey, reverse=True):
        coefficient = _owned_engine_element(base, coefficients[exponent])
        monomial = _owned_monomial_text(variables, exponent)
        terms.append(_owned_term_text(coefficient, monomial, atomic))
    return " + ".join(terms).replace(" + -", " - ") or "0"


def _owned_term_text(coefficient, monomial: str, atomic: bool) -> str:
    r"""The term ``coefficient*monomial`` as Sage's ``Polynomial._repr`` writes it.

    A coefficient ``1`` or ``-1`` leaves the monomial or its negative.  A
    coefficient whose text past a leading minus holds a ``+`` or ``-`` is a sum
    and is parenthesized, unless the coefficient ring's elements print
    atomically or the term is constant: ``(i + 1)*s`` and ``s + i + 1``, while
    ``-2`` stays bare so that the sum writes ``s - 2``.
    """
    if monomial == "1":
        return repr(coefficient)
    if coefficient.is_one():
        return monomial
    if (-coefficient).is_one():
        return f"-{monomial}"
    text = repr(coefficient)
    unsigned = text.removeprefix("-")
    if not atomic and ("+" in unsigned or "-" in unsigned):
        text = f"({text})"
    return f"{text}*{monomial}"


def _owned_ring_element_text(element) -> str:
    parent = element.parent()
    engine = parent._engine
    value = element._backend()
    if engine is SageZZ:
        return str(int(value))
    if engine is SageQQ:
        numerator = int(value.numerator())
        denominator = int(value.denominator())
        return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"
    if isinstance(engine, (PolynomialRing_generic, MPolynomialRing_base)):
        return _owned_polynomial_text(parent, value)
    kind = parent._preamble_ring_display_kind
    if kind == "modular":
        return f"[{int(value.lift())}]"
    if kind == "real" or kind == "complex" or kind == "symbolic":
        return str(value)
    if parent._preamble_is_number_field():
        return str(value)
    if parent._preamble_is_number_field_order():
        coefficients = tuple(value.list())
        owned = tuple(_cross_engine_ring_value(coefficient) for coefficient in coefficients)
        return f"coordinates {owned} in {parent}"
    if kind == "padic":
        valuation = value.valuation()
        precision = value.precision_absolute()
        residue = value.residue()
        return (
            f"p-adic element with residue {int(residue)}, "
            f"valuation {valuation}, precision {precision}"
        )
    if isinstance(engine, QuotientRing_generic) and isinstance(
        engine.cover_ring(), (PolynomialRing_generic, MPolynomialRing_base)
    ):
        cover = parent.quotient_source()
        return f"[{_owned_polynomial_text(cover, value.lift())}]"
    return f"element of {parent}"


class _OwnedRingElement(RingElement):
    r"""An element of an owned ring with a private backend realization."""

    def __init__(self, parent, backend_value) -> None:
        RingElement.__init__(self, parent)
        self._backend_value = backend_value

    def _backend(self):
        r"""Return the private backend value for boundary code in this module."""
        return self._backend_value

    def _operator_operand(self, value):
        r"""``value`` in this ring along the canonical map, or ``NotImplemented`` for Python dispatch.

        When the canonical map runs from this ring into the other operand's ring
        and not back, the operation lives in the other ring, and
        ``NotImplemented`` lets Python ask the other operand: ``2 * q.one()``
        for a quotient ``q`` of ``QQ[x,y]`` is an element of ``q``, not the
        integer that the lift of ``1`` would convert to.  Otherwise the value
        is read in this ring when it is one of its elements.
        """
        ring = self.parent()
        other_parent = element_parent(value)
        if (
            other_parent is not ring
            and other_parent in OwnedRings()
            and _engine_ring(other_parent).has_coerce_map_from(_engine_ring(ring))
            and not _engine_ring(ring).has_coerce_map_from(_engine_ring(other_parent))
        ):
            return NotImplemented
        if value not in ring:
            return NotImplemented
        return ring(value)
    def _add_(self, other):
        parent = self.parent()
        return _owned_engine_element(parent, self._backend() + other._backend())

    def __add__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return self._add_(other)

    __radd__ = __add__

    def __sub__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return self._add_(-other)

    def __rsub__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return other._add_(-self)

    def _mul_(self, other):
        parent = self.parent()
        return _owned_engine_element(parent, self._backend() * other._backend())

    def _lmul_(self, scalar):
        r"""``r * a`` for ``r`` in the ring this ring is presented over: the engine's own action.

        The engine presents this ring over its base, so ``r`` enters through
        the engine's map from its base and multiplies ``a`` there.  The algebra
        root derives ``algebra_structure_morphism`` from this action as
        ``r |-> rho(r)(1)``, so the action is never read back from it.
        """
        parent = self.parent()
        return parent(parent.base_ring()(scalar)) * self

    def __mul__(self, other):
        r"""``r x`` for a scalar of this ring and an element over it.

        A module over this ring registers the action of this ring on its
        elements, and the host's coercion model finds that action for ``r*m``.
        It finds it only when this method defers, and this method cannot defer
        whenever this ring can convert the other element: the line below would
        then multiply in this ring and answer in it, so ``3`` times the identity
        of the Gaussian field would be the rational three rather than the
        Gaussian three.  A number field, a polynomial ring and every other
        algebra over this ring holds such elements -- the ones this ring already
        names.

        So the scalar action is taken here, on the element's own parent, before
        the conversion is tried.  It is the same operation the registered action
        performs, reached on the one route the coercion model does not see.
        """
        from sage_extensions.categories.modules.pure.modules import Modules

        other_parent = element_parent(other)
        if other_parent is not self.parent() and other_parent in Modules(self.parent()):
            return other_parent.scalar_multiple(self, other)
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return _OwnedRingElement._mul_(self, other)

    def __rmul__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return _OwnedRingElement._mul_(other, self)

    def _neg_(self):
        return _owned_engine_element(self.parent(), -self._backend())

    def _richcmp_(self, other, op):
        if element_parent(other) is not self.parent():
            other = self._operator_operand(other)
            if other is NotImplemented:
                return NotImplemented
        return richcmp(self._backend(), other._backend(), op)

    def _ordered_comparison(self, other, op):
        if self.parent() not in OwnedOrderedRings():
            return NotImplemented
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return bool(richcmp(self._backend(), other._backend(), op))

    def __lt__(self, other):
        return self._ordered_comparison(other, op_LT)

    def __le__(self, other):
        return self._ordered_comparison(other, op_LE)

    def __gt__(self, other):
        return self._ordered_comparison(other, op_GT)

    def __ge__(self, other):
        return self._ordered_comparison(other, op_GE)

    def __eq__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            # Not this ring's decision: a cardinal, say, knows whether it
            # equals a natural number of the ring, so Python asks it next.
            return NotImplemented
        return bool(self._backend() == other._backend())

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

    def __hash__(self):
        # Equal elements hash equally: ``__eq__`` identifies this element with
        # the literal it converts from, so the hash is the value's, as for
        # Sage's own elements (``hash(Integer(1)) == hash(1)``).
        return hash(self._backend())

    def __bool__(self):
        return bool(self._backend())

    def __int__(self):
        return int(self._backend())

    def __float__(self):
        return float(self._backend())

    def __complex__(self):
        return complex(self._backend())

    def _repr_(self):
        return _owned_ring_element_text(self)

    def _coeff_repr(self, no_space=True) -> str:
        r"""This element as a coefficient of a linear combination, its sign outside.

        Sage's ``repr_lincomb`` (``sage/misc/repr.py``) writes ``a - c*m`` when
        the coefficient text starts with ``-`` or ``c < 0``, and an unordered
        ring such as ``QQ(i)`` cannot answer ``c < 0``.  ``Element._coeff_repr``
        (``sage/structure/element.pyx``) parenthesizes ``-2`` because its text
        holds a ``-``; this one parenthesizes only what is a sum past a leading
        minus, as ``Polynomial._repr`` does, so ``-2*e`` is written as a
        subtraction and ``(i+1)*e`` keeps its parentheses.
        """
        text = repr(self)
        unsigned = text.removeprefix("-")
        atomic = self.parent()._repr_option("element_is_atomic") or not (
            "+" in unsigned or "-" in unsigned or " " in unsigned
        )
        if not atomic:
            text = f"({text})"
        return text.replace(" ", "") if no_space else text

    def _latex_(self):
        text = _owned_ring_element_text(self).replace("_", r"\_")
        return rf"\text{{{text}}}"

    def is_zero(self):
        return bool(self._backend() == self.parent()._engine.zero())

    def is_one(self):
        return bool(self._backend() == self.parent()._engine.one())

    def _unit_decision(self):
        return bool(self._backend().is_unit())

    def _unit_inverse_decision(self):
        match self.is_unit():
            case True:
                pass
            case False:
                raise ZeroDivisionError(f"{self} is not a unit")
            case _:
                return None
        return _owned_engine_element(self.parent(), self._backend() ** -1)

    def __invert__(self):
        return _owned_engine_element(self.parent(), ~self._backend())

    def __mod__(self, other):
        r"""The remainder of Euclidean division by ``other``, as the engine ring computes it."""
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return _owned_engine_element(self.parent(), self._backend() % other._backend())

    def __rmod__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        return _owned_engine_element(self.parent(), other._backend() % self._backend())

    def __truediv__(self, other):
        other = self._operator_operand(other)
        if other is NotImplemented:
            return NotImplemented
        value = self._backend() / other._backend()
        value_parent = element_parent(value)
        if value_parent is self.parent()._engine:
            return _owned_engine_element(self.parent(), value)
        if value_parent in SageRings():
            return _owned_engine_element(value_parent, value)
        return value

    def __pow__(self, exponent, modulus=None):
        if modulus is not None:
            modulus = self._operator_operand(modulus)
            if modulus is NotImplemented:
                return NotImplemented
            value = pow(self._backend(), exponent, modulus._backend())
        else:
            try:
                exponent = exponent.__index__()
            except AttributeError:
                return NotImplemented
            value = self._backend() ** exponent
        value_parent = element_parent(value)
        if value_parent is self.parent()._engine:
            return _owned_engine_element(self.parent(), value)
        if value_parent in SageRings():
            return _owned_engine_element(value_parent, value)
        return value

    def __rtruediv__(self, other):
        numerator = self._operator_operand(other)
        if numerator is NotImplemented:
            return NotImplemented
        return numerator.__truediv__(self)

    def __floordiv__(self, other):
        other = self.parent()(other)
        return _owned_engine_element(self.parent(), self._backend() // other._backend())

    def quo_rem(self, other):
        other = self.parent()(other)
        quotient, remainder = self._backend().quo_rem(other._backend())
        ring = self.parent()
        product = owned_sets.Sets().product((ring, ring))
        return product((
            _owned_engine_element(ring, quotient),
            _owned_engine_element(ring, remainder),
        ))

    def divides(self, other):
        other = self.parent()(other)
        return bool(self._backend().divides(other._backend()))

    def gcd(self, other):
        other = self.parent()(other)
        return _owned_engine_element(self.parent(), self._backend().gcd(other._backend()))

    def xgcd(self, other):
        r"""Return ``(g,s,t)`` with ``g = s*self + t*other`` in this ring."""
        other = self.parent()(other)
        gcd, left, right = self._backend().xgcd(other._backend())
        ring = self.parent()
        product = owned_sets.Sets().product((ring, ring, ring))
        return product((
            _owned_engine_element(ring, gcd),
            _owned_engine_element(ring, left),
            _owned_engine_element(ring, right),
        ))

    def lcm(self, other):
        other = self.parent()(other)
        return _owned_engine_element(self.parent(), self._backend().lcm(other._backend()))

    def valuation(self, prime):
        prime = self.parent()(prime)
        integers = _owned_integers()
        return _owned_engine_element(integers, SageZZ(self._backend().valuation(prime._backend())))

    def prime_divisors(self):
        r"""Return the distinct prime divisors as an owned finite ordered set."""
        return owned_sets.finite_ordered_set(
            tuple(
                _owned_engine_element(self.parent(), prime)
                for prime in self._backend().prime_divisors()
            )
        )

    def is_prime(self):
        return bool(self._backend().is_prime())

    def divisors(self):
        r"""Return the positive divisors as an owned finite ordered set."""
        return owned_sets.finite_ordered_set(
            tuple(
                _owned_engine_element(self.parent(), divisor)
                for divisor in self._backend().divisors()
            )
        )

    def euler_phi(self):
        r"""Return Euler's totient as an owned nonnegative integer."""
        integers = _owned_integers()
        return _owned_engine_element(integers, SageZZ(_engine_euler_phi(self._backend())))

    def number_of_divisors(self):
        r"""Return the number of positive divisors as an owned integer."""
        integers = _owned_integers()
        return _owned_engine_element(integers,
            SageZZ(_engine_number_of_divisors(self._backend()))
        )

    def factor(self):
        r"""Return the engine factorization crossed into owned factors and multiplicities."""
        factorization = self._backend().factor()
        return OwnedFactorization(
            self.parent(),
            factorization.unit(),
            tuple(factorization),
        )

    def is_irreducible(self):
        return bool(self._backend().is_irreducible())

    def roots(self, ring=None):
        r"""Return the finite family of roots indexed by the roots themselves."""
        if ring is None:
            backend_roots = tuple(self._backend().roots())
        else:
            ring = _owned_ring(ring)
            backend_roots = tuple(self._backend().roots(_engine_ring(ring)))
        if ring is None:
            owned_pairs = tuple(
                (
                    _cross_engine_ring_value(root),
                    _owned_engine_element(SageZZ, SageZZ(multiplicity)),
                )
                for root, multiplicity in backend_roots
            )
        else:
            owned_pairs = tuple(
                (
                    _owned_engine_element(ring, root),
                    _owned_engine_element(SageZZ, SageZZ(multiplicity)),
                )
                for root, multiplicity in backend_roots
            )
        indices = owned_sets.finite_ordered_set(tuple(root for root, _multiplicity in owned_pairs))
        multiplicities = dict(owned_pairs)
        return owned_sets.finite_indexed_family(
            indices,
            multiplicities.__getitem__,
            name=f"Roots of {self}",
        )

    def discriminant(self):
        return _cross_engine_ring_value(self._backend().discriminant())

    def resultant(self, other):
        other = self.parent()(other)
        return _cross_engine_ring_value(self._backend().resultant(other._backend()))

    def splitting_field(self):
        r"""Return the owned splitting field of this polynomial.

        Sage requires a presentation name even though the splitting field is
        the mathematical output.  Keep that choice private, then refine the
        crossed ring through the number-field owner so field operations such
        as ``degree`` remain available.
        """
        from sage_extensions.categories.rings.number_fields import (
            _own_number_field,
        )

        return _own_number_field(self._backend().splitting_field("a"))

    def factorial(self):
        return _owned_engine_element(self.parent(), self._backend().factorial())

    def binomial(self, m):
        r"""The binomial coefficient of this element over the natural number ``m``."""
        return _owned_engine_element(self.parent(), self._backend().binomial(int(m)))

    def _squareness_decision(self):
        r"""Supply the retained exact ring-element square procedure to Magmas."""
        decision = self._backend().is_square()
        if decision is True or decision is False or isinstance(decision, Predicate):
            return decision
        return AtomicProposition("is_square", self)

    def sqrt(self):
        return _cross_engine_ring_value(self._backend().sqrt())

    def numerator(self):
        value = self._backend().numerator()
        parent = value.parent()
        return _owned_engine_element(parent, value)

    def denominator(self):
        value = self._backend().denominator()
        parent = value.parent()
        return _owned_engine_element(parent, value)

    def additive_order(self):
        value = self._backend().additive_order()
        return _owned_engine_element(SageZZ, SageZZ(value))

    def multiplicative_order(self):
        value = self._backend().multiplicative_order()
        return _owned_engine_element(SageZZ, SageZZ(value))

    def degree(self):
        value = self._backend().degree()
        return _owned_engine_element(SageZZ, SageZZ(value))

    def trace(self):
        return _cross_engine_ring_value(self._backend().trace())

    def norm(self):
        return _cross_engine_ring_value(self._backend().norm())

    def minpoly(self):
        polynomial = self._backend().minpoly()
        return _owned_engine_element(polynomial.parent(), polynomial)


class _PredicateSubringElement(_OwnedRingElement):
    r"""The shared native scalar realization with this subring as its parent.

    Computation may use the larger ring, but results re-enter the predicate
    subring. A unit of the larger ring is a unit here exactly when its inverse
    lies here; field arithmetic must not classify every nonzero subring
    element as a unit.
    """

    def _repr_(self):
        return repr(self.parent().inclusion()(self))

    def _latex_(self):

        return latex(self.parent().inclusion()(self))

    def __call__(self, *arguments, **options):
        r"""Apply this element when its ambient ring element is itself callable.

        A predicate subring changes the parent that records membership; it does
        not erase operations intrinsic to the selected ambient element. This is
        needed, for example, for central elements of an endomorphism ring, whose
        ambient elements are morphisms and therefore evaluate on module
        elements. Non-callable ambient elements retain ordinary Python's
        TypeError behavior.
        """
        ambient = self.parent().inclusion()(self)
        if not callable(ambient):
            raise TypeError(f"{ambient!r} is not callable")
        return ambient(*arguments, **options)

    def is_zero(self):
        return self == self.parent().zero()

    def is_one(self):
        return self == self.parent().one()

    def _unit_decision(self):
        if (self == self.parent().one()) is True or (self == -self.parent().one()) is True:
            return True
        value = self.parent().inclusion()(self)
        decision = value.is_unit()
        if decision is False:
            return False
        if decision is not True:
            return AtomicProposition("is_unit", self)
        return value.inverse_of_unit() in self.parent()


class _OwnedIntegerElement(_OwnedRingElement):
    r"""An integer engine value implementing Python's exact index protocol.

    ``__index__`` is not a truncating conversion from an arbitrary ring.
    The private ring engine selects this element realization only for ZZ;
    sets and other consumers then use the native protocol without importing
    the ring constructor or inspecting its engine.
    """

    def __index__(self) -> int:
        return int(self)

    def _integer_(self, integer_ring):
        r"""This integer in ``integer_ring``, by Sage's ``Integer(x)`` conversion protocol.

        ``sage/rings/integer.pyx:Integer.__init__`` reads ``x._integer_`` and
        does not consult ``__index__``.
        """
        return integer_ring(self._backend())


class _OwnedRingParent(Parent):
    r"""An owned ring parent with one private computational realization.

    The parent and its elements belong to the preamble universe.  ``engine``
    is implementation state only; raw backend elements enter through
    ``_from_engine_element`` and leave through ``_engine_element``.
    """

    _native_module_basis = None


    @lazy_attribute
    def Element(self):
        r"""The engine-specific element realization consumed by Sage Parent.

        ``sage/structure/parent.pyx:Parent.element_class`` reads ``self.Element``
        and combines it with the category's element methods.  This native
        representation boundary supplies exact indexing only for integers;
        it does not change the mathematical category of either ring.
        """
        match self._engine:
            case _ if self._engine is SageZZ:
                return _OwnedIntegerElement
            case _:
                return _OwnedRingElement

    def __init__(
        self, engine: Ring, *, base=None, category=None, constructing_category=None,
        named_placement=None, named_cardinality=None, order_basis=None,
        _defer_construction_facets=False,
    ) -> None:
        r"""Construct over the scalar ring the level above declares.

        ``base`` is that ring.  A level sitting over a ring states its own base
        when it constructs through the level below -- the algebra level does --
        and carrying it to the host here is what makes the module level's
        ``base_ring()`` an answer of the construction rather than state a leaf
        restates.

        A ring the preamble adopts has no level above it to declare one, so it
        declares its own: the ring the engine presents it over, and itself when
        the engine presents it over nothing smaller, since a ring is free of
        rank one over its own scalars.  That is the same question the placement
        asks in order to read this ring as an algebra, and asking it here is
        what lets the module level's construction step -- registering the
        scalar action -- run on this route with nothing left to guess.
        """
        SageObject.__init__(self)
        canonical_native = base is None and category is None
        # The constructing category is defining construction data (OWN-15):
        # a level above names the category it builds in. Raw engine rings do
        # not receive a generic OwnedRings placement; _owned_engine_ring must
        # route them through a constructor that supplies this datum.
        self._constructing_category = (
            OwnedRings() if constructing_category is None else constructing_category
        )
        self._engine = engine
        # A named construction that presents a known set states its size,
        # as it states its placement: ``RR`` and ``CC`` have the cardinality
        # of the continuum, whatever precision the engine computes at.
        self._named_cardinality = named_cardinality
        self._preamble_ring_display = None
        self._preamble_ring_display_kind = None
        self._local_ring_construction = None
        integer_bootstrap = canonical_native and engine is SageZZ
        # ``OwnedOrders`` is declared using ``Algebras(ZZ)``.  The canonical
        # integer object therefore has to be the parameter of that category
        # while its own initial placement is being assembled.  Seed only this
        # initial-object identity before category construction; every other
        # native ring keeps the ordinary post-Parent interning below.
        if integer_bootstrap:
            _owned_engine_ring.set_cache(self, engine)
            _owned_integers.set_cache(self)
        try:
            if base is None:
                if isinstance(engine, SageNumberFieldOrder) and self is not _owned_integers():
                    # An order is a ZZ-algebra even though Sage's order engine
                    # is implemented over its fraction field. Its native
                    # integral basis and module resolution are over ZZ; using
                    # engine.base_ring() here gives the wrong Parent base and
                    # contradicts OrdersWithChosenIntegralBasis.base_ring().
                    base = _owned_integers()
                    category_base = base
                else:
                    scalars = _engine_scalar_ring(engine)
                    base = self if scalars is None else _own_ring(scalars)
                    category_base = None if scalars is None else base
            else:
                base = _own_ring(base)
                category_base = base
            # Number fields already have a defining-polynomial power basis
            # over their coefficient field. Install this constructor datum
            # before deriving ring placement: placement hooks can ask for the
            # module basis before Parent.__init__ ever runs. The basis
            # callbacks remain lazy until the parent is initialized.
            if (
                engine is not SageQQ
                and engine in SageNumberFields()
                and base is _own_ring(_engine_scalar_ring(engine))
                and self._native_module_basis is None
            ):
                from sage_extensions.categories.modules.native_modules import (
                    _power_module_basis,
                )

                degree = int(
                    engine.defining_polynomial().degree()
                    if engine.is_absolute()
                    else engine.relative_polynomial().degree()
                )
                self._native_module_basis = _power_module_basis(
                    base,
                    degree,
                    lambda exponent: _owned_engine_element(self, engine.gen() ** exponent),
                    lambda element: _engine_element(self, element).list(),
                )
            if isinstance(engine, SageNumberFieldOrder) and self is not _owned_integers():
                # The integral basis is constructor data, but registering a
                # selected resolution here is too early: Parent.__init__ has
                # not yet installed the category-owned resolution registry.
                # Retain the actual basis instead; the common native module
                # constructor registers its resolution after Parent setup and
                # before it exposes the module to construction hooks.
                if order_basis is None:
                    raise TypeError(
                        "an owned number-field order must be constructed with its selected integral basis"
                    )
                from sage_extensions.categories.modules.native_modules import (
                    _NativeModuleBasis,
                )

                integers = _owned_integers()
                labels = owned_sets.finite_ordered_set(range(int(engine.rank())))
                field_engine = engine.number_field()
                degree = int(field_engine.degree())
                # The order constructor owns the selected integral basis.
                # Generic ring construction must consume that retained datum,
                # not ask the backend parent to choose it again.
                basis_elements = tuple(order_basis)
                basis_matrix = _SageMatrix(
                    SageQQ,
                    tuple(
                        tuple(field_engine(element).list())
                        + (SageQQ.zero(),) * (degree - len(field_engine(element).list()))
                        for element in basis_elements
                    ),
                )
                inverse_basis_matrix = basis_matrix.inverse()

                def order_coordinates(element):
                    # Read coordinates in the number field's power basis,
                    # not through any order-specific element representation.
                    values = tuple(field_engine(_engine_element(self, element)).list())
                    assert len(values) <= degree, (
                        f"the coordinates of {element} exceed the degree {degree} of {engine.number_field()}"
                    )
                    values += (SageQQ.zero(),) * (degree - len(values))
                    coordinates = _SageMatrix(SageQQ, 1, degree, values) * inverse_basis_matrix
                    result = {}
                    ranking = labels.ranking_map()
                    for label in labels:
                        coefficient = coordinates[0, int(ranking(label))]
                        assert coefficient in SageZZ, (
                            f"the selected integral basis of {self} gave nonintegral coordinate "
                            f"{coefficient} for {element}"
                        )
                        if coefficient:
                            result[label] = _owned_engine_element(integers, SageZZ(coefficient))
                    return result

                self._native_module_basis = _NativeModuleBasis(
                    integers.free_module(labels),
                    lambda label: _owned_engine_element(
                        self, basis_elements[int(labels.ranking_map()(label))]
                    ),
                    order_coordinates,
                )
            from sage_extensions.owned_category import owned_category_join

            # A named construction (``ZZ``, ``QQ``, ...) states its placement;
            # it is not read off the engine (ARC-08).
            defer_ring_facets = _defer_construction_facets or isinstance(
                engine, SageNumberFieldOrder
            )
            placement = _owned_ring_category(
                engine,
                scalar_base=category_base,
                owned_ring=self,
                presented=(
                    None if named_placement is None
                    else owned_category_join((OwnedRings(), *named_placement()))
                ),
                defer_construction_facets=defer_ring_facets,
            )
            # Every ring's additive structure is part of its defining
            # operations. Include the abelian-group owner in the initial
            # category join, before Parent.__init__ runs construction hooks;
            # a post-construction refinement is too late for owners that
            # construct the regular module during those hooks.
            from sage_extensions.categories.group.magmas import AdditiveGroups

            placement = owned_category_join(
                (placement, AdditiveGroups().AdditiveCommutative())
            )
            if category is not None:
                from sage_extensions.owned_category import owned_category_join

                placement = owned_category_join((placement, category))
            Parent.__init__(self, base=base, category=placement)
            realize_owned_category(self)

            # The primitive owned ring now exists as a Parent.  Cache every
            # canonical native ring before its regular module/algebra datum is
            # constructed so those owners reuse this exact scalar object.
            if canonical_native and not integer_bootstrap:
                _owned_engine_ring.set_cache(self, engine)

            _install_engine_selected_ring_data(self, engine)

            if not self._defer_native_algebra_construction():
                from sage_extensions.categories.algebras.algebras import (
                    _algebra_from_native_ring,
                )

                _algebra_from_native_ring(
                    self,
                    lambda left, right: left * right,
                    self._from_engine_element(engine.one()),
                    self._native_scalar_action,
                    module_basis=self._native_module_basis,
                    scalar_ring=base,
                )
            if defer_ring_facets and not _defer_construction_facets:
                # Orders need the same two-phase construction as native
                # algebras: install the selected ZZ-module action before
                # exposing the full order/algebra/free-module facets whose
                # realization hooks query that action.
                placement = _owned_ring_category(
                    engine,
                    scalar_base=category_base,
                    owned_ring=self,
                    presented=(
                        None if named_placement is None
                        else owned_category_join((OwnedRings(), *named_placement()))
                    ),
                    defer_construction_facets=False,
                )
                placement = owned_category_join(
                    (placement, AdditiveGroups().AdditiveCommutative())
                )
                if category is not None:
                    placement = owned_category_join((placement, category))
                refine(self, placement)
        except BaseException:
            # A failed constructor cannot leave its incomplete owned ring in
            # the canonical cache. Remove only this exact object's entries.
            if canonical_native:
                key = _owned_engine_ring.get_key(engine)
                if _owned_engine_ring.cache.get(key) is self:
                    del _owned_engine_ring.cache[key]
                if engine is SageZZ:
                    key = _owned_integers.get_key()
                    if _owned_integers.cache.get(key) is self:
                        del _owned_integers.cache[key]
            raise

    def _defer_native_algebra_construction(self):
        r"""Whether a stronger algebra constructor must finish its own data first."""
        return False



    def _native_scalar_action(self, scalar, element):
        r"""The native coefficient embedding before its module action is constructed."""
        element = self(element)
        return element._lmul_(self.base_ring()(scalar))

    def _from_engine_element(self, value):
        if element_parent(value) is not self._engine:
            value = self._engine(value)
        return self.element_class(self, value)

    def _engine_element(self, value):
        value = self(value)
        return value._backend()

    def _selected_engine_ring(self):
        r"""Return this native ring's selected private Sage realization."""
        return self._engine

    def _selected_local_ring_construction(self):
        r"""Return this native ring's selected local quotient datum, if any."""
        return self._local_ring_construction

    def _cardinality_decision(self):
        r"""Return the cardinality the named construction states, if it states one."""
        match self._named_cardinality:
            case None:
                return super()._cardinality_decision()
            case size:
                return size()

    def __call__(self, value):
        r"""Construct an owned ring element without Sage coercion discovery."""
        return self._element_constructor_(value)

    def _element_constructor_(self, value):
        r"""Construct a ring element, including the image of a finite cardinal.

        EXAMPLES::

            sage: from dzack_research.preamble.all import ZZ, finite_ordered_set
            sage: ZZ(finite_ordered_set((4, 3)).cardinality()) == ZZ(2)
            True
        """
        from sage_extensions.categories.sets.cardinals import Cardinalities

        # A cardinal is an owned parent, not an element with a scalar parent.
        # Its finite value is the natural number mapped into this ring.
        match value:
            case Parent() if value in Cardinalities():
                if not value.is_finite():
                    raise TypeError(f"cannot convert infinite cardinal {value} into {self}")
                return self._from_engine_element(self._engine(value.finite_value()))
            case _:
                pass
        parent = element_parent(value)
        if parent is self:
            return value
        from sage_extensions.categories.modules.pure.modules import Modules

        if parent in Modules(self.base_ring()) and parent.unformed_module() is self:
            return parent._element_of_unformed_module(value)
        if parent is not None:
            if parent in OwnedRings():
                return self._from_engine_element(
                    self._engine(_rational_engine_value(self._engine, _engine_element(parent, value)))
                )
            from sage_extensions.categories.sets.set_categories import NN

            if parent is NN:
                return self._from_engine_element(self._engine(int(value)))
            if parent in SageRings() or parent is self._engine:
                raise TypeError(
                    f"cannot convert {value!r} into {self}: it is a raw Sage element of {parent}; construct it "
                    "from a ring of this session"
                )
        if isinstance(value, SageObject):
            raise TypeError(
                f"cannot convert {value!r} into {self}: it is a raw Sage object; construct it from an object "
                "of this session"
            )
        return self._from_engine_element(self._engine(value))

    def __contains__(self, value) -> bool:
        r"""Decide whether ``value`` represents an element of this ring.

        Sage distinguishes set membership from ``is_parent_of``: membership
        asks whether the value lies in the represented set, not whether this
        exact parent already owns its current representation.  Keep that
        distinction while making the admissible routes explicit.  Owned ring
        elements are lowered at the ring adapter and the selected Sage ring
        decides membership of the represented value; raw Sage elements remain
        outside the public owned universe.
        """
        source = element_parent(value)
        if source is self:
            return True
        # Sage's parent() of a value outside Sage (a Cartan type, a list) is
        # its Python class, which no category can be asked about.
        if not isinstance(source, Parent):
            return value in self._engine
        from sage_extensions.categories.modules.pure.modules import Modules

        if source in Modules(self.base_ring()) and source.unformed_module() is self:
            return True
        if source in OwnedRings():
            # An element on which the canonical map lands is in this ring.
            # Sage's FreeAlgebra answers `2 in F` False although F(2) is its
            # scalar two (TRAPS.md), so the coercion is asked first.
            represented = _engine_element(source, value)
            return self._engine.has_coerce_map_from(_engine_ring(source)) or represented in self._engine
        from sage_extensions.categories.sets.set_categories import NN

        if source is NN:
            return True
        if source in SageRings() or isinstance(value, SageObject):
            return False
        return value in self._engine

    def _coerce_map_from_(self, source):
        r"""Return the represented canonical scalar map into this ring.

        Between owned rings the engine decides whether its canonical ring map
        exists.  The other canonical source is the initial semiring NN: every
        unital ring receives its unique unital semiring morphism, represented
        by the semiring category itself rather than by a ring-specific
        exception.
        """
        match source:
            case _ if source in OwnedRings():
                return self._engine.has_coerce_map_from(_engine_ring(source))
            case _ if source is OwnedSemirings().initial_object():
                return OwnedSemirings().initial_morphism(self)
            case _:
                return None

    def zero(self):
        return self._from_engine_element(self._engine.zero())

    def one(self):
        return self._from_engine_element(self._engine.one())

    def multiplicative_generator(self):
        return self._from_engine_element(_engine_multiplicative_generator(self._engine))

    def an_element(self):
        return self._from_engine_element(self._engine.an_element())

    def _characteristic_decision(self):
        integers = _owned_integers()
        return _owned_engine_element(integers, SageZZ(self._engine.characteristic()))

    def is_exact(self):
        return self._engine.is_exact()

    def _field_decision(self):
        r"""The engine's field decision, an untrusted answer to the caller of ``is_field``."""
        decision = _engine_field_decision(self._engine)
        match decision:
            case None:
                return AtomicProposition("is_field", self)
            case _:
                return decision

    def _commutativity_decision(self):
        return self._engine.is_commutative()

    def _integral_domain_decision(self):
        return self._engine.is_integral_domain()

    def _finiteness_decision(self):
        decision = _engine_finiteness_decision(self._engine)
        return AtomicProposition("is_finite", self) if decision is None else decision

    def _preamble_is_number_field_order(self):
        r"""Whether the selected ring datum is ZZ or a number-field order."""
        return self._engine is SageZZ or isinstance(self._engine, SageNumberFieldOrder)

    def is_projective(self) -> bool:
        r"""Projectivity as a module over the base ring.

        A ring is free of rank one over itself, a number-field order is
        free of finite rank over the integers (its integral basis), and a
        ring constructed with a native module basis over its base ring (a
        free algebra on its words) is free on that basis.  This is asked
        while the regular module is admitted into its free placement, so it
        is read from the construction's basis rather than that placement.
        """
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )
        from sage_extensions.categories.modules.pure.modules import Modules

        if self.base_ring() is self or self._preamble_is_number_field_order():
            return True
        presentation = Modules.ParentMethods._native_module_presentation(self)
        basis = None if presentation is None else presentation.module_basis()
        if basis is not None and basis.source() in FramedFreeModules(self.base_ring()):
            return True
        raise AssertionError(
            f"cannot decide whether {self} is projective as a module over {self.base_ring()}"
        )

    def _preamble_is_number_field(self):
        return self._engine in SageNumberFields()

    def _preamble_has_chosen_primitive_element(self):
        return self._engine in SageNumberFields() and self._engine is not SageQQ

    def base_ring(self):
        r"""Return the scalar ring this ring's construction declared."""
        return self.base()

    def variable_names(self):
        return self._engine.variable_names()

    def _first_ngens(self, n):
        return tuple(self._from_engine_element(value) for value in self._engine.gens()[:n])

    def elements(self):
        r"""Return all elements when this ring is finite, as an owned ordered set."""
        if self not in owned_sets.FiniteSets():
            raise ValueError(
                f"elements() lists the elements of a finite ring, but {self} is not known to be finite"
            )
        return owned_sets.finite_ordered_set(
            tuple(self._from_engine_element(element) for element in self._engine.list())
        )

    def _repr_(self):
        display = self._preamble_ring_display
        if display is not None:
            return display
        if self._engine is SageZZ:
            return "Integer Ring"
        if self._engine is SageQQ:
            return "Rational Field"
        if isinstance(self._engine, (PolynomialRing_generic, MPolynomialRing_base)):
            variables = ", ".join(self.variable_names())
            return f"Polynomial ring {self.base_ring()}[{variables}]"
        if self._preamble_is_number_field():
            return (
                f"Number field over {self.base_ring()} with defining polynomial "
                f"{self.defining_polynomial()}"
            )
        if self._preamble_is_number_field_order():
            rank = self.module_rank()
            names = tuple(self.variable_names())
            generator_text = f" generated by {', '.join(names)}" if names else ""
            return f"Order of rank {rank} over Integer Ring{generator_text}"
        if self in owned_sets.FiniteSets():
            size = self.cardinality()
            kind = "Field" if self in OwnedRings().Division().Commutative() else "Ring"
            return f"Finite {kind.lower()} with {size} elements"
        base = self.base_ring()
        # A ring that is its own base names itself; its category's name contains it.
        return f"Ring over {base}" if base is not self else repr(self._engine)

    def _latex_(self):
        text = self._repr_().replace("_", r"\_")
        return rf"\text{{{text}}}"


_OwnedRingBootstrapParent.register(_OwnedRingParent)


def _product_ring_placements(factors) -> tuple[Category, ...]:
    r"""The placement of ``R_1 x ... x R_n`` read from the factors.

    The operations are coordinatewise, so the product is commutative when
    every factor is; its ideals are the products of ideals of the factors,
    so it is Noetherian, or Artinian, when every factor is; its underlying
    set is the product of finitely many sets, finite when every factor is.
    A product of fields is not a field or a domain.  (No named Mathlib
    instance for the finite-product chain conditions was found by the
    formalization-corpus search of 2026-10-14.)
    """
    placements = []
    for placement in (
        OwnedRings().Commutative(),
        OwnedRings().Noetherian(),
        OwnedRings().Artinian(),
        owned_sets.FiniteSets(),
    ):
        if all(factor in placement for factor in factors):
            placements.append(placement)
    return tuple(placements)


class _ProductRingParent(_OwnedRingParent):
    r"""``R_1 x ... x R_n`` over a finite enumerated index set, realized by Sage's Cartesian product.

    The index set and the factor at each index are this level's datum; the
    projections are the universal cone of :meth:`OwnedRings.product`.
    """

    def __init__(self, index_set, factors) -> None:
        self._product_index_set = index_set
        self._product_factors = factors
        engine = _engine_ring(factors[0]).cartesian_product(
            *(_engine_ring(factor) for factor in factors[1:])
        )
        super().__init__(engine, named_placement=lambda: _product_ring_placements(factors))

    def product_factor(self, label):
        r"""The factor ``R_i`` at the index ``i``."""
        return self._product_factors[int(self._product_index_set.ranking_map()(label))]


@cached_function
def _product_ring(index_set, factors):
    r"""The one product ring of these factors over this index set."""
    return _ProductRingParent(index_set, factors)


def _product_ring_of_family(family):
    r"""The product ring of a finite family; a one-factor family is its factor (``ARC-10``)."""
    index_set = family.index_set()
    factors = tuple(family.value(label) for label in index_set)
    assert factors, (
        "the empty product of rings is the zero ring, which is not represented here as a product"
    )
    if len(factors) == 1:
        return factors[0]
    return _product_ring(index_set, factors)


def _product_ring_projection(product, family, label):
    r"""The projection ``prod_j R_j -> R_i`` at the index ``i``."""
    factor = family.value(label)
    if product is factor:
        return OwnedRings().Mor(factor, factor).identity()
    position = int(family.index_set().ranking_map()(label))
    return OwnedRings().Mor(product, factor)(
        lambda element: _owned_engine_element(
            factor, _engine_element(product, element).cartesian_projection(position)
        )
    )


def _product_ring_element(product, family, components):
    r"""The element of the product ring with the stated component at each index."""
    labels = tuple(family.index_set())
    if len(labels) == 1:
        return product(components[labels[0]])
    engine = _engine_ring(product)
    return _owned_engine_element(
        product,
        engine(tuple(_engine_element(family.value(label), components[label]) for label in labels)),
    )




def _engine_scalar_ring(engine: Ring):
    r"""Return the owned ring over which ``engine`` presents this ring.

    The answer is ``None`` for a ring the engine presents over itself, which is
    every ring free of rank one over its own scalars -- ``ZZ``, ``QQ``, a
    finite field.  A number field over the rationals or a p-adic ring over the
    integers presents over a smaller ring, and that ring is the scalars its
    module structure is over.  The placement below and the construction that
    threads the scalars to the host both ask this one question.
    """
    base = engine.base_ring()
    if base is engine or base not in SageRings():
        return None
    return _own_ring(base)


def _is_integral_multivariate_ideal(engine_ideal) -> bool:
    r"""Whether ``engine_ideal`` lives in ``ZZ[x_1, ..., x_n]``, where Sage's own ``is_prime`` and ``is_maximal`` raise."""
    ring = engine_ideal.ring()
    return isinstance(ring, MPolynomialRing_base) and ring.base_ring() is SageZZ


def _integral_polynomial_ideal_is_prime(engine_ideal) -> bool:
    r"""Primality of ``I`` in ``ZZ[x_1, ..., x_n]``.

    ``OWN-06`` adapter.  Sage's ``is_prime`` raises over ``ZZ`` (TRAPS.md);
    Singular's ``minAssZ`` (``primdecint.lib``) gives the minimal primes of
    ``I``, and a proper ``I`` is prime exactly when it is its only minimal
    prime.
    """
    from sage.libs.singular.function import lib as singular_lib, singular_function

    ring = engine_ideal.ring()
    if engine_ideal.is_one():
        return False
    singular_lib("primdecint.lib")
    minimal_primes = singular_function("minAssZ")(engine_ideal)
    return len(minimal_primes) == 1 and ring.ideal(minimal_primes[0]) == engine_ideal


def _integral_polynomial_ideal_is_maximal(engine_ideal) -> bool:
    r"""Maximality of ``I`` in ``ZZ[x_1, ..., x_n]``.

    ``OWN-06`` adapter.  ``ZZ`` is a Jacobson ring, so a field that is a
    finitely generated ``ZZ``-algebra is finite: ``I`` is maximal exactly
    when ``I cap ZZ = (p)`` for a prime ``p`` and the image of ``I`` in
    ``F_p[x_1, ..., x_n]`` is maximal, which Zariski's lemma decides there
    (prime, with quotient of dimension zero).  ``I cap ZZ`` is read off the
    constants of a Groebner basis over ``ZZ``.
    """
    ring = engine_ideal.ring()
    constants = tuple(g for g in engine_ideal.groebner_basis() if g.degree() <= 0)
    match constants:
        case (constant,):
            characteristic = SageZZ(constant).abs()
        case _:
            return False
    if not characteristic.is_prime():
        return False
    reduction = engine_ideal.change_ring(ring.change_ring(SageGF(characteristic)))
    return bool(reduction.is_prime() and reduction.dimension() == 0)


def _engine_field_decision(engine):
    r"""Return the engine's exact field decision when represented, else ``None``.

    ``OWN-06`` adapter.  ``S/I`` is a field exactly when ``I`` is maximal.
    For a multivariate polynomial ring ``S`` over a field Sage's
    ``is_maximal`` raises (TRAPS.md), so Zariski's lemma decides it: ``I`` is
    maximal exactly when it is prime and ``S/I`` has Krull dimension zero.
    """
    match engine:
        case _ if engine in SageFields():
            return True
        case QuotientRing_generic() if isinstance(engine.cover_ring(), MPolynomialRing_base) and (
            engine.cover_ring().base_ring() is SageAA
        ):
            # Singular has no algebraic-real coefficients and Sage has no
            # other primality route over AA (TRAPS.md): undecided.
            return None
        case QuotientRing_generic() if isinstance(engine.cover_ring(), MPolynomialRing_base) and bool(
            engine.cover_ring().base_ring().is_field()
        ):
            defining = engine.defining_ideal()
            return bool(defining.is_prime() and defining.dimension() == 0)
        case QuotientRing_generic() if _is_integral_multivariate_ideal(engine.defining_ideal()):
            return _integral_polynomial_ideal_is_maximal(engine.defining_ideal())
        case QuotientRing_generic() if isinstance(engine.cover_ring(), MPolynomialRing_base) and isinstance(
            engine.cover_ring().base_ring(), IntegerModRing_generic
        ):
            # (Z/n)[x]/I = Z[x]/(n, I), so the integral test decides it.
            cover = engine.cover_ring()
            modulus = SageZZ(cover.base_ring().characteristic())
            integral = cover.change_ring(SageZZ)
            lifted = integral.ideal(
                (integral(modulus), *(integral(generator.change_ring(SageZZ)) for generator in engine.defining_ideal().gens()))
            )
            return _integral_polynomial_ideal_is_maximal(lifted)
        case _:
            try:
                return engine.is_field()
            except NotImplementedError:
                # Sage's generic integral domains raise, rather than answer,
                # when they cannot decide field-ness (e.g. lazy power series
                # rings). Undecided is None, never an implicit False.
                return None


def _engine_finiteness_decision(engine):
    r"""Return whether the engine's ring is a finite set.

    ``OWN-06`` adapter.  Sage's ``QuotientRing_generic`` has no
    ``is_finite`` (TRAPS.md).  For ``A = k[x_1, ..., x_n]/I`` over a field
    ``k``: the unit ideal gives the zero ring, a finite set.  Otherwise
    ``k -> A`` is injective, and ``A`` is finite exactly when ``k`` is
    finite and ``dim_k A`` is finite, that is when ``A`` has Krull
    dimension zero (Atiyah--Macdonald, Ch. 8 and Cor. 5.24 (Zariski)).
    """
    match engine:
        case QuotientRing_generic() if engine.defining_ideal().is_one():
            # R/R has one element for every coefficient ring, including
            # infinite and non-Noetherian rings.  Do not ask the generic
            # quotient engine for an is_finite method it does not supply.
            return True
        case QuotientRing_generic() if engine.cover_ring().is_finite():
            # The quotient map is surjective, so a quotient of a finite
            # ring is finite regardless of its ideal presentation.
            return True
        case QuotientRing_generic() if isinstance(engine.cover_ring(), MPolynomialRing_base) and bool(
            engine.cover_ring().base_ring().is_field()
        ):
            dimension = engine.defining_ideal().dimension()
            return bool(dimension == -1 or (engine.cover_ring().base_ring().is_finite() and dimension == 0))
        case QuotientRing_generic():
            # No generic quotient-ring finiteness decision is supplied by
            # Sage.  The remaining presentations need their own exact
            # construction argument; absence of one is not infinitude.
            return None
        case _:
            return engine.is_finite()


def _size_of_finitely_supported_families(coefficients, indeterminates) -> Category:
    r"""The size of a ring of finitely supported coefficient families on monomials or words.

    ``R[x_1, ..., x_n]``, ``R<x_1, ..., x_n>`` and ``R[x_1^{\pm 1}, ..., x_n^{\pm 1}]``
    have as elements the finitely supported maps from the set of monomials or
    words in ``n`` indeterminates to ``R``.  For ``n = 0`` that set is one
    point and the ring is ``R``.  For ``n >= 1`` it is countably infinite, so
    over a nonzero finite or countable ``R`` the ring is countably infinite,
    and over an uncountable ``R`` it is uncountable.  The size of ``R``, and
    that ``1 != 0`` in ``R``, are read from its placement.
    """
    match coefficients:
        case _ if indeterminates == 0:
            return _placed_size(coefficients)
        case _ if coefficients in owned_sets.UncountableSets():
            return owned_sets.UncountableSets()
        case _ if coefficients in owned_sets.CountablyInfiniteSets():
            return owned_sets.CountablyInfiniteSets()
        case _ if _placed_nonzero(coefficients) and coefficients in owned_sets.FiniteSets():
            return owned_sets.CountablyInfiniteSets()
        case _:
            return owned_sets.Sets()


def _placed_nonzero(ring) -> bool:
    r"""Whether the placement of ``ring`` states ``1 != 0``.

    A nontrivial ring states it: division rings, local rings and ``ZZ/nZZ``
    for ``n >= 2`` are placed there by their categories and constructor. An
    infinite ring has more than one element. The bare zero-product axiom
    alone does not exclude the zero ring ``ZZ/1ZZ``.
    """
    return (
        ring in OwnedRings().Nontrivial()
        or ring in owned_sets.CountablyInfiniteSets()
        or ring in owned_sets.UncountableSets()
    )


def _size_of_all_coefficient_families(coefficients) -> Category:
    r"""The size of ``R[[x_1, ..., x_n]]`` or ``R((x))``, read from the placement of ``R``.

    A power series is an arbitrary map from the countably infinite set of
    monomials to ``R``, so there are ``|R|^{aleph_0}`` of them: uncountably
    many for every ``R`` with ``1 != 0``.
    """
    match coefficients:
        case _ if _placed_nonzero(coefficients):
            return owned_sets.UncountableSets()
        case _:
            return owned_sets.Sets()


def _placed_size(ring) -> Category:
    r"""The size placement of the owned ring ``ring``: finite, countably infinite, uncountable, or unstated."""
    match ring:
        case _ if ring in owned_sets.FiniteSets():
            return owned_sets.FiniteSets()
        case _ if ring in owned_sets.CountablyInfiniteSets():
            return owned_sets.CountablyInfiniteSets()
        case _ if ring in owned_sets.UncountableSets():
            return owned_sets.UncountableSets()
        case _:
            return owned_sets.Sets()


def _inherited_ring_placements(coefficients, *, univariate_over_field_is_principal: bool) -> tuple[Category, ...]:
    r"""The placements an extension of ``R`` by indeterminates inherits from ``R``.

    For ``A`` one of ``R[x_1, ..., x_n]``, ``R[x^{\pm 1}]``, ``R[[x_1, ..., x_n]]``
    with finitely many indeterminates:

    - ``A`` is commutative when ``R`` is;
    - ``A`` has no zero divisors when ``R`` does (the leading or lowest-order
      term of a product is the product of those terms);
    - ``A`` is nontrivial when ``R`` is, since the constants embed;
    - ``A`` is Noetherian when ``R`` is (Hilbert's basis theorem, and its
      power series form; a localization of a Noetherian ring is Noetherian).

    When ``univariate_over_field_is_principal`` holds, a single indeterminate
    over a field also makes ``A`` a principal ideal domain: ``K[x]`` is
    Euclidean, ``K[x^{\pm 1}]`` is a localization of it, and ``K[[x]]`` is a
    discrete valuation ring.  ``R`` is read through its placement only.
    """
    placements = []
    if coefficients in OwnedIntegralDomains():
        # The polynomial, Laurent and formal-power-series extensions of a
        # domain are domains.  Preserve the conjunction as a construction
        # theorem, rather than assuming the category join reconstructs it
        # from separately inherited commutativity, nonzero-divisor and
        # nontriviality placements.
        placements.append(OwnedIntegralDomains())
    if coefficients in OwnedRings().Commutative():
        placements.append(OwnedRings().Commutative())
    if coefficients in OwnedRings().Commutative().NoZeroDivisors():
        placements.append(OwnedRings().Commutative().NoZeroDivisors())
    if coefficients in OwnedRings().Nontrivial():
        placements.append(OwnedRings().Nontrivial())
    if coefficients in OwnedRings().Noetherian():
        placements.append(OwnedRings().Noetherian())
    if univariate_over_field_is_principal and coefficients in OwnedRings().Division().Commutative():
        placements.append(OwnedPrincipalIdealDomains())
    return tuple(placements)


def _polynomial_ring_placements(coefficients, indeterminates: int) -> tuple[Category, ...]:
    r"""The placement of ``R[x_1, ..., x_n]``, read from the placement of ``R`` and ``n``.

    The theorems are those of :func:`_inherited_ring_placements`; the size is
    that of the finitely supported coefficient families on the monomials.
    ``R[]`` is ``R`` and is Artinian when ``R`` is.
    """
    artinian = (
        (OwnedRings().Artinian(),)
        if indeterminates == 0 and coefficients in OwnedRings().Artinian()
        else ()
    )
    return (
        *_inherited_ring_placements(
            coefficients, univariate_over_field_is_principal=indeterminates == 1,
        ),
        _size_of_finitely_supported_families(coefficients, indeterminates),
        *artinian,
    )


def _free_associative_algebra_placements(coefficients, indeterminates: int) -> tuple[Category, ...]:
    r"""The placement of ``R<x_1, ..., x_n>``, read from the placement of ``R`` and ``n``.

    For ``n <= 1`` it is ``R[x]`` (or ``R``).  For ``n >= 2`` the generators
    ``x, y`` have ``xy != yx`` and the two-sided ideals ``(x y^k x)`` do not
    stabilize; constants embed, and the greatest words in two nonzero finite
    supports have a unique greatest product, whose coefficient is the product
    of their coefficients.
    """
    if indeterminates <= 1:
        return _polynomial_ring_placements(coefficients, indeterminates)
    inherited = tuple(
        placement
        for placement in (OwnedRings().NoZeroDivisors(), OwnedRings().Nontrivial())
        if coefficients in placement
    )
    # For at least two generators this ring is noncommutative, so it is not
    # an integral domain in this project's commutative-ring terminology.
    # The unique-leading-word argument proves only the non-zero-divisor
    # property, which is already retained in ``inherited``.
    return (*inherited, _size_of_finitely_supported_families(coefficients, indeterminates))


def _field_placements() -> tuple[Category, ...]:
    r"""A field is a commutative division ring; its only ideals are 0 and
    itself, so it is a principal ideal domain and Noetherian."""
    return (
        OwnedRings().Division().Commutative(),
        OwnedIntegralDomains(),
        OwnedIntegralDomains().PrincipalIdeals(),
        OwnedRings().Noetherian(),
    )


def _integer_placements() -> tuple[Category, ...]:
    r"""The placement of the named construction ``ZZ``.

    ``ZZ`` has distinct 0 and 1; it is Euclidean, ordered, countable, and
    its own ring of integers with the integral basis (1), hence an order.
    """
    from sage_extensions.categories.rings.number_fields import (
        OrdersWithChosenIntegralBasis,
    )

    return (
        OwnedIntegralDomains().PrincipalIdeals(), OwnedRings().Noetherian(),
        OwnedRings().Nontrivial(), OwnedOrderedRings(),
        owned_sets.CountablyInfiniteSets(), OrdersWithChosenIntegralBasis(),
        OwnedOrders(),
    )


def _rational_placements() -> tuple[Category, ...]:
    r"""The placement of the named construction ``QQ = Frac(ZZ)``: the prime
    field of characteristic 0, ordered, and the number field of degree 1."""
    from sage_extensions.categories.rings.number_fields import OwnedNumberFields

    return (
        *_field_placements(), PrimeFields(), OwnedOrderedRings(), OwnedNumberFields(),
        owned_sets.CountablyInfiniteSets(),
    )


def _real_algebraic_placements() -> tuple[Category, ...]:
    r"""The placement of ``AA``: the real algebraic numbers form an ordered,
    countable field."""
    return (*_field_placements(), OwnedOrderedRings(), owned_sets.CountablyInfiniteSets())


def _algebraic_number_placements() -> tuple[Category, ...]:
    r"""The placement of ``QQbar``: a countable field."""
    return (*_field_placements(), owned_sets.CountablyInfiniteSets())


def _algebraic_closure_finite_field_placements() -> tuple[Category, ...]:
    r"""An algebraic closure of a finite field is a countable field."""
    return (*_field_placements(), owned_sets.CountablyInfiniteSets())


def _monomial_term_variables(ring, element):
    r"""The variables of ``element`` when it is one nonzero term ``c x^a`` of the polynomial ring ``ring``."""
    engine_element = _engine_element(ring, element)
    match engine_element.monomials():
        case [_]:
            return frozenset(str(variable) for variable in engine_element.variables())
        case _:
            return None


def _continuum():
    r"""The cardinality of ``RR`` and of ``CC``, ``2^aleph_0``."""
    from sage_extensions.categories.sets.cardinals import continuum

    return continuum


def _real_or_complex_field_placements() -> tuple[Category, ...]:
    r"""The placement of ``RDF``, ``CDF`` and ``CC``: they present ``RR`` or
    ``CC``, uncountable fields."""
    return (*_field_placements(), owned_sets.UncountableSets())


def _owned_ring_category(
    engine: Ring, *, scalar_base=None, owned_ring=None, presented: Category | None = None,
    defer_construction_facets=False,
) -> Category:
    r"""Return the owned ring category the construction of ``engine`` places it in.

    The ring placement is supplied by the selected constructor. To it this
    adds the algebra and module structure the constructor selects: the ring is an
    associative unital algebra over ``scalar_base`` (over itself when there is
    none), commutative exactly when its ring placement is, and the module
    framing the constructor fixes.

    ``scalar_base`` is the owned base already selected by the constructor.
    Re-reading an engine scalar parent here can create a second owned view of
    the same mathematical base and hence two distinct parameterized algebra
    categories.
    """
    from sage_extensions.owned_category import owned_category_join

    if defer_construction_facets:
        # An owner such as _OwnedAlgebraParent must install its selected
        # resolution and native module datum before any of the presented
        # ring/algebra/free-module categories run construction hooks. This
        # initial placement deliberately supplies only the already-defined
        # ring and additive-group structure; the owning constructor refines
        # to the full, construction-derived placement after setup completes.
        from sage_extensions.categories.group.magmas import AdditiveGroups

        return owned_category_join((OwnedRings(), AdditiveGroups().AdditiveCommutative()))
    if presented is None:
        raise TypeError(
            f"{engine} has no selected ring-construction placement; "
            "native engine classes do not determine owned category membership"
        )
    from sage_extensions.categories.group.magmas import AdditiveGroups

    # Owned category joins are not guaranteed to materialize inherited
    # category facets on a concrete parent.  Ring addition is nevertheless
    # an abelian group by construction, and native module formation consumes
    # that facet before it refines the ring to an algebra.
    extra = [AdditiveGroups().AdditiveCommutative()]
    match owned_ring:
        case None:
            algebra_base = scalar_base
        case _:
            match scalar_base:
                case None:
                    algebra_base = owned_ring
                case _:
                    algebra_base = scalar_base
    match algebra_base:
        case None:
            pass
        case _:
            # The selected scalar object is part of the ring constructor.
            # Record its ordinary algebra/module structure in the initial
            # placement; the native algebra owner below supplies the
            # multiplication and unit data.
            from sage_extensions.categories.algebras.algebras import Algebras

            algebra = Algebras(algebra_base).Associative().Unital()
            match presented.is_subcategory(OwnedRings().Commutative()):
                case True:
                    extra.append(algebra.Commutative())
                case False:
                    extra.append(algebra)
    match (scalar_base is None, owned_ring is not None):
        case (True, True):
            # Every ring is the rank-one free module over itself.  Fix that
            # placement before Parent construction; the native module owner
            # fixes the selected unit framing before this constructor returns.
            from sage_extensions.categories.modules.pure.modules import (
                FinitelyGeneratedFreeModules,
            )

            extra.append(FinitelyGeneratedFreeModules(owned_ring))
        case _:
            pass
    match owned_ring:
        case _ if (
            not defer_construction_facets
            and owned_ring is not None
            and owned_ring._native_module_basis is not None
        ):
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                FramedFreeModules,
            )

            native_source = owned_ring._native_module_basis.source()
            # The retained frame is over its own coefficient ring, which
            # need not be the ring's algebra base. In particular an order
            # carries its integral basis over ZZ while its regular algebra
            # structure is over the order itself.
            native_free = FramedFreeModules(native_source.base_ring())
            if native_source.module_generating_set().cardinality().is_finite():
                native_free = native_free.FinitelyGenerated()
            extra.append(native_free)
        case _:
            pass
    return owned_category_join((presented, *extra))


def _install_engine_selected_ring_data(ring, engine) -> None:
    r"""Fix constructor data required by exact initial ring placement."""
    match ring:
        case _:
            pass


def _own_if_ring(result):
    return _own_ring(result) if result in SageRings() else result


@cached_function
def _owned_engine_ring(engine: Ring) -> Ring:
    r"""Raise a native engine through the owned constructor for its defining data.

    Polynomial and free associative engines present the free algebra on
    their native variables over their coefficient ring.  They therefore
    take the same monomial-module construction as the public free functor,
    rather than a bare native ring later labelled as a free algebra.
    """
    from sage.algebras.free_algebra import FreeAlgebra_generic
    from sage.rings.complex_double import CDF as SageCDF
    from sage.rings.qqbar import QQbar as SageQQbar
    from sage.rings.algebraic_closure_finite_field import (
        AlgebraicClosureFiniteField,
        AlgebraicClosureFiniteField_generic,
    )
    from sage.rings.abc import ComplexField as SageComplexFieldClass
    from sage.rings.abc import RealField as SageRealFieldClass
    from sage.rings.abc import pAdicField as SagePadicFieldClass
    from sage.rings.abc import pAdicRing as SagePadicRingClass
    from sage.rings.finite_rings.finite_field_base import FiniteField as SageFiniteFieldClass
    from sage.matrix.matrix_space import MatrixSpace as SageMatrixSpaceClass
    from sage.rings.fraction_field import FractionField_generic
    from sage.rings.laurent_series_ring import LaurentSeriesRing
    from sage.rings.lazy_series_ring import LazyLaurentSeriesRing, LazyPowerSeriesRing
    from sage.rings.polynomial.laurent_polynomial_ring_base import LaurentPolynomialRing_generic
    from sage.rings.power_series_ring import PowerSeriesRing_generic
    from sage.rings.real_double import RDF as SageRDF

    match engine:
        # An engine that is a named session ring is raised through that
        # ring's named construction, so every route meets one object.
        case _ if engine is SageZZ:
            return _owned_integers()
        case _ if engine is SageQQ:
            return _owned_rationals()
        case _ if engine is SageAA:
            return _owned_real_algebraic_numbers()
        case _ if engine is SageQQbar:
            return _owned_algebraic_numbers()
        case AlgebraicClosureFiniteField_generic():
            return _owned_algebraic_closure_finite_field(int(engine.characteristic()))
        case _ if engine is SageRDF:
            return _owned_real_double_field()
        case _ if engine is SageCDF:
            return _owned_complex_double_field()
        case SageRealFieldClass():
            return _owned_real_field(int(engine.precision()))
        case SageComplexFieldClass():
            return _owned_complex_field_of_precision(int(engine.precision()))
        case SagePadicFieldClass() if engine is _SageQp(engine.prime(), engine.precision_cap()):
            return _owned_padic_field(int(engine.prime()), int(engine.precision_cap()))
        case SagePadicFieldClass():
            # Q_p is constructed only by Qp(p, precision); no other p-adic
            # field engine has an owned construction to be raised through.
            assert False, (
                f"{engine} is a p-adic field with no owned construction: Q_p is constructed by "
                "Qp(p, precision), and a finite extension of Q_p is not yet constructed"
            )
        case SagePadicRingClass():
            from sage_extensions.categories.rings.commutative_algebra import Zp

            return Zp(int(engine.prime()), int(engine.precision_cap()))
        case SageFiniteFieldClass() if engine.degree() == 1:
            # A prime-field engine is ZZ/(p).
            return Zmod(int(engine.characteristic()))
        case SageFiniteFieldClass():
            # A finite-field engine is F_p[label]/(m) for its own modulus m,
            # never the field rebuilt with GF's default modulus: two
            # presentations of F_q are isomorphic only non-uniquely.
            return _finite_field_with_modulus(
                int(engine.characteristic()),
                engine.variable_name(),
                tuple(int(coefficient) for coefficient in engine.modulus().list()),
            )
        case SageMatrixSpaceClass():
            # M_n(R) is End_R(F_R([n])), the matrix ring R.matrix_space(n)
            # (ARC-09, ARC-10); a rectangular matrix space is no ring.
            assert engine.nrows() == engine.ncols(), (
                f"{engine} is not a ring: its matrices are not square"
            )
            return _own_ring(engine.base_ring()).matrix_space(int(engine.nrows()))
        case FractionField_generic():
            # A fraction-field engine is raised through Frac of the domain it
            # is the fraction field of.
            return _own_ring(engine.ring()).fraction_field()
        case IntegerModRing_generic():
            # After the finite fields: ``ZZ/nZZ`` met in an adapter is the quotient ``ZZ/(n)``.
            return Zmod(int(engine.order()))
        case SageNumberFieldOrder():
            # An order engine is raised through the order of its number field.
            from sage_extensions.categories.rings.number_fields import (
                _order_from_engine,
            )

            return _order_from_engine(engine)
        case _ if engine in SageNumberFields():
            # A number-field engine is raised through the number field of
            # its defining polynomial (relative: over its raised base).
            from sage_extensions.categories.rings.number_fields import (
                _number_field_from_engine,
            )

            return _number_field_from_engine(engine)
        case QuotientRing_generic():
            # A quotient engine is raised through R/I, retaining its owned
            # cover and the ideal's defining generators.  The generic engine
            # adoption fallback would instead select category placement from
            # the quotient's Sage parent class and lose the construction data.
            from sage_extensions.categories.rings.commutative_ideals import (
                _from_engine_ideal,
            )

            cover = _own_ring(engine.cover_ring())
            defining_ideal = _from_engine_ideal(cover, engine.defining_ideal())
            return cover.quotient_ring(defining_ideal)
        case LaurentPolynomialRing_generic():
            from sage_extensions.categories.algebras.free_algebras import (
                _laurent_polynomial_ring,
            )

            return _laurent_polynomial_ring(
                _own_ring(engine.base_ring()), tuple(engine.variable_names())
            )
        case PowerSeriesRing_generic() | LazyPowerSeriesRing():
            from sage_extensions.categories.rings.commutative_algebra import (
                FormalPowerSeriesRings,
            )

            return FormalPowerSeriesRings(_own_ring(engine.base_ring()))(
                tuple(engine.variable_names()), default_prec=engine.default_prec()
            )
        case LaurentSeriesRing() | LazyLaurentSeriesRing():
            # R((t)) is the localization of R[[t]] at the powers of t.
            # Rebuild the retained formal-series source first, then use its
            # localization constructor so the source and inverted parameter
            # remain explicit construction data rather than a Laurent engine
            # being adopted and classified by its Sage parent class.
            from sage_extensions.categories.rings.commutative_algebra import (
                FormalPowerSeriesRings,
            )

            coefficient_ring = _own_ring(engine.base_ring())
            variable_names = tuple(engine.variable_names())
            if len(variable_names) != 1:
                raise TypeError(
                    f"Laurent-series construction requires one formal variable, got {variable_names!r}"
                )
            precision = (
                int(engine.default_prec())
                if callable(getattr(engine, "default_prec", None))
                else int(engine.precision_cap())
            )
            power_series = FormalPowerSeriesRings(coefficient_ring)(
                variable_names, default_prec=precision
            )
            return power_series.localization(power_series.power_series_variable())
        case PolynomialRing_generic() | MPolynomialRing_base():
            # A polynomial engine met in an adapter is raised through the
            # one polynomial ring on its variables (OWN-02); its elements
            # convert by variable name into that ring's realization. Route
            # through the polynomial-ring owner rather than calling the
            # symmetric-algebra constructor with a raw tuple: fraction-field
            # adapters arrive here with the same variable names as an already
            # selected polynomial ring, and must reuse its literal framing.
            from sage_extensions.categories.algebras.free_algebras import (
                _polynomial_ring,
            )

            return _polynomial_ring(
                _own_ring(engine.base_ring()), tuple(engine.variable_names())
            )
        case FreeAlgebra_generic():
            from sage_extensions.categories.algebras.free_algebras import (
                _tensor_algebra_on,
            )

            return _tensor_algebra_on(
                _own_ring(engine.base_ring()), tuple(engine.variable_names())
            )
        case _:
            raise TypeError(
                f"cannot raise {engine} through an owned ring constructor: "
                "no constructor for this native ring family has been selected"
            )


def _own_ring(ring):
    r"""Private backend adapter: build the preamble ring represented by ``ring``.

    One engine has one owned view.  Number-field, order and ordinary algebra
    placement are fixed by that constructor before the parent is exposed;
    selected residue and integral-basis data are installed in the same
    construction.  Thus ``ZZ.base_ring() is ZZ`` and every morphism
    ``R[G] -> R`` finds one common base ring.
    """
    if ring in OwnedRings():
        return ring
    if ring not in SageRings():
        raise TypeError(f"{ring} is not a ring")
    if ring is SageZZ:
        return _owned_integers()
    return _owned_engine_ring(ring)


def _set_owned_ring_display(ring, display, *, kind=None):
    r"""Install presentation metadata at the owned ring boundary.

    Protected ring-storage contract under OWN-05. Ring and algebra
    constructors may select human-readable display metadata, but they do not
    write the ring parent's private storage directly. This owner dispatcher
    returns the same owned ring after installing only presentation metadata;
    it changes no mathematical category or realization.
    """
    owned = _own_ring(ring)
    owned._preamble_ring_display = str(display)
    if kind is not None:
        owned._preamble_ring_display_kind = str(kind)
    return owned


@cached_function
def _owned_integers() -> _OwnedRingParent:
    r"""The canonical owned integers, including their initial order placement."""
    return _OwnedRingParent(SageZZ, named_placement=_integer_placements)


# The named session rings.  Each is the one owned object of its name; a
# caller that needs it names it here instead of adopting the engine.


def _owned_rationals() -> Ring:
    r"""The canonical rational field ``QQ = (ZZ - {0})^{-1} ZZ``.

    There is one owned object for the rational field: the localization of the
    canonical integer ring at its nonzero multiplicative submonoid. Sage's
    fraction-field engine is selected privately by that localization
    construction; it is not separately adopted as a second owned ring.
    """
    rationals = _owned_integers().fraction_field_localization()
    _set_owned_ring_display(rationals, "Rational field QQ")
    return rationals


def _owned_real_algebraic_numbers() -> _OwnedRingParent:
    r"""The canonical owned real algebraic numbers ``AA``."""
    return _OwnedRingParent(SageAA, named_placement=_real_algebraic_placements)


@cached_function(key=lambda characteristic: int(characteristic))
def _owned_algebraic_closure_finite_field(characteristic: int) -> _OwnedRingParent:
    r"""The algebraic closure of a finite prime field, keyed by characteristic."""
    from sage.rings.algebraic_closure_finite_field import AlgebraicClosureFiniteField

    engine = AlgebraicClosureFiniteField(int(characteristic))
    return _OwnedRingParent(
        engine,
        named_placement=_algebraic_closure_finite_field_placements,
    )


def _owned_algebraic_numbers() -> _OwnedRingParent:
    r"""The canonical owned algebraic numbers ``QQbar``."""
    from sage.rings.qqbar import QQbar as SageQQbar

    return _OwnedRingParent(SageQQbar, named_placement=_algebraic_number_placements)


def _owned_real_double_field() -> _OwnedRingParent:
    r"""The canonical owned double-precision real field ``RDF``."""
    from sage.rings.real_double import RDF as SageRDF

    return _OwnedRingParent(
        SageRDF,
        named_placement=_real_or_complex_field_placements,
        named_cardinality=_continuum,
    )


def _owned_complex_double_field() -> _OwnedRingParent:
    r"""The canonical owned double-precision complex field ``CDF``."""
    from sage.rings.complex_double import CDF as SageCDF

    return _OwnedRingParent(
        SageCDF,
        named_placement=_real_or_complex_field_placements,
        named_cardinality=_continuum,
    )


def _owned_complex_field():
    r"""The canonical exact complex field ``CC``."""
    from sage_extensions.rings.complex import CC

    return CC


def _owned_ring(ring):
    r"""Return ``ring`` after asserting it already belongs to the preamble universe."""
    if ring not in OwnedRings():
        raise TypeError(f"expected a ring of this session, but {ring!r} is not one")
    return ring


def _engine_ring(ring):
    r"""Return the selected private computation parent behind an owned ring.

    This is the designated dispatcher for the protected ring-realization
    contract declared on :class:`OwnedRings.ParentMethods`.  It performs no
    representation probing: each construction owner states its realization.
    """
    owned = _own_ring(ring)
    engine = owned._selected_engine_ring()
    assert engine is not None, (
        f"cannot compute in {owned}: its construction supplies no selected computer-algebra model"
    )
    return engine


def _linear_algebra_ring(ring):
    r"""Choose exact scalar arithmetic for generic linear algebra.

    An exact field may select a symbolic computation ring whose parent
    also admits inexact elements. Sage reports SR.is_exact() as False.
    Generic elimination over the owned field itself instead uses its
    exact arithmetic and partial equality protocol. This choice applies
    to generic linear algebra, not to serialization for other engines.
    """
    engine = _engine_ring(ring)
    if (
        ring in OwnedFields()
        and ring.is_exact() is True
        and engine.is_exact() is False
    ):
        return ring
    return engine


def _linear_algebra_element(ring, element):
    r"""Supply a scalar in the selected generic linear-algebra parent.

    When generic arithmetic keeps the owned exact field, retain its
    element rather than serializing it into an inexact symbolic ring.
    Other selected computation parents keep their ordinary engine crossing.
    """
    if _linear_algebra_ring(ring) is ring:
        return ring(element)
    return _engine_element(ring, element)


def _engine_quotient_cover_ideal(ring, engine_ideal):
    r"""Lift an ideal of a selected quotient engine to its cover ring.

    If the computation parent of ``ring`` is ``S/J``, then an ideal generated
    by classes ``f_i`` is represented upstairs by ``J + (\tilde f_i)``.  This
    private crossing is the exact backend datum needed by Singular operations
    that work over ``S`` but not over Sage's generic quotient-ring parent.
    """
    engine = _engine_ring(ring)
    cover = engine.cover_ring()
    defining = engine.defining_ideal()
    lifted = tuple(engine(generator).lift() for generator in engine_ideal.gens())
    return cover.ideal(tuple(defining.gens()) + lifted)


def _rational_engine_value(engine, value):
    r"""Return ``value`` in a form that the engine ``ZZ`` or ``QQ`` converts exactly.

    The symbolic ring keeps distinct square roots apart, so it cannot read
    ``sqrt(6)*sqrt(3)*sqrt(2)`` as ``6`` and Sage's ``QQ`` rejects it.  ``AA``
    decides an algebraic value exactly, so a symbolic value bound for ``ZZ`` or
    ``QQ`` crosses through it; ``ZZ`` or ``QQ`` still rejects an irrational one.
    Every other value and target is returned unchanged.
    """
    from sage.rings.integer_ring import ZZ as SageIntegers
    from sage.rings.qqbar import AA
    from sage.rings.rational_field import QQ as SageRationals
    from sage.symbolic.expression import Expression

    if engine in (SageIntegers, SageRationals) and isinstance(value, Expression) and value in AA:
        return AA(value)
    return value


def _engine_element(ring, element):
    r"""Return the private computation-engine realization of ``element``.

    ``_engine_ring(R)`` identifies a currently selected CAS realization of the
    owned ring ``R``.  This companion crossing converts an element of the
    *owned* ring into that engine without asking the engine's coercion graph to
    know about the owned parent.  Quotients, localizations, completions, and
    future Julia/OSCAR-backed rings can therefore keep one public mathematical
    parent while changing computational realizations independently.
    """
    return _own_ring(ring)._engine_element(element)


def _owned_engine_element(ring, engine_element):
    r"""Raise one private computation result into the owned ring.

    Protected ring-realization contract (OWN-05--07).  Implementers are the
    ring parents' private ``_from_engine_element`` methods; callers are only
    computation adapters that have already selected this ring's realization
    and must immediately return to the owned mathematical parent.  Raw engine
    elements do not leave that adapter.  This is the raising companion to
    :func:`_engine_element`, so every ring realization has one lowering and
    one raising dispatcher.
    """
    return _own_ring(ring)._from_engine_element(engine_element)


def _engine_numeral(ring, value):
    r"""Cross an ingress numeral to the selected private Sage ring.

    Constructor arguments can arrive as Python numerals, owned ring elements,
    or raw Sage ring elements from backend code.  Public owned-ring coercion
    deliberately rejects the last case; this private constructor boundary is
    precisely where all three spellings are normalized before entering Sage.
    """

    owned = _own_ring(ring)
    engine = _engine_ring(owned)
    parent = element_parent(value)
    if parent in OwnedRings():
        value = _engine_element(parent, value)
    elif parent not in SageRings() and isinstance(value, SageObject):
        raise TypeError(
            f"cannot read {value!r} as an element of {ring}: its parent {parent!r} is not a ring"
        )
    return engine(value)


def _owning_constructor(constructor):
    @wraps(constructor)
    def construct(*args, **kwargs):
        result = constructor(*args, **kwargs)
        return _own_ring(result) if result in SageRings() else result

    return construct


def _constructor_over_ring(constructor):
    @wraps(constructor)
    def construct(base_ring, *args, **kwargs):
        result = constructor(_engine_ring(base_ring), *args, **kwargs)
        return _own_ring(result) if result in SageRings() else result

    return construct


def _lowered_integer_arguments(args):
    r"""The arguments of an engine ring constructor, with the session's integers lowered to Python ``int``.

    Sage's constructors neither contain nor convert the owned integers
    (TRAPS.md); every other argument, such as a generator name, passes as given.
    """
    integers = _owned_integers()
    return tuple(int(argument) if argument in integers else argument for argument in args)


def GF(order, name=None):
    r"""``F_q``, ``q = p^k``: the quotient ``F_p[label]/(m)`` by a monic irreducible ``m`` of degree ``k``.

    ``F_q`` is unique only up to a non-unique isomorphism, so its presentation
    is data.  ``GF(q, label)`` is the field ``F_p[label]/(m)`` with

    - ``label`` the name of the class of the variable, ``z<k>`` when none is
      given (Sage's default name);
    - ``m`` Sage's default modulus for a named ``GF(q, label)``:
      ``F_p[x].irreducible_element(k)``, the Conway polynomial ``C_{p,k}`` when
      Sage's database holds it, otherwise the minimal-weight irreducible
      polynomial for ``p = 2`` and PARI's Adleman--Lenstra polynomial for odd
      ``p`` (``sage/rings/polynomial/polynomial_ring.py``,
      ``PolynomialRing_dense_finite_field.irreducible_element``;
      ``finite_field_constructor.py``, ``create_key_and_extra_args``).  Sage's
      unnamed ``GF(q)`` uses a pseudo-Conway polynomial outside the database;
      that polynomial is not used here, so ``GF(q)`` is ``GF(q, "z<k>")``.

    It is that quotient, one object for ``(p, m, label)`` (``OWN-02``): the
    ideal ``(m)`` is constructed maximal (the caller's claim, ``OWN-22``) and
    the quotient is interned on ``F_p[label]`` and that ideal.  A finite field
    with another modulus is ``F_p[label].quotient_ring`` of that modulus.

    For a prime ``q = p`` the field is ``ZZ/(p)``, the one object ``Zmod(p)``
    also returns; ``F_p`` has no generator over its prime field, so ``name``
    is ignored there.
    """
    (order,) = _lowered_integer_arguments((order,))
    order = SageZZ(order)
    if order.is_prime():
        return Zmod(int(order))
    assert order.is_prime_power(), (
        f"there is no field with {order} elements: the order of a finite field is a prime power"
    )
    characteristic, degree = order.is_prime_power(get_data=True)
    label = f"z{degree}" if name is None else str(name)
    modulus = _SagePolynomialRing(_SageGF(int(characteristic)), "x").irreducible_element(int(degree))
    return _finite_field_with_modulus(
        int(characteristic), label, tuple(int(coefficient) for coefficient in modulus.list())
    )


def _finite_field_with_modulus(characteristic: int, label: str, coefficients: tuple[int, ...]):
    r"""``F_p[label]/(m)``, ``m`` the monic irreducible with these coefficients, lowest degree first.

    The construction of :func:`GF` and of a finite-field engine raised in an
    adapter (:func:`_owned_engine_ring`, by the engine's own modulus).  The
    ideal ``(m)`` is placed maximal by construction; the quotient selects
    Sage's finite field with modulus exactly ``m`` as its realization
    (``_quotient_ring``).
    """
    from sage_extensions.categories.rings.commutative_ideals import (
        CommutativeIdeals,
    )

    polynomials = Zmod(characteristic).polynomial_ring(label)
    modulus = _owned_engine_element(polynomials, _engine_ring(polynomials)(list(coefficients)))
    return polynomials.quotient_ring(CommutativeIdeals(polynomials).Maximal()(modulus))


def Zmod(modulus):
    r"""``ZZ/(n)``: the quotient of ``ZZ`` by the ideal ``(n)``, ``n`` the modulus.

    It is that quotient, one object (``OWN-02``), placed where the ideal's
    routing puts it: a field when ``n`` is prime.  ``ZZ/(0)`` is ``ZZ``.
    """
    (modulus,) = _lowered_integer_arguments((modulus,))
    integers = _owned_integers()
    if int(modulus) == 0:
        return integers
    return integers.quotient_ring(integers.ideal(integers(int(modulus))))


def Qp(prime, precision=20):
    r"""The ``p``-adic numbers ``Q_p`` represented to relative ``precision``.

    ``p`` is the defining datum; the precision is part of which represented
    field this is (``API-10``).  Equal data give the same field.
    """
    (prime, precision) = _lowered_integer_arguments((prime, precision))
    return _owned_padic_field(int(prime), int(precision))


def _padic_field_placements() -> tuple[Category, ...]:
    r"""``Q_p`` and its finite extensions are uncountable fields."""
    return (*_field_placements(), owned_sets.UncountableSets())


@cached_function
def _owned_padic_field(prime: int, precision: int) -> _OwnedRingParent:
    engine = _SageQp(prime, precision)
    # Z_p is in bijection with {0, ..., p-1}^NN by p-adic digits, and Q_p
    # is a countable union of translates of p^-k Z_p, so |Q_p| = 2^aleph_0.
    field = _OwnedRingParent(
        engine, named_placement=_padic_field_placements, named_cardinality=_continuum
    )
    _set_owned_ring_display(field, f"Q_{prime} with precision {precision}", kind="padic")
    return field


def RealField(precision=53):
    r"""The real numbers represented to ``precision`` bits (``API-10``)."""
    (precision,) = _lowered_integer_arguments((precision,))
    return _owned_real_field(int(precision))


@cached_function
def _owned_real_field(precision: int) -> _OwnedRingParent:
    field = _OwnedRingParent(
        _SageRealField(precision),
        named_placement=_real_or_complex_field_placements,
        named_cardinality=_continuum,
    )
    _set_owned_ring_display(field, f"Real field with {precision} bits precision", kind="real")
    return field


def ComplexField(precision=53):
    r"""The complex numbers represented to ``precision`` bits (``API-10``)."""
    (precision,) = _lowered_integer_arguments((precision,))
    return _owned_complex_field_of_precision(int(precision))


@cached_function
def _owned_complex_field_of_precision(precision: int) -> _OwnedRingParent:
    field = _OwnedRingParent(
        _SageComplexField(precision),
        named_placement=_real_or_complex_field_placements,
        named_cardinality=_continuum,
    )
    _set_owned_ring_display(
        field, f"Complex field with {precision} bits precision", kind="complex"
    )
    return field


Rings = OwnedRings
OrderedRings = OwnedOrderedRings
DivisionRings = OwnedDivisionRings
Fields = OwnedFields
IntegralDomains = OwnedIntegralDomains
PrincipalIdealDomains = OwnedPrincipalIdealDomains
NoetherianRings = OwnedNoetherianRings
ArtinianRings = OwnedArtinianRings
LocalRings = OwnedLocalRings
AdicallyCompleteRings = OwnedAdicallyCompleteRings
CompleteLocalRings = OwnedCompleteLocalRings
Orders = OwnedOrders


def binomial(x, m):
    r"""The binomial coefficient \(\binom{x}{m}\), for a natural number \(m\)."""
    return x.binomial(m)


def CommutativeRings():
    r"""The category of commutative unital rings.

    The session name for ``OwnedRings().Commutative()``: commutativity is an
    axiom on the operation, and this is the category it cuts out.
    """
    return OwnedRings().Commutative()


OwnedCommutativeRings = CommutativeRings


def _enumerated_ring_elements(ring):
    r"""Finite scalar enumeration at the native ring boundary, or ``None``.

    The finite-linearity callers use owned values.  Only this ring adapter
    accesses the computation ring's iterator and converts its outputs.
    """
    match ring:
        case _ if ring in owned_sets.FiniteSets():
            engine = _engine_ring(ring)
            return tuple(_owned_engine_element(ring, engine(value)) for value in engine)
        case _:
            return None
