r"""Geometric cochain complexes and comparison-owned cohomology constructions."""

from math import prod

from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import parent as element_parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.group.cyclic_subgroups import (
    CyclicGroups,
)
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.modules.cochain_complexes import (
    CochainComplexes,
)
from sage_extensions.categories.modules.hodge_structures import (
    _split_mixed_hodge_structure,
)
from sage_extensions.categories.modules.pure.modules import BilinearMap
from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
    _engine_ring,
    _own_ring,
    _owned_complex_field,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.owned_category import _object_of


class ToricWeightCohomologyComplexes(OwnedCategoryOverBaseRing):
    r"""Shifted reduced simplicial complexes computing one toric sheaf-cohomology weight."""

    def an_object(self):
        r"""The zero-character weight complex of O(1) on the toric projective line."""
        from sage_extensions.categories.schemes.toric.toric_schemes import ToricSchemes

        scheme = ToricSchemes(self.base_ring()).an_object()
        return scheme.weight_cohomology_complex(
            scheme.hyperplane_divisor(),
            scheme.character_lattice().zero(),
        )

    @classmethod
    def _repr_object_names(cls):
        return "toric weight cohomology complexes"

    def super_categories(self):
        return [CochainComplexes(self.base_ring())]

    class ParentMethods:
        def __init__(self, cohomology_scheme, cohomology_divisor, cohomology_weight, **rest) -> None:
            self._cohomology_scheme = cohomology_scheme
            self._cohomology_divisor = cohomology_divisor
            self._cohomology_weight = cohomology_weight
            super().__init__(**rest)

        def cohomology_scheme(self):
            return self._cohomology_scheme

        def cohomology_divisor(self):
            return self._cohomology_divisor

        def cohomology_weight(self):
            return self._cohomology_weight

        def comparison_description(self):
            return "H^i(X,O_X(D))_m is identified with shifted reduced simplicial cohomology H~^(i-1)(V_{D,m})"


class ToricGeometricLineBundleCohomologySpaces(OwnedCategoryOverBaseRing):
    r"""Total toric line-bundle cohomology assembled from its live weight complexes."""

    def an_object(self):
        r"""The degree-zero cohomology of O(1) on the toric projective line."""
        from sage_extensions.categories.schemes.toric.toric_schemes import ToricSchemes

        scheme = ToricSchemes(self.base_ring()).an_object()
        return scheme.line_bundle_cohomology(scheme.hyperplane_divisor(), 0)

    @classmethod
    def _repr_object_names(cls):
        return "geometric toric line-bundle cohomology spaces"

    def super_categories(self):
        from sage_extensions.categories.divisors.cohomology import (
            LineBundleCohomologySpaces,
        )

        return [LineBundleCohomologySpaces(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            cohomology_weight_support,
            cohomology_weight_pieces,
            **rest,
        ) -> None:
            self._cohomology_weight_support = cohomology_weight_support
            self._cohomology_weight_pieces = cohomology_weight_pieces
            super().__init__(**rest)

        def cohomology_weight_support(self):
            return self._cohomology_weight_support

        def cohomology_weight_piece(self, weight):
            weight = self.cohomology_scheme().character_lattice()(weight)
            return self._cohomology_weight_pieces[weight]

        def cohomology_weight_inclusion(self, weight):
            weight = self.cohomology_scheme().character_lattice()(weight)
            assert weight in self.cohomology_weight_support(), (
                f"the weight-{weight} summand of the cohomology {self} is zero, so it has no inclusion"
            )
            return self.injection(weight)

        def cohomology_weight_projection(self, weight):
            weight = self.cohomology_scheme().character_lattice()(weight)
            assert weight in self.cohomology_weight_support(), (
                f"the weight-{weight} summand of the cohomology {self} is zero, so it has no projection"
            )
            return self.projection(weight)


class AffineGeometricCohomologyComplexes(OwnedCategoryOverBaseRing):
    r"""The affine-acyclic complex computing a represented quasi-coherent sheaf."""

    @classmethod
    def _repr_object_names(cls):
        return "affine geometric cohomology complexes"

    def super_categories(self):
        return [CochainComplexes(self.base_ring())]

    class ParentMethods:
        def __init__(self, geometric_sheaf, geometric_cover=None, **rest) -> None:
            self._geometric_sheaf = geometric_sheaf
            self._geometric_cover = geometric_cover
            super().__init__(**rest)

        def geometric_sheaf(self):
            return self._geometric_sheaf

        def geometric_scheme(self):
            return self.geometric_sheaf().scheme()

        def geometric_cover(self):
            r"""The distinguished unit cover the complex was stated on, or ``None`` for the one-chart cover."""
            return self._geometric_cover

        def acyclicity_reason(self):
            return "quasi-coherent sheaves on an affine scheme have no higher cohomology; this is the one-chart affine Cech resolution"

        def augmentation(self):
            r"""Return the identification of degree zero with global sections."""
            source = self.graded_piece(0)
            target = self.geometric_sheaf().global_sections()
            return source.module_category().Mor(source, target).identity()

        def derived_global_sections(self):
            r"""``RΓ(X, F)`` as ``Q`` of this complex, an object of ``DerivedCategory(R)``.

            An affine Čech complex of a quasi-coherent sheaf on an affine
            scheme is an acyclic resolution computing ``Γ(X, -)``, so its
            image under the localization ``Q : Ch(R) -> D(R)`` represents
            ``RΓ(X, F)``.
            """
            return CochainComplexes(self.base_ring()).localization_at_quasi_isomorphisms()(self)


def _affine_geometric_cohomology_complex(sheaf, cover=None):
    r"""Return the one-chart affine complex computing ``H^*(X,sheaf)``.

    The sheaf is a quasi-coherent sheaf ``M~`` on an affine scheme ``X``.  The
    cover consists of the single affine chart ``X`` itself, whose finite
    intersections are affine; quasi-coherent affine acyclicity therefore
    identifies the Cech complex with ``M`` in degree zero and zero elsewhere.
    """
    from sage_extensions.categories.schemes.ringed_spaces import (
        QuasiCoherentSheaves,
    )
    from sage_extensions.categories.schemes.schemes import Schemes

    scheme = sheaf.scheme()
    assert scheme in Schemes(scheme.scheme_base_ring()).Affine() and sheaf in QuasiCoherentSheaves(scheme), (
        f"the Cech complex of {sheaf} is computed here only for a quasi-coherent sheaf on an "
        f"affine scheme, but {scheme} is in {scheme.category()} and {sheaf} is in {sheaf.category()}"
    )
    match cover:
        case None:
            pass
        case _:
            assert cover.ambient_scheme() is scheme, (
                f"the cover {cover} is a cover of {cover.ambient_scheme()}, not of {scheme}"
            )
            one = scheme.coordinate_algebra().one()
            assert all(cover.defining_element(index) == one for index in cover.atlas()), (
                f"the Cech complex of {sheaf} is computed here only for covers of {scheme} by the "
                f"chart D(1) = {scheme}, but {cover} has a chart D(f) with f not equal to 1"
            )
    module = sheaf.global_sections()
    base = module.base_ring()
    zero = base._fresh_free_module_on(finite_ordered_set(()))
    return CochainComplexes(base)(
        {0: module, 1: zero},
        {0: module.module_category().Mor(module, zero).zero()},
        name=f"Affine Cech complex of {sheaf}",
        extra_categories=(AffineGeometricCohomologyComplexes(base),),
        extra_construction_data={"geometric_sheaf": sheaf, "geometric_cover": cover},
    )


@cached_function(key=lambda sheaf: id(sheaf))
def _projective_space_line_bundle_derived_global_sections(sheaf):
    r"""``RΓ(P^n_R, O(d))`` for the standard line bundle ``O(d)`` on ``P^n_R``, ``n >= 1``.

    Hartshorne, Theorem III.5.1, with \(S = R[x_0, \dots, x_n]\): the
    cohomology of \(\mathcal{O}(d)\) is \(H^0 = S_d\), the degree-\(d\)
    forms; \(H^n = (S_{-d-n-1})^\vee\), the dual module of the degree
    \(-d-n-1\) forms (the perfect pairing III.5.1(c)); and \(H^i = 0\) for
    \(0 < i < n\) and \(i > n\).  Both nonzero modules are free, so
    \(\operatorname{Ext}^{n+1}_R(H^n, H^0) = 0\) and the triangle
    \(H^0 \to R\Gamma \to H^n[-n] \to\) of the truncations splits:
    \(R\Gamma \cong H^0 \oplus H^n[-n]\), which is \(Q\) of the complex with
    those pieces and zero differentials.
    """
    from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

    space = sheaf.projective_space()
    base = space.scheme_base_ring()
    dimension = space.relative_dimension()
    degree = sheaf.degree()
    assert space in ProjectiveSpaces(base) and sheaf is space.O(degree), (
        f"RΓ is computed here for the standard line bundle O(d) on a projective space, but {sheaf} "
        f"is not O({degree}) on {space}"
    )
    assert dimension >= 1, (
        f"Hartshorne III.5.1 states the cohomology of O(d) on P^n for n >= 1, but {space} has dimension "
        f"{dimension}"
    )
    complex_ = CochainComplexes(base)(
        {
            0: sheaf.global_sections(),
            int(dimension): space.O(-degree - dimension - 1).global_sections().dual_module(),
        },
        {},
        name=f"Cohomology of {sheaf} in degrees 0 and {dimension} with zero differentials",
    )
    return CochainComplexes(base).localization_at_quasi_isomorphisms()(complex_)


@cached_function(key=lambda space: id(space))
def _projective_space_de_rham_hypercohomology(space):
    r"""``RΓ(P^n_R, Ω^•_{P^n_R/R})``, an object of ``DerivedCategory(R)``.

    Stacks Project, Tag 0FMJ (Lemma 50.11.4): for \(0 \le i \le n\),
    \(H^{2i}_{dR}(\mathbf{P}^n_R/R)\) is free of rank one with basis
    \(c_1^{dR}(\mathcal{O}(1))^i\), and every other de Rham cohomology module
    is zero.  The hypercohomology is bounded and every cohomology module is
    free, so each truncation triangle splits (\(\operatorname{Ext}^1_R\) out
    of a free module vanishes) and the object is \(Q\) of the complex with
    those modules in degrees \(0, 2, \dots, 2n\) and zero differentials.
    """
    base = space.scheme_base_ring()
    dimension = space.relative_dimension()
    complex_ = CochainComplexes(base)(
        {
            2 * power: base.free_module(finite_ordered_set((f"c_1(O(1))^{power}",)))
            for power in range(int(dimension) + 1)
        },
        {},
        name=f"de Rham cohomology of {space} with zero differentials",
    )
    return CochainComplexes(base).localization_at_quasi_isomorphisms()(complex_)


def _affine_geometric_scalar_cohomology_map(sheaf, degree, scalar, *, cover=None):
    r"""Return the cohomology map induced by scalar multiplication on ``sheaf``."""
    complex_ = _affine_geometric_cohomology_complex(sheaf, cover=cover)
    scalar = complex_.base_ring()(scalar)
    cochain_map = scalar * CochainComplexes(complex_.base_ring()).Mor(complex_, complex_).identity()
    return CochainComplexes(complex_.base_ring()).cohomology(int(degree))(cochain_map)


def _affine_cover_refinement_cochain_map(refinement, sheaf):
    r"""Return the cochain map ``C(U; F) -> C(V; F)`` induced by a unit-cover refinement ``V`` of ``U``.

    Both complexes are the contracted affine Čech complexes of ``F``, which
    are ``F(X)`` in degree zero, so the comparison is the identity there.
    Its cohomology image in degree ``d`` is
    ``CochainComplexes(R).cohomology(d)`` applied to this map.
    """
    assert refinement.ambient_scheme() is sheaf.scheme(), (
        f"the refinement {refinement} is a refinement of covers of {refinement.ambient_scheme()}, "
        f"not of {sheaf.scheme()}, the scheme of {sheaf}"
    )
    source = _affine_geometric_cohomology_complex(sheaf, cover=refinement.coarse_cover())
    target = _affine_geometric_cohomology_complex(sheaf, cover=refinement.fine_cover())
    source_degree_zero = source.graded_piece(0)
    degree_zero = source_degree_zero.module_category().Mor(source_degree_zero, target.graded_piece(0)).identity()
    return CochainComplexes(source.base_ring()).Mor(source, target)({0: degree_zero})


def _affine_cover_refinement_cohomology_map(refinement, sheaf, degree):
    r"""Return ``H^degree`` of the refinement cochain map, the comparison on sheaf cohomology."""
    cochain_map = _affine_cover_refinement_cochain_map(refinement, sheaf)
    return CochainComplexes(cochain_map.domain().base_ring()).cohomology(int(degree))(cochain_map)


def _toric_weight_cohomology_complex(scheme, divisor, weight):
    r"""Return the finite complex computing ``H^*(X,O_X(D))_weight``.

    Sage's toric-divisor engine selects the simplicial complex ``V_{D,m}`` of
    negative cones.  We retain only that finite combinatorial output and cross
    its augmented cochain incidence matrices into owned free modules.  The
    grading is shifted by one so degree ``i`` computes
    ``H~^(i-1)(V_{D,m})``, the toric line-bundle weight cohomology.
    """
    base = scheme.scheme_base_ring()
    divisor = scheme.weil_divisor_group()(divisor)
    assert scheme.is_cartier(divisor), (
        f"the weight-{weight} cohomology complex of O(D) on {scheme} needs D Cartier, but "
        f"D = {divisor} is not Cartier"
    )
    weight = scheme.character_lattice()(weight)
    pieces, differentials = scheme._weight_cohomology_presentation(divisor, weight)
    return CochainComplexes(base)(
        pieces,
        differentials,
        name="Toric weight cohomology complex",
        extra_categories=(ToricWeightCohomologyComplexes(base),),
        extra_construction_data={
            "cohomology_scheme": scheme,
            "cohomology_divisor": divisor,
            "cohomology_weight": weight,
        },
    )


def _toric_weight_cohomology(scheme, divisor, weight, degree):
    r"""Return the owned weight piece ``H^degree(X,O_X(D))_weight`` from its complex."""
    return scheme.weight_cohomology_complex(divisor, weight).cohomology(int(degree))


def _toric_weight_scalar_cochain_map(scheme, divisor, weight, scalar):
    r"""Return multiplication by ``scalar`` on the selected toric weight complex.

    This is the cochain map induced by the scalar endomorphism of the line
    bundle ``O_X(D)``.  It is represented on the actual complex computing the
    chosen character weight, so the induced cohomology map is obtained by the
    shared cohomology functor rather than by scalar multiplication on a
    separately recomputed vector space.
    """
    complex_ = scheme.weight_cohomology_complex(divisor, weight)
    scalar = complex_.base_ring()(scalar)
    return scalar * CochainComplexes(complex_.base_ring()).Mor(complex_, complex_).identity()


def _toric_weight_scalar_cohomology_map(scheme, divisor, weight, degree, scalar):
    r"""Return the map on one weight cohomology induced by scalar multiplication."""
    cochain_map = scheme.weight_scalar_cochain_map(divisor, weight, scalar)
    return CochainComplexes(scheme.scheme_base_ring()).cohomology(int(degree))(cochain_map)


def _toric_line_bundle_cohomology(scheme, divisor, degree):
    r"""Assemble ``H^degree(X,O_X(D))`` as the direct sum of its weight cohomologies."""
    from sage_extensions.categories.modules.pure.modules import Modules

    degree = int(degree)
    assert 0 <= degree <= int(scheme.dimension()), (
        f"the cohomology H^i(O(D)) of {scheme} is computed in degrees 0 through "
        f"{scheme.dimension()} (its dimension), but degree {degree} was requested"
    )
    assert scheme.fan().is_complete(), (
        f"the cohomology of O(D) on {scheme} is finite-dimensional, and computed here, only when "
        "the fan is complete, but the fan of this toric variety is not complete"
    )
    divisor = scheme.weil_divisor_group()(divisor)
    assert scheme.is_cartier(divisor), (
        f"the cohomology of O(D) on {scheme} is computed here only for Cartier D, but "
        f"D = {divisor} is not Cartier"
    )

    candidate_weights = tuple(
        scheme._line_bundle_cohomology_candidate_weights(divisor)
    )
    pieces = {
        weight: scheme.weight_cohomology(divisor, weight, degree)
        for weight in candidate_weights
    }
    pieces = {weight: piece for weight, piece in pieces.items() if int(piece.dimension()) != 0}
    weights = finite_ordered_set(tuple(pieces))
    base = scheme.scheme_base_ring()
    weight_pieces = finite_indexed_family(
        weights,
        lambda weight: pieces[weight],
        name="Nonzero toric cohomology weight pieces",
    )
    construction_data = {
        "cohomology_scheme": scheme,
        "cohomology_divisor": divisor,
        "cohomological_degree": degree,
        "cohomology_weight_support": weights,
        "cohomology_weight_pieces": weight_pieces,
    }
    if weights.cardinality() == 0:
        total = base._fresh_free_module_on(
            finite_ordered_set(()),
            _extra_categories=(ToricGeometricLineBundleCohomologySpaces(base),),
            _extra_construction_data=construction_data,
        )
    else:
        total = Modules(base).biproduct(
            weight_pieces,
            extra_categories=(ToricGeometricLineBundleCohomologySpaces(base),),
            extra_construction_data=construction_data,
        )
    return total


def _require_smooth_quartic_k3_complex_realization(scheme):
    r"""Require the represented smooth quartic K3 regime over ``QQ``."""
    from sage_extensions.categories.schemes.complete_intersections import (
        ProjectiveCompleteIntersections,
    )

    base = scheme.scheme_base_ring()
    assert _engine_ring(base) is SageQQ, (
        f"the integral cohomology of the quartic K3 surface {scheme} is computed only over QQ, "
        f"embedded in CC, but its base ring is {base}"
    )
    assert scheme in ProjectiveCompleteIntersections(base), (
        f"{scheme} must be a complete intersection in projective space to be a quartic K3 "
        f"surface, but it is in {scheme.category()}"
    )
    assert int(scheme.expected_dimension()) == 2 and tuple(scheme.defining_degrees()) == (4,), (
        f"{scheme} is not a quartic surface in P^3: it has dimension {scheme.expected_dimension()} "
        f"and equations of degrees {tuple(scheme.defining_degrees())}"
    )
    assert bool(scheme.is_smooth()), (
        f"the quartic surface {scheme} is singular, so it is not a K3 surface"
    )


class _QuarticK3IntegralTopology(SageObject):
    r"""Integral singular cohomology of a smooth quartic K3 with one marking.

    Under the selected complex realization, a smooth quartic surface is a K3
    surface.  Its middle integral cohomology with cup product is the even
    unimodular K3 lattice ``3U + 2E8(-1)``.  A *marking* is additional data;
    this object selects the catalogue marking in which the hyperplane class is
    ``e1 + 2 f1``, a primitive vector of square ``4``.  No toric Chow
    comparison is used.
    """

    def __init__(self, scheme) -> None:
        _require_smooth_quartic_k3_complex_realization(scheme)
        self._scheme = scheme

    def scheme(self):
        return self._scheme

    def realization_description(self):
        return "ordinary singular cohomology of the complex analytic quartic under the selected QQ-to-CC embedding"

    @cached_method
    def middle_cohomology_lattice(self):
        from sage_extensions.catalogue import NamedLattices

        return NamedLattices.LK3

    @cached_method
    def integral_cohomology(self, degree):
        degree = int(degree)
        assert degree >= 0, (
            f"singular cohomology of {self.scheme()} is defined in degrees >= 0, not in degree {degree}"
        )
        integers = _owned_integers()
        if degree == 2:
            return self.middle_cohomology_lattice()
        if degree in (0, 4):
            return integers._fresh_free_module_on(
                finite_ordered_set((f"H{degree}",)),
            )
        return integers._fresh_free_module_on(finite_ordered_set(()))

    @cached_method
    def cup_product(self, left_degree, right_degree):
        r"""Return the graded cup product in the selected K3 marking."""
        left_degree = int(left_degree)
        right_degree = int(right_degree)
        assert left_degree >= 0 and right_degree >= 0, (
            f"the cup product H^{left_degree} x H^{right_degree} of {self.scheme()} needs both "
            "degrees >= 0"
        )
        left = self.integral_cohomology(left_degree)
        right = self.integral_cohomology(right_degree)
        target = self.integral_cohomology(left_degree + right_degree)
        if left_degree == 0:
            return BilinearMap(
                left,
                right,
                target,
                lambda _unit_label, right_label: target.module_generator(right_label),
            )
        if right_degree == 0:
            return BilinearMap(
                left,
                right,
                target,
                lambda left_label, _unit_label: target.module_generator(left_label),
            )
        if left_degree == right_degree == 2:
            top_label = next(iter(target.module_generating_set()))
            middle = self.middle_cohomology_lattice()
            return BilinearMap(
                left,
                right,
                target,
                lambda left_label, right_label: target.scalar_multiple(
                    middle.b(
                        middle.module_generator(left_label),
                        middle.module_generator(right_label),
                    ),
                    target.module_generator(top_label),
                ),
            )
        return BilinearMap(
            left,
            right,
            target,
            lambda _left_label, _right_label: target.zero(),
        )

    @cached_method
    def cup_product_pairing(self):
        middle = self.middle_cohomology_lattice()
        values = _owned_integers().regular_module()
        return BilinearMap(
            middle,
            middle,
            values,
            lambda left, right: middle.b(
                middle.module_generator(left),
                middle.module_generator(right),
            ),
        )

    @cached_method
    def hyperplane_first_chern_class(self):
        middle = self.middle_cohomology_lattice()
        e1, f1 = tuple(middle.module_generators())[:2]
        hyperplane = e1 + 2 * f1
        assert middle.q(hyperplane) == _owned_integers()(4), (
            f"the hyperplane class {hyperplane} of the quartic {self.scheme()} must have square "
            f"H^2 = 4 in the K3 lattice, but it has square {middle.q(hyperplane)}"
        )
        assert hyperplane.is_primitive(), (
            f"the hyperplane class {hyperplane} of the quartic {self.scheme()} is not primitive "
            "in the K3 lattice"
        )
        return hyperplane

    @cached_method
    def hyperplane_c1_embedding(self):
        from sage_extensions.catalogue import NamedLattices

        source = NamedLattices.Z.twist(4)
        target = self.middle_cohomology_lattice()
        hyperplane = self.hyperplane_first_chern_class()
        return source.Emb(target)(lambda _label: hyperplane)

    def first_chern_class(self, line_bundle):
        r"""``c_1(O_X(d)) = d h`` for a restricted projective line bundle ``O_X(d)``.

        The represented line bundles on the quartic are the restrictions
        ``O_X(d)``; other classes of ``Pic(X)`` are not constructed.
        """
        assert line_bundle.scheme() is self.scheme(), (
            f"cannot take c_1 of {line_bundle} in the cohomology of {self.scheme()}: it is a "
            f"line bundle on {line_bundle.scheme()}"
        )
        return int(line_bundle.degree()) * self.hyperplane_first_chern_class()

    @cached_method
    def hodge_structure(self):
        r"""The Hodge structure on ``H^*(X(CC); ZZ)``, an object of ``MixedHodgeStructures(ZZ)``.

        See ``hodge_structure`` on smooth quartic K3 complete intersections.
        """
        return _quartic_k3_hodge_structure(self.scheme())

    def middle_cohomology_torsion_free_quotient(self):
        r"""K3 middle cohomology is already torsion-free."""
        return self.middle_cohomology_lattice()

    def _repr_(self) -> str:
        return f"Integral topology of {self.scheme()} ({self.realization_description()})"



def _quartic_k3_hodge_structure(scheme):
    r"""``H^*(X(CC); ZZ)`` of a smooth quartic K3 surface ``X``, split by degree.

    ``Gr^W_k = H^k``, of rank ``1, 0, 22, 0, 1``.  Adjunction gives
    ``K_X = O_X``, and ``X`` is proper and geometrically integral, so
    ``h^{2,0} = h^0(K_X) = h^0(O_X) = 1``; Hodge symmetry gives
    ``h^{0,2} = 1``, and ``h^{1,1} = b_2 - 2``.  Every weight is polarizable:
    ``H^2`` by the intersection form, ``H^0`` and ``H^4`` by ``ZZ(0)`` and
    ``ZZ(-2)``.
    """
    _require_smooth_quartic_k3_complex_realization(scheme)
    topology = scheme.integral_topology()
    ranks = tuple(int(topology.integral_cohomology(degree).module_rank()) for degree in range(5))
    weights = tuple(degree for degree in range(5) for _ in range(ranks[degree]))
    middle_rank = ranks[2]
    return _split_mixed_hodge_structure(
        _owned_integers(),
        weights,
        hodge_number_table=lambda: {
            (0, 0): NN(1),
            (2, 0): NN(1),
            (0, 2): NN(1),
            (1, 1): NN(middle_rank - 2),
            (2, 2): NN(1),
        },
        polarizable_weights=frozenset(weights),
        name="H^*(X(CC); ZZ) of a smooth quartic K3 surface X",
    )


def _free_integral_topology_group(degree, rank):
    r"""``ZZ^rank``, the free group ``H^degree(X; ZZ)`` that the caller's theorem computes.

    ``H^degree(X; ZZ)`` is an object of ``Modules(ZZ)`` and nothing more: the
    space and the degree are the arguments of the cohomology functor, not data
    of its value.
    """
    return _owned_integers()._fresh_free_module_on(
        finite_ordered_set(tuple(f"H{degree}_{index}" for index in range(rank))),
    )


def _zmod2_integral_topology_group():
    r"""``ZZ/2``, presented as the cokernel of ``2: ZZ -> ZZ``."""
    from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
        _presented_module_from_morphism,
    )

    integers = _owned_integers()
    source = integers.free_module(1)
    target = integers.free_module(1)
    presentation = source.module_category().Mor(source, target)({0: integers(2) * target.module_generator(0)})
    return _presented_module_from_morphism(presentation)


@cached_function
@cached_function
def NodalCubic():
    r"""Return the rational nodal cubic ``y^2 z = x^2(x+z)`` in ``P^2``."""
    from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

    base = _owned_rationals()
    plane = ProjectiveSpaces(base)(2, names=("x", "y", "z"))
    ring = plane.O(3).global_sections().homogeneous_coordinate_ring()
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    z = ring.algebra_generator("z")
    return plane.closed_subscheme(y**2 * z - x**2 * (x + z))


@cached_function
def NodalCubicNormalization():
    r"""Return the explicit normalization ``P^1 -> C`` of :func:`NodalCubic`."""
    from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

    curve = NodalCubic()
    plane = curve.inclusion().codomain()
    line = ProjectiveSpaces(curve.scheme_base_ring())(1, names=("s", "t"))
    ring = line.O(3).global_sections().homogeneous_coordinate_ring()
    s = ring.algebra_generator("s")
    t = ring.algebra_generator("t")
    ambient = line.projective_morphism_from_coordinates(
        plane,
        ((s**2 - t**2) * t, s * (s**2 - t**2), t**3),
    )
    normalization = curve.corestriction(ambient)
    return normalization


def _geometric_fundamental_group(generator, scheme, base_point):
    r"""``pi_1(X(CC), x)``, the cyclic group on ``generator``, an object of ``Groups``.

    The pointed space ``(X(CC), x)`` is the argument of the fundamental-group
    functor on pointed spaces; the value is a group and records neither.
    """
    assert base_point.codomain() is scheme, (
        f"the base point {base_point} of pi_1 is a point of {base_point.codomain()}, not of {scheme}"
    )
    return CyclicGroups()(generator)


def _nodal_cubic_fundamental_group(scheme=None, base_point=None):
    r"""Return the pointed ``pi_1`` of the rational nodal cubic, an infinite cyclic group."""
    selected = NodalCubic() if scheme is None else scheme
    assert selected is NodalCubic(), (
        f"this fundamental group is computed only for the nodal cubic {NodalCubic()}, not for {selected}"
    )
    point = selected.point_morphism((0, 1, 0)) if base_point is None else base_point
    generator = next(iter(OwnedGroups().Free(1).group_generators()))
    return _geometric_fundamental_group(generator, selected, point)


def _projective_line_fundamental_group(line, base_point):
    r"""Return the trivial pointed fundamental group of one represented projective line."""
    return _geometric_fundamental_group(OwnedGroups().C(1).one(), line, base_point)


class NodalCubicIntegralTopology(SageObject):
    r"""Ordinary and normalization-resolution cohomology of the rational nodal cubic.

    Analytically, identifying the two preimages of the node in ``P^1`` gives
    ``C(C) ~= S^2 vee S^1``.  Thus ordinary cohomology has ``H^1=Z``, while
    resolution cohomology means the ordinary cohomology of the normalization
    ``P^1`` and has ``H^1=0``.  The normalization morphism supplies the actual
    contravariant comparison map between the two selected theories.
    """

    def __init__(self, scheme=None) -> None:
        selected = NodalCubic() if scheme is None else scheme
        assert selected is NodalCubic(), (
            f"this topology of X(CC) is computed only for the nodal cubic {NodalCubic()}, not for {selected}"
        )
        self._scheme = selected

    def scheme(self):
        return self._scheme

    @cached_method
    def normalization_morphism(self):
        return NodalCubicNormalization()

    def normalization_scheme(self):
        return self.normalization_morphism().domain()

    @cached_method
    def base_point(self):
        return self.scheme().point_morphism((0, 1, 0))

    @cached_method
    def normalization_base_point(self):
        point = self.normalization_scheme().point_morphism((1, 0))
        image = self.normalization_morphism().image_of_point(point)
        assert tuple(image.point_coordinates()) == tuple(self.base_point().point_coordinates()), (
            f"the normalization P^1 -> {self.scheme()} sends [1:0] to {image}, not to the base "
            f"point {self.base_point()} of the nodal cubic"
        )
        return point

    @cached_method
    def fundamental_group(self):
        return _nodal_cubic_fundamental_group(self.scheme(), self.base_point())

    @cached_method
    def normalization_fundamental_group(self):
        return _projective_line_fundamental_group(
            self.normalization_scheme(),
            self.normalization_base_point(),
        )

    @cached_method
    def normalization_fundamental_group_map(self):
        r"""Return the induced map ``pi_1(P^1)->pi_1(C)`` of the pointed normalization."""
        source = self.normalization_fundamental_group()
        target = self.fundamental_group()
        induced = source.Mor(target)(())
        return induced

    @cached_method
    def ordinary_cohomology(self, degree):
        degree = int(degree)
        assert degree >= 0, (
            f"singular cohomology of {self.scheme()} is defined in degrees >= 0, not in degree {degree}"
        )
        rank = 1 if degree in (0, 1, 2) else 0
        return _free_integral_topology_group(degree, rank)

    @cached_method
    def resolution_cohomology(self, degree):
        degree = int(degree)
        assert degree >= 0, (
            f"singular cohomology of the normalization of {self.scheme()} is defined in degrees "
            f">= 0, not in degree {degree}"
        )
        rank = 1 if degree in (0, 2) else 0
        return _free_integral_topology_group(degree, rank)

    @cached_method
    def normalization_pullback(self, degree):
        r"""Return ``nu^*:H^degree(C,Z)->H^degree(P^1,Z)`` for the normalization."""
        source = self.ordinary_cohomology(degree)
        target = self.resolution_cohomology(degree)
        source_labels = tuple(source.module_generating_set())
        target_labels = tuple(target.module_generating_set())
        if len(source_labels) == len(target_labels) == 1:
            return source.module_category().Mor(source, target)({source_labels[0]: target.module_generator(target_labels[0])})
        return source.module_category().Mor(source, target)({label: target.zero() for label in source_labels})

    def _repr_(self) -> str:
        return f"Integral topology of {self.scheme()} with normalization {self.normalization_scheme()}"



@cached_function
def ProjectiveGeneralLinearGroup2():
    r"""Return ``PGL_2`` over ``QQ`` as ``P^3 - V(ad-bc)``."""
    from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

    base = _owned_rationals()
    projective = ProjectiveSpaces(base)(3, names=("a", "b", "c", "d"))
    sections = projective.O(2).global_sections()
    ring = sections.homogeneous_coordinate_ring()
    a = ring.algebra_generator("a")
    b = ring.algebra_generator("b")
    c = ring.algebra_generator("c")
    d = ring.algebra_generator("d")
    return projective.closed_subscheme(a * d - b * c).open_complement()


def _pgl2_fundamental_group(scheme=None, base_point=None):
    r"""Return the pointed ``pi_1(PGL_2(C)) ~= C_2``."""
    selected = ProjectiveGeneralLinearGroup2() if scheme is None else scheme
    assert selected is ProjectiveGeneralLinearGroup2(), (
        f"this fundamental group is computed only for PGL_2, not for {selected}"
    )
    point = selected.point_morphism((1, 0, 0, 1)) if base_point is None else base_point
    generator = next(iter(OwnedGroups().C(2).group_generators()))
    return _geometric_fundamental_group(generator, selected, point)


class PGL2IntegralTopology(SageObject):
    r"""Ordinary integral cohomology of ``PGL_2(C)`` via its ``SO(3)`` retract.

    Polar decomposition retracts ``PGL_2(C)`` onto ``PU(2) ~= SO(3) ~= RP^3``.
    Hence the integral cohomology has ``Z`` in degrees 0 and 3, ``Z/2`` in
    degree 2, and zero otherwise.  This torsion is deliberately retained and
    disappears after rational coefficient change.
    """

    _realization = "PGL_2(C)=P^3(C)-V(ad-bc), deformation retracted by polar decomposition to PU(2) ~= SO(3) ~= RP^3"

    def __init__(self, scheme=None) -> None:
        selected = ProjectiveGeneralLinearGroup2() if scheme is None else scheme
        assert selected is ProjectiveGeneralLinearGroup2(), (
            f"this topology of X(CC) is computed only for PGL_2, not for {selected}"
        )
        self._scheme = selected

    def scheme(self):
        return self._scheme

    def realization_description(self):
        return self._realization

    @cached_method
    def base_point(self):
        return self.scheme().point_morphism((1, 0, 0, 1))

    @cached_method
    def fundamental_group(self):
        return _pgl2_fundamental_group(self.scheme(), self.base_point())

    @cached_method
    def integral_cohomology(self, degree):
        degree = int(degree)
        assert 0 <= degree <= 6, (
            f"PGL_2(CC) has complex dimension 3, so its singular cohomology is computed in "
            f"degrees 0 through 6, but degree {degree} was requested"
        )
        if degree == 2:
            return _zmod2_integral_topology_group()
        if degree in (0, 3):
            return _free_integral_topology_group(degree, 1)
        return _free_integral_topology_group(degree, 0)

    @cached_method
    def rational_cohomology(self, degree):
        integers = _owned_integers()
        extension = integers.fraction_field_map()
        return self.integral_cohomology(degree).base_change(extension)

    @cached_method
    def coefficient_change_to_rationals(self, degree):
        from sage_extensions.categories.modules.pure.modules import Modules

        integers = _owned_integers()
        extension = integers.fraction_field_map()
        return Modules(integers).base_change_adjunction(extension).unit(self.integral_cohomology(degree))

    def _repr_(self) -> str:
        return f"Integral topology of {self.scheme()} ({self.realization_description()})"



def _require_smooth_complete_rational_toric_realization(scheme):
    assert _engine_ring(scheme.scheme_base_ring()) is SageQQ, (
        f"the integral singular cohomology of the toric variety {scheme} is computed only over "
        f"QQ, embedded in CC, but its base ring is {scheme.scheme_base_ring()}"
    )
    assert scheme.fan().is_smooth() and scheme.fan().is_complete(), (
        f"the Jurkiewicz-Danilov theorem computing H^*({scheme}(CC), ZZ) needs a smooth complete "
        f"toric variety, but its fan is smooth: {scheme.fan().is_smooth()}, complete: "
        f"{scheme.fan().is_complete()}"
    )


def _toric_integral_singular_cohomology(scheme, degree):
    r"""Return ``H^degree(X(CC),ZZ)`` through the integral toric cycle comparison.

    For a smooth complete complex toric variety, Danilov--Jurkiewicz identifies
    the integral Chow ring with integral singular cohomology, with invariant
    divisor classes in Chow codimension ``k`` mapping to degree ``2k``.
    Odd cohomology vanishes and the even groups are torsion-free.
    """
    _require_smooth_complete_rational_toric_realization(scheme)
    degree = int(degree)
    dimension = int(scheme.dimension())
    assert 0 <= degree <= 2 * dimension, (
        f"singular cohomology of {scheme}(CC) is computed in degrees 0 through {2 * dimension} "
        f"(twice its dimension), but degree {degree} was requested"
    )
    if degree % 2:
        return _free_integral_topology_group(degree, 0)

    codimension = degree // 2
    chow = scheme.chow_group(dimension - codimension)
    return chow._same_presentation_module(chow.module_generating_set())


def _toric_cycle_class_isomorphism(scheme, codimension):
    r"""Return ``CH^k(X) -> H^(2k)(X(CC),ZZ)`` for smooth complete toric ``X/QQ``."""
    _require_smooth_complete_rational_toric_realization(scheme)
    codimension = int(codimension)
    dimension = int(scheme.dimension())
    assert 0 <= codimension <= dimension, (
        f"cycles on {scheme} have codimension 0 through {dimension} (its dimension), but "
        f"codimension {codimension} was requested"
    )
    chow = scheme.chow_group(dimension - codimension)
    cohomology = scheme.integral_singular_cohomology(2 * codimension)
    forward = chow.module_category().Mor(chow, cohomology)({label: cohomology.module_generator(label) for label in chow.module_generating_set()})
    inverse = cohomology.module_category().Mor(cohomology, chow)({label: chow.module_generator(label) for label in cohomology.module_generating_set()})
    return chow.module_category().Core().Mor(chow, cohomology)(forward, inverse)


def _toric_picard_to_chow_isomorphism(scheme):
    r"""Return ``Pic(X) -> CH^1(X)`` for a smooth complete toric surface."""
    _require_smooth_complete_rational_toric_realization(scheme)
    assert int(scheme.dimension()) == 2, (
        f"the isomorphism Pic -> CH^1 is constructed here only for toric surfaces, but {scheme} "
        f"has dimension {scheme.dimension()}"
    )
    picard = scheme.picard_group()
    chow = scheme.chow_group(1)
    cycles = scheme.torus_invariant_cycle_group(1)
    cycle_projection = scheme.torus_invariant_cycle_class_map(1)
    forward = picard.module_category().Mor(picard, chow)({label: cycle_projection(cycles.module_generator(label)) for label in picard.module_generating_set()})
    return picard.module_category().Core().Mor(picard, chow)(forward, forward.inverse())


def _toric_middle_cohomology_form(scheme):
    r"""Return ``H^2(X(CC),ZZ)`` with its cup-product intersection form."""
    from sage_extensions.categories.modules.framed.formed.form_modules import BilinearFormModules

    _require_smooth_complete_rational_toric_realization(scheme)
    assert int(scheme.dimension()) == 2, (
        f"the intersection form on H^2 is constructed here only for toric surfaces, but {scheme} "
        f"has dimension {scheme.dimension()}"
    )
    cohomology = scheme.integral_singular_cohomology(2)
    cycle_class = scheme.cycle_class_isomorphism(1)
    picard_to_chow = scheme.picard_to_chow_isomorphism()
    cohomology_to_picard = picard_to_chow.inverse() * cycle_class.inverse()
    intersection = scheme.picard_intersection_pairing()
    integers = _owned_integers()
    # Degree-two classes commute under cup product.
    return BilinearFormModules(integers).Symmetric()(
        cohomology.bilinear_forms(integers)(
            lambda left, right: intersection(
                cohomology_to_picard(left),
                cohomology_to_picard(right),
            )
        )
    )


def _toric_fundamental_group(scheme, base_point_cone=None):
    r"""Return the pointed ``pi_1`` of a smooth complete toric complex realization.

    For a normal toric variety ``X_Sigma``, the fundamental group is the
    quotient of ``N`` by the sublattice generated by ``|Sigma| cap N``.  A
    complete fan has full support, hence that quotient is trivial.  A maximal
    cone is retained as the selected torus-fixed basepoint.
    """
    _require_smooth_complete_rational_toric_realization(scheme)
    maximal = scheme.fan().maximal_cones()
    if base_point_cone is None:
        base_point_cone = next(iter(maximal))
    assert base_point_cone in maximal, (
        f"the base point of pi_1({scheme}) must be the torus-fixed point of a maximal cone, but "
        f"{base_point_cone} is not a maximal cone of the fan"
    )
    return CyclicGroups()(OwnedGroups().C(1).one())


def _toric_hodge_structure(scheme):
    r"""``H^*(X(CC); ZZ)`` of a smooth complete toric variety ``X``, split by degree.

    ``Gr^W_k = H^k``.  By Jurkiewicz–Danilov ``H^*`` is free, zero in odd
    degree, and ``H^{2p}`` is spanned by the classes of torus-invariant
    cycles, so ``H^{2p}`` is a sum of copies of ``ZZ(-p)`` and the structure
    is Hodge–Tate.
    """
    _require_smooth_complete_rational_toric_realization(scheme)
    dimension = int(scheme.dimension())
    weights = tuple(
        degree
        for degree in range(2 * dimension + 1)
        for _ in range(int(scheme.integral_singular_cohomology(degree).module_rank()))
    )
    return _split_mixed_hodge_structure(_owned_integers(), weights, name=f"H^*({scheme}(CC); ZZ)")


def _complete_intersection_integral_singular_cohomology(scheme, degree):
    r"""``H^degree(X(CC), ZZ)`` of a smooth projective complete intersection ``X`` over ``QQ``.

    Let ``X <= P^{n+c}`` be smooth of dimension ``n >= 1``, cut out by
    equations of degrees ``d_1, ..., d_c``.  Dimca, *Singularities and
    Topology of Hypersurfaces* [Dim92], Ch. 5, §3:

    - Lemma (3.1): ``H^*(X; ZZ)`` is torsion-free;
    - (3.2): ``H^k(X) = H^k(P^n)`` for ``k != n`` (the Lefschetz
      hyperplane theorem, Lazarsfeld [Laz04] Thm. 3.1.17 and
      Example 3.1.31 for complete intersections, with Poincare duality);
    - (3.4): ``chi(X) = <c_n(X), [X]>``, and the normal bundle sequence gives
      ``(1 + a)^{n+c+1} = c(X) (1 + d_1 a) ... (1 + d_c a)`` with
      ``a^n = d_1 ... d_c g`` for ``g`` a generator of ``H^{2n}(X)``.

    So ``chi(X) = d_1 ... d_c [t^n] (1 + t)^{n+c+1} / prod (1 + d_i t)``, and
    the even degrees ``k != n`` contribute ``n + 1 - [n even]`` to the
    alternating sum, which leaves
    ``b_n = (-1)^n (chi(X) - (n + 1) + [n even])``.

    A smooth quartic surface is a K3 surface, and its middle cohomology with
    the cup product is the K3 lattice (Huybrechts, *Lectures on K3
    Surfaces* [Huy16], Ch. 1, Prop. 3.5); that case returns the groups of
    the marked K3 topology, which carry the cup product.
    """
    from sage.rings.power_series_ring import PowerSeriesRing

    from sage_extensions.categories.schemes.complete_intersections import (
        ProjectiveCompleteIntersections,
    )

    base = scheme.scheme_base_ring()
    assert scheme in ProjectiveCompleteIntersections(base), (
        f"the Lefschetz computation of H^*({scheme}(CC); ZZ) needs a projective complete "
        f"intersection, but {scheme} is in {scheme.category()}"
    )
    assert bool(scheme.is_smooth()), (
        f"the Lefschetz computation of H^*({scheme}(CC); ZZ) (Dimca, Ch. 5, §3) needs a smooth "
        f"complete intersection, and {scheme} is singular"
    )
    dimension = int(scheme.expected_dimension())
    assert dimension >= 1, (
        f"the Lefschetz computation of H^*({scheme}(CC); ZZ) (Dimca, Ch. 5, (2.1)) needs "
        f"dimension n >= 1, but {scheme} has dimension {dimension}"
    )
    degree = int(degree)
    degrees = tuple(int(value) for value in scheme.defining_degrees())
    if (dimension, degrees) == (2, (4,)):
        return scheme.integral_topology().integral_cohomology(degree)
    if degree < 0 or degree > 2 * dimension:
        return _free_integral_topology_group(degree, 0)
    if degree != dimension:
        return _free_integral_topology_group(degree, 1 - degree % 2)
    series = PowerSeriesRing(SageZZ, "t", default_prec=dimension + 1)
    t = series.gen()
    normal_chern = prod((1 + equation_degree * t for equation_degree in degrees), start=series.one())
    chern = (1 + t) ** (dimension + len(degrees) + 1) * ~normal_chern
    euler = prod(degrees, start=SageZZ.one()) * chern[dimension]
    middle = (-1) ** dimension * (euler - (dimension + 1) + (1 - dimension % 2))
    return _free_integral_topology_group(degree, int(middle))


class _ComplexRealizationTopologyData(SageObject):
    r"""The analytic topology of ``X(CC)``.

    The open sets are those of the topology induced on each affine chart by
    the Euclidean topology of ``CC^r``.  No subset of ``X(CC)`` other than
    the empty set and the whole space is represented, so openness is decided
    for those two only.
    """

    def __init__(self, scheme) -> None:
        self._scheme = scheme

    def open_subsets(self, space):
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset) -> bool:
        power = space.power_set()
        selected = power(subset)
        match selected:
            case _ if selected == power.bottom():
                return True
            case _ if selected == power.top():
                return True
            case _:
                assert False, (
                    f"whether {subset} is open in {space} is decided only for the empty set and "
                    "the whole space: no other subset of the complex points is represented"
                )


class _ComplexRealizationEngine:
    r"""Private realization of ``X(CC)`` along ``sigma: k -> CC`` in ``TopologicalSpaces``."""

    def __init__(self, scheme, scalar_embedding, **rest) -> None:
        self._scheme = scheme
        self._scalar_embedding = scalar_embedding
        super().__init__(**rest)

    def scheme(self):
        return self._scheme

    def scalar_embedding(self):
        return self._scalar_embedding

    def __contains__(self, point) -> bool:
        return element_parent(point) is self

    is_parent_of = __contains__

    def _element_constructor_(self, point):
        match element_parent(point) is self:
            case True:
                return point
            case False:
                assert False, (
                    f"{point} is not a point of {self}: no complex point of {self.scheme()} is "
                    "constructed"
                )

    @cached_method
    def singular_cohomology(self, coefficients):
        r"""``H^*(X(CC); R)``, through the theorem that computes it for the category of ``X``.

        Projective space ``P^n``: Hatcher, *Algebraic Topology* [Hat02],
        Thm. 3.19, ``H^*(CP^n; ZZ) = ZZ[alpha]/(alpha^{n+1})`` with
        ``|alpha| = 2``.  Every ``H^k(CP^n; ZZ)`` is free, so the universal
        coefficient theorem gives ``H^*(CP^n; R) = R[alpha]/(alpha^{n+1})``
        for every ring ``R`` ([Hat02], Thm. 3.2).
        """
        from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

        scheme = self.scheme()
        match scheme:
            case _ if scheme in ProjectiveSpaces(scheme.scheme_base_ring()):
                from sage_extensions.categories.algebras.graded_algebras import (
                    _truncated_polynomial_graded_algebra,
                )

                return _truncated_polynomial_graded_algebra(
                    coefficients, 2, int(scheme.dimension())
                )
            case _:
                assert False, (
                    f"the cup product on H^*({self}; {coefficients}) is computed only for projective "
                    f"spaces, and {scheme} is in {scheme.category()}"
                )

    @cached_method
    def integral_singular_cohomology(self, degree):
        r"""``H^degree(X(CC); ZZ)``, through the theorem that computes it for the category of ``X``.

        - a smooth complete toric variety: the cycle map ``CH^k -> H^{2k}`` is
          an isomorphism and odd cohomology vanishes (Danilov--Jurkiewicz);
        - a smooth projective complete intersection: the Lefschetz hyperplane
          theorem and the Euler number of its Chern class (Dimca, Ch. 5, §3);
        - projective space ``P^n``: Hatcher, *Algebraic Topology* [Hat02],
          Thm. 3.19, ``H^*(CP^n; ZZ) = ZZ[alpha]/(alpha^{n+1})`` with
          ``|alpha| = 2``, so ``H^k`` is free of rank one for even
          ``0 <= k <= 2n`` and zero otherwise.
        """
        from sage_extensions.categories.schemes.complete_intersections import (
            ProjectiveCompleteIntersections,
        )
        from sage_extensions.categories.schemes.schemes import ProjectiveSpaces
        from sage_extensions.categories.schemes.toric.toric_schemes import (
            ToricSchemes,
        )

        scheme = self.scheme()
        base = scheme.scheme_base_ring()
        match scheme:
            case _ if scheme in ProjectiveSpaces(base):
                return self.singular_cohomology(_owned_integers()).graded_piece(degree)
            case _ if scheme in ToricSchemes(base):
                return _toric_integral_singular_cohomology(scheme, degree)
            case _ if scheme in ProjectiveCompleteIntersections(base):
                return _complete_intersection_integral_singular_cohomology(scheme, degree)
            case _:
                assert False, (
                    f"H^{degree}({self}; ZZ) is computed only for projective spaces, smooth complete toric "
                    f"varieties and smooth projective complete intersections, and {scheme} is in "
                    f"{scheme.category()}"
                )

    def _finite_cw_dimension(self):
        r"""``2 dim X`` for smooth ``X``: the protected contract of :class:`TopologicalSpaces`.

        Dimca [Dim92], Ch. 1, (6.10): an algebraic variety has the homotopy
        type of a finite CW complex.  Lazarsfeld [Laz04], §3.1.A: a
        nonsingular complex variety of dimension ``n`` is a ``C^infty``
        manifold of real dimension ``2n``, hence of the homotopy type of a CW
        complex of dimension ``<= 2n``.
        """
        scheme = self.scheme()
        assert bool(scheme.is_smooth()), (
            f"the bound 2 dim X on the CW dimension of {self} is stated (Lazarsfeld, §3.1.A) for "
            f"nonsingular X, and {scheme} is singular"
        )
        return 2 * int(scheme.dimension())

    def _repr_(self) -> str:
        return f"Complex points of {self.scheme()} along {self.scalar_embedding()}"


@cached_function(key=lambda scheme, scalar_embedding: (id(scheme), id(scalar_embedding)))
def _complex_realization(scheme, scalar_embedding):
    return _object_of(
        TopologicalSpaces(),
        _engine=(TopologicalSpaces(), _ComplexRealizationEngine, None),
        topology_data=_ComplexRealizationTopologyData(scheme),
        scheme=scheme,
        scalar_embedding=scalar_embedding,
    )


@cached_function
def _integral_singular_cohomology_over_rationals(scheme, degree):
    """Integral cohomology after the canonical rational-to-complex base change."""
    assert _engine_ring(scheme.scheme_base_ring()) is SageQQ, (
        f"H^{degree}({scheme}(CC); ZZ) is computed along the unique embedding QQ -> CC, but "
        f"{scheme} is over {scheme.scheme_base_ring()}"
    )
    return scheme.complex_realization(_rational_complex_embedding()).integral_singular_cohomology(degree)


def _rational_complex_embedding():
    r"""The embedding ``QQ -> CC``; it is the only one, since ``QQ`` is the prime field."""
    rationals = _owned_rationals()
    complexes = _owned_complex_field()
    return rationals.Mor(complexes, category=OwnedRings())(lambda scalar: complexes(scalar))


__all__ = [
    "NodalCubicIntegralTopology",
    "NodalCubicNormalization",
    "NodalCubic",
    "ProjectiveGeneralLinearGroup2",
    "PGL2IntegralTopology",
    "AffineGeometricCohomologyComplexes",
    "ToricGeometricLineBundleCohomologySpaces",
    "ToricWeightCohomologyComplexes",
]
