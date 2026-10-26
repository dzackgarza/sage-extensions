"""Algebras graded by a monoid."""

from sage.categories.category_with_axiom import all_axioms
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    MultiplicativeAlgebraMorphism,
    _algebra_on_module,
    _assert_not_refuted,
    _associativity,
    _decide_on_module_generators,
    _two_sided_unit,
    _unit_from_multiplication,
)
from sage_extensions.categories.modules.graded_modules import (
    GradedModuleMorphismMethods,
    GradedModules,
    _concentrated_graded_module,
    _require_grading_monoid,
)
from sage_extensions.categories.modules.pure.modules import BilinearMap, Modules
from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    OwnedCategoryOverBaseRing,
    OwnedIntegralDomains,
    OwnedRings,
    _own_ring,
    _owned_integers,
)
from sage_extensions.lexicon.algebra import MonoidObject
from sage_extensions.logic import AtomicProposition
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

# Bourbaki, Algebra III §4.9: an alternating graded algebra is one satisfying
# the Koszul sign rule in which every odd-degree element squares to zero.
if "Alternating" not in all_axioms:
    all_axioms.add("Alternating")


def _graded_multiplication_from_components(module, component_product):
    r"""Classify the bilinear product specified on homogeneous summands.

    Protected graded-algebra constructor operation: callers supply maps
    M_s x M_t -> M_(st), bilinear over the fixed scalar ring.  The finite
    distributive extension is the unique product on the direct sum with those
    restrictions (Mathlib Algebra/DirectSum/Ring, mulHom_of_of).
    """
    tensor = Modules(module.base_ring()).tensor_product((module, module))

    def product(left, right):
        return sum((
            module.from_component(
                module.combine_degrees(s, t), component_product(s, x, t, y),
            )
            for s, x in module(left).homogeneous_components().items()
            for t, y in module(right).homogeneous_components().items()
        ), module.zero())

    return tensor.from_bilinear_map(module, product)


def _rank_one_unit_algebra(category):
    r"""``R e`` with ``e e = e``, concentrated in the identity degree of the grading of ``category``.

    Through the one construction: a rank-one module whose generator squares to
    itself is a commutative associative unital algebra with unit ``e``, and a
    module concentrated in the identity degree is graded by it, so the sign
    rule and the odd-square condition hold vacuously.  That is the placement
    ``category`` states.
    """
    ring = category.base_ring()
    module = _concentrated_graded_module(ring, category.grading_monoid())
    label = module.module_generating_set()[0]
    generator = module.module_generator(label)
    multiplication = BilinearMap(
        module,
        module,
        module,
        {(label, label): generator},
    )
    return _algebra_on_module(
        module,
        multiplication,
        placement=(category, Algebras(ring).Commutative()),
        unit=generator,
        law_decisions={
            "associativity": True,
            "unit": True,
            "commutativity": True,
            "grading": True,
        },
    )


def _truncated_polynomial_graded_algebra(ring, generator_degree, top_power):
    r"""``R[x]/(x^{m+1})`` with ``|x| = d``, graded by ``ZZ``.

    The graded module is free on ``x^0, ..., x^m``, each labelled by its
    degree ``k d``, and the product is ``x^j x^k = x^{j+k}``, zero when
    ``j + k > m``.  It is associative, with unit ``x^0``, and commutative,
    since it is a quotient of ``R[x]``.  It is supercommutative: for even
    ``d`` every degree is even, and for odd ``d`` the defining relation must
    kill ``x^2``, which the assertion requires.  ``H^*(CP^n; ZZ)`` is the case
    ``(d, m) = (2, n)`` and ``H^*(S^n; R)`` the case ``(n, 1)`` (Hatcher,
    *Algebraic Topology* [Hat02], Thm. 3.19 and Ex. 3.7).
    """
    from sage_extensions.categories.sets.finite_ordered_sets import (
        finite_ordered_set,
    )

    integers = _owned_integers()
    assert generator_degree % 2 == 0 or top_power <= 1, (
        f"R[x]/(x^{top_power + 1}) with x of odd degree {generator_degree} is not supercommutative: "
        "an odd element must square to zero"
    )
    degrees = finite_ordered_set(
        tuple(integers(generator_degree * power) for power in range(top_power + 1))
    )
    top_degree = generator_degree * top_power

    def degree_on_module_generator(module_generator):
        selected = module_generator.parent()
        return next(degree for degree in degrees if selected.module_generator(degree) == module_generator)

    construction_data = {"degree_on_module_generator": degree_on_module_generator}
    module = ring._fresh_free_module_on(
        degrees,
        _extra_categories=(GradedModules(ring, integers),),
        _extra_construction_data=construction_data,
    )

    def power_of_generator(degree):
        match degree <= top_degree:
            case True:
                return module.module_generator(degree)
            case False:
                return module.zero()

    product = BilinearMap(
        module,
        module,
        module,
        {(left, right): power_of_generator(left + right) for left in degrees for right in degrees},
    )
    return _algebra_on_module(
        module,
        product,
        placement=(
            GradedAlgebras(ring, integers).Supercommutative(),
            Algebras(ring).Commutative(),
        ),
        unit=module.module_generator(integers(0)),
        construction_data=construction_data,
        law_decisions={
            "associativity": True,
            "unit": True,
            "commutativity": True,
            "grading": True,
        },
    )


def _homogeneous_degree(element):
    r"""Return the degree owned by ``element.parent()``."""
    parent = element.parent()
    return parent.homogeneous_degree(element)


class GradedAlgebraMorphism:
    r"""An algebra morphism preserving the selected grading."""

    def __init__(
        self, parent, images, *, degree_preservation=None,
        degree_preservation_premises=None, **options,
    ) -> None:
        self._graded_algebra_degree_preservation_decision = degree_preservation
        self._graded_algebra_degree_preservation_source = (
            images if isinstance(images, GradedModuleMorphismMethods) else None
        )
        self._graded_algebra_degree_preservation_premises = (
            None if degree_preservation_premises is None
            else tuple(degree_preservation_premises)
        )
        super().__init__(parent, images, **options)

    def _degree_preservation_derivation(self):
        r"""Use a retained exact map or the actual laws of a construction.

        Only known input laws prove that a composite preserves degree. A
        failed or undecided sufficient premise does not decide the composite:
        inverse translations of a polynomial generator compose to identity.
        In that case the inherited graded-module diagnostic decides the
        resulting map's own equation, or retains that proposition.
        """
        supplied = self._graded_algebra_degree_preservation_decision
        if supplied is not None:
            return supplied
        premises = self._graded_algebra_degree_preservation_premises
        if premises is not None:
            if all(arrow.degree_preservation_decision() is True for arrow in premises):
                return True
            return None
        source = self._graded_algebra_degree_preservation_source
        if source is not None:
            return source.degree_preservation_decision()
        return None

    def __mul__(self, other):
        if not isinstance(other, GradedAlgebraMorphism):
            return super().__mul__(other)
        if other.codomain() is not self.domain():
            return NotImplemented
        source = other.domain()
        mor = GradedAlgebras(
            source.base_ring(),
            _require_grading_monoid(source.grading_monoid()),
        ).Mor(source, self.codomain())
        # Reading a graded arrow in a weaker Mor retains that same arrow.
        # The shared algebra composition instead applies its actual module
        # forgetful functor before composing, avoiding recursive dispatch.
        composite = MultiplicativeAlgebraMorphism.__mul__(self, other)
        if composite is NotImplemented:
            return NotImplemented
        return mor._from_degree_preserving_underlying_morphism(
            composite,
            degree_preservation_premises=(self, other),
        )


class GradedAlgebraMor(CategoricalMor):
    ElementMethods = GradedAlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        self._grading_monoid = mor_family.base_category().grading_monoid()
        if domain.base_ring() is not codomain.base_ring():
            raise ValueError(
                f"morphisms of graded algebras {domain} -> {codomain} need one base ring, but they are over "
                f"{domain.base_ring()} and {codomain.base_ring()}"
            )
        if _require_grading_monoid(domain.grading_monoid()) != self._grading_monoid:
            raise ValueError(
                f"{domain} is graded by {domain.grading_monoid()}, not by {self._grading_monoid}"
            )
        if _require_grading_monoid(codomain.grading_monoid()) != self._grading_monoid:
            raise ValueError(
                f"{codomain} is graded by {codomain.grading_monoid()}, not by {self._grading_monoid}"
            )
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def grading_monoid(self):
        return self._grading_monoid

    def _element_constructor_(self, images, *, check=False):
        r"""Construct the graded algebra map; ``check=True`` runs its validators (``OWN-22``)."""
        morphism = self.element_class(self, images)
        morphism.validate_linearity(check=check)
        morphism.validate_degree_preservation(check=check)
        return morphism

    def _from_degree_preserving_generator_map(self, images):
        r"""Construct a graded map whose generator construction preserves degree."""
        return self.element_class(self, images, degree_preservation=True)

    def _from_degree_preserving_underlying_morphism(
        self, morphism, *, degree_preservation_premises=(),
    ):
        r"""Lift a construction using its actual sufficient degree premises.

        The empty family is used for the identity, whose construction proves
        degree preservation. Composition retains its actual two input maps;
        arbitrary ingress uses the ordinary constructor and diagnostic.
        """
        return self.element_class(
            self, morphism,
            degree_preservation_premises=tuple(degree_preservation_premises),
        )

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        ordinary = Algebras(self.domain().base_ring()).Associative().Unital().Mor(
            self.domain(), self.codomain()
        )
        return self._from_degree_preserving_underlying_morphism(ordinary.identity())


class GradedAlgebraMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return GradedAlgebraMor


class GradedAlgebras(OwnedCategoryOverBaseRing):
    r"""Associative unital algebras graded by a monoid.

    Let \(M\) be a monoid. An \(M\)-graded \(R\)-algebra is an associative
    unital \(R\)-algebra \(A\) together with a direct-sum decomposition
    \(A = \bigoplus_{m \in M} A_m\) of the underlying module such that the
    product sends \(A_m \times A_{m'}\) into \(A_{mm'}\).

    The default monoid is \(\mathbb{Z}\) (additive), which is Sage's graded
    algebra axiom. The additive monoid \(\mathbb{N}\) is the nonnegative
    case. This is the nLab definition of a graded algebra; Stacks Project
    tag 00JL is the special case \(M = \mathbb{N}\).
    """

    def an_object(self):
        r"""A rank-one unital algebra concentrated in the identity degree."""
        return _rank_one_unit_algebra(self)

    @staticmethod
    def __classcall__(cls, base_ring, grading_monoid=None, parity=None):
        r"""``GradedAlgebras(R, M, parity)``: the grading datum is that of ``GradedModules``."""
        graded_modules = GradedModules(base_ring, grading_monoid, parity)
        return OwnedCategoryOverBaseRing.__classcall__(
            cls, graded_modules.base_ring(), graded_modules
        )

    def __init__(self, base_ring, graded_modules: Parent) -> None:
        self._graded_modules = graded_modules
        super().__init__(base_ring)

    def grading_monoid(self) -> MonoidObject:
        return self._graded_modules.grading_monoid()

    def parity_homomorphism(self):
        r"""Return the parity ``M -> ZZ/2`` stated with the grading."""
        return self._graded_modules.parity_homomorphism()

    def _repr_object_names(self) -> str:
        monoid = self.grading_monoid()
        names = "graded algebras" if monoid is _owned_integers() else f"algebras graded by {monoid}"
        return f"{names} over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self._graded_modules)

    def super_categories(self):
        r"""Retain both the algebra structure and the selected graded-module datum.

        EXAMPLES::

            sage: C = GradedAlgebras(ZZ)
            sage: C.super_categories()[0] is Algebras(ZZ).Associative().Unital()
            True
            sage: C.super_categories()[1] is C._graded_modules
            True
            sage: A = C.an_object()
            sage: A in C and A in C._graded_modules
            True
            sage: A in C.super_categories()[0]
            True
        """
        return [
            Algebras(self.base_ring()).Associative().Unital(),
            self._graded_modules,
        ]

    class SubcategoryMethods:
        def Supercommutative(self):
            r"""Return the refinement satisfying the Koszul sign rule."""
            return self._with_axiom("Supercommutative")

    class Supercommutative(CategoryWithAxiom):
        r"""Graded algebras with ``xy = (-1)^(eps(p) eps(q)) yx`` on homogeneous elements.

        ``eps`` is the parity stated with the grading, so a grading that
        recorded none has no supercommutative refinement.  Sage's
        ``Supercommutative`` axiom states the same rule for ``ZZ/2``-gradings.
        """

        def __init__(self, base_category) -> None:
            base_category.parity_homomorphism()
            super().__init__(base_category)

        def grading_monoid(self) -> MonoidObject:
            return self._base_category.grading_monoid()

        def parity_homomorphism(self):
            r"""Return the parity ``M -> ZZ/2`` the Koszul sign is read through."""
            return self._base_category.parity_homomorphism()

        def an_object(self):
            r"""The identity-degree rank-one algebra, where the sign rule is vacuous."""
            return _rank_one_unit_algebra(self)

        class SubcategoryMethods:
            def Alternating(self):
                r"""Return the refinement whose odd-degree elements square to zero."""
                return self._with_axiom("Alternating")

        class Alternating(CategoryWithAxiom):
            r"""Supercommutative graded algebras with ``x^2 = 0`` for ``eps(deg x) = 1``.

            Bourbaki, Algebra III §4.9, "alternating graded algebra"; Sage's
            ``commutative_dga`` calls the differential graded case strictly
            commutative.  The condition is independent of the sign rule over
            rings with 2-torsion.
            """

            def grading_monoid(self) -> MonoidObject:
                return self._base_category.grading_monoid()

            def parity_homomorphism(self):
                r"""Return the parity ``M -> ZZ/2`` odd degree is read through."""
                return self._base_category.parity_homomorphism()

            def an_object(self):
                r"""The identity-degree rank-one algebra, where odd-square conditions are vacuous."""
                return _rank_one_unit_algebra(self)

    class ParentMethods:
        def grading_compatibility_decision(self):
            r"""Return the retained decision that multiplication respects the selected grading, else the proposition."""
            return self._preamble_algebra_law_decisions.get(
                "grading", AtomicProposition("respects_grading", self.multiplication())
            )

        def restrict_scalars(self, ring_map):
            r"""Restrict scalars while retaining this algebra's grading."""
            from sage_extensions.categories.algebras.restricted_graded_algebras import (
                _restrict_graded_algebra_scalars,
            )

            return _restrict_graded_algebra_scalars(self, ring_map)

        def graded_derivations(self, target=None, shift=0):
            r"""Return degree-``shift`` graded derivations into ``target``."""
            from sage_extensions.categories.algebras.derivations import (
                _graded_derivations,
            )

            return _graded_derivations(self, target=target, shift=shift)

        def _Hom_(self, codomain, category=None):
            # ``A.Mor(B)`` is ``A.ambient_category().Mor(A, B)`` (``ARC-07``,
            # owner ruling 2026-10-14): for an algebra built by
            # ``GradedAlgebras(R, M, parity)`` that is the degree-preserving
            # algebra maps.  This hook only answers Sage's own ``Hom`` calls.
            return super()._Hom_(codomain, category=category)

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism in {self} needs two of its objects, but got {domain} and {codomain}"
            )
        if domain.base_ring() is not self.base_ring() or codomain.base_ring() is not self.base_ring():
            raise ValueError(
                f"morphisms in {self} need both algebras over {self.base_ring()}, but they are over "
                f"{domain.base_ring()} and {codomain.base_ring()}"
            )
        if _require_grading_monoid(domain.grading_monoid()) != self.grading_monoid():
            raise ValueError(
                f"{domain} is graded by {domain.grading_monoid()}, not by {self.grading_monoid()}"
            )
        if _require_grading_monoid(codomain.grading_monoid()) != self.grading_monoid():
            raise ValueError(
                f"{codomain} is graded by {codomain.grading_monoid()}, not by {self.grading_monoid()}"
            )
        return self.MorCategory().Of(domain, codomain)

    _MorCategory = GradedAlgebraMorCategoryConstruction

    def _call_(self, multiplication):
        r"""The graded algebra on the graded module ``M`` with multiplication ``m``.

        The unit is recovered from ``m``, and associativity and the unit
        equations are decided on module generators of ``M``.  That ``m``
        sends ``M_p (x) M_q`` into ``M_{pq}`` is the hypothesis this entry
        takes with ``m``: the module layer represents no homogeneous degree on
        which to decide it.
        """
        module = multiplication.codomain()
        assert module in GradedModules(self.base_ring(), self.grading_monoid()), (
            f"{module} is not a module graded by {self.grading_monoid()}"
        )
        unit = _unit_from_multiplication(multiplication)
        associativity = _decide_on_module_generators(
            module, _associativity(multiplication), 3,
            AtomicProposition("is_associative", multiplication),
        )
        unit_laws = _decide_on_module_generators(
            module, _two_sided_unit(multiplication, unit), 1,
            AtomicProposition("is_two_sided_unit", multiplication, unit),
        )
        _assert_not_refuted(associativity, "associativity", module)
        _assert_not_refuted(unit_laws, "the two unit equations", module)
        return _algebra_on_module(
            module,
            multiplication,
            placement=(self,),
            unit=unit,
            law_decisions={
                "associativity": associativity,
                "unit": unit_laws,
                "grading": AtomicProposition("respects_grading", multiplication),
            },
        )


class CommutativeGradedIntegralDomains(GradedAlgebras):
    r"""Commutative graded integral domains with homogeneous fraction charts."""

    def super_categories(self):
        return [GradedAlgebras(self.base_ring(), self.grading_monoid(), self.parity_homomorphism()), OwnedIntegralDomains()]

    def _call_(self, algebra):
        from sage_extensions.refine import refine
        if algebra not in GradedAlgebras(self.base_ring(), self.grading_monoid(), self.parity_homomorphism()) or algebra not in OwnedIntegralDomains():
            raise TypeError("degree-zero charts require a commutative graded integral domain")
        return refine(algebra, self)

    class ParentMethods:
        @cached_method
        def degree_zero_chart(self, localization):
            r"""Return ``(S_f)_0``, the degree-zero part of a graded localization.

            Localizing a graded ring at homogeneous elements grades the result
            by ``deg(a/s) = deg(a) - deg(s)``, now over the integers rather than
            the original monoid.  The degree-zero part is a subring, and for a
            single homogeneous ``f`` it is the affine coordinate ring of the
            standard open ``D_+(f)`` of ``Proj S``: the chart every projective
            construction is read in.

            A fraction is degree zero exactly when its numerator is homogeneous
            of the degree its denominator has, so the chart is cut out by that
            condition rather than by a chosen presentation in new variables.
            The degree of a fraction is well defined because ``a/s = b/t``
            forces ``at = bs``, hence equal degree differences, over an integral
            domain.
            """

            assert localization in LocalizationRings(), (
                f"a degree-zero chart is the degree-zero part of a localization, but {localization} is not one"
            )
            assert localization.localization_source() is self, (
                f"{localization} localizes a different ring than {self}"
            )
            assert self in OwnedIntegralDomains(), (
                f"the degree of a fraction over {self} is well defined once "
                "cancellation cannot change it, which an integral domain assures"
            )
            assert all(
                self(inverted).is_homogeneous() for inverted in localization.inverted_elements()
            ), (
                f"the degree-zero part of {localization} needs every inverted element homogeneous, but "
                f"{localization.inverted_elements()} are not all homogeneous"
            )

            def is_degree_zero(fraction) -> bool:
                numerator = self(fraction.numerator())
                if numerator == self.zero():
                    return True
                if not numerator.is_homogeneous():
                    return False
                denominator = self(fraction.denominator())
                return self.homogeneous_degree(numerator) == self.homogeneous_degree(denominator)

            return localization.predicate_subring(
                is_degree_zero,
                f"a/s is homogeneous of degree zero in {localization}",
                OwnedRings().Commutative(),
            )

        def degree_zero_chart_restriction(self, source_localization, target_localization):
            r"""Return the overlap map ``(S_f)_0 -> (S_fg)_0`` of two standard charts.

            The restriction ``S_f -> S_fg`` preserves the grading, so it carries
            degree-zero fractions to degree-zero fractions and cuts down to the
            charts.  These maps compose because the localization restrictions
            do, which is the compatibility ``Proj`` needs on overlaps.
            """

            restriction = source_localization.restriction_to(target_localization)
            source_chart = self.degree_zero_chart(source_localization)
            target_chart = self.degree_zero_chart(target_localization)
            return source_chart.Mor(target_chart)(
                lambda element: target_chart(restriction(source_localization(element))),
            )



__all__ = [
    "GradedAlgebraMorCategoryConstruction",
    "GradedAlgebraMor",
    "GradedAlgebraMorphism",
    "GradedAlgebras",
    "CommutativeGradedIntegralDomains",
]
