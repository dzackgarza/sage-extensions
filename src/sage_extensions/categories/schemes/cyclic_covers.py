r"""Relative cyclic covers of an affine scheme, with their deck action.

Let ``X = Spec(A)``, let ``L`` be an invertible ``O_X``-module, let ``n >= 1``
and let ``s`` be a section of ``L^n``.  The cyclic cover of degree ``n``
branched along ``s`` is the relative spectrum of the ``O_X``-algebra
``⊕_{i=0}^{n-1} L^{-i}``, whose multiplication
``L^{-i} ⊗ L^{-j} -> L^{-(i+j)}`` is the identity when ``i + j < n`` and is
multiplication by ``s`` when ``i + j >= n`` (Barth, Hulek, Peters and Van de
Ven, *Compact Complex Surfaces*, I.17).

That algebra is owned by ``CyclicCoverAlgebra``, which builds it for any
invertible sheaf represented by rank-one descent on an affine cover: on each
chart it is the trivialized algebra returned by
``R.cyclic_cover_presentation(f, n)``, and
the charts are glued by the transition units of ``L``.  One construction
therefore supplies the multiplication, the underlying finite module on
``1, z, ..., z^{n-1}``, the local equation ``z^n - f`` and every scalar change
of it, on the charts and here alike.

The covers constructed in this category are the globally trivialized ones,
``L = O_X`` on the affine ``X = Spec(A)``: the section is an element ``f`` of
``A``, the descent is vacuous, and the cover algebra is the single chart
algebra ``A[z]/(z^n - f)``.  The graded summand ``A z^i`` is the
trivialization of ``L^{-i}``.

The deck group is always the group scheme ``mu_n``, acting through the scheme
morphism whose coordinate pullback sends ``z`` to ``u z``.  When the scalars
contain a primitive ``n``-th root of unity ``zeta`` and ``n`` is invertible,
this action also has the familiar constant ``C_n`` realization
``z -> zeta z``.  The two notions are kept separate: the constant action is an
additional identification, never a replacement for ``mu_n``.

The quotient by the deck action is ``X`` again: the ``mu_n``-coaction gives
the summand ``A z^i`` weight ``i`` modulo ``n``, so the invariant subalgebra is
the degree-zero part ``A``.  This is a theorem about the grading, not an
invariant-ring computation, and it does not require a primitive root of unity.

For nontrivial ``L``, relative ``Spec`` is assembled from the affine spectra
of the local algebras.  Above a base overlap ``U_i cap U_j`` the cover chart is
the distinguished open of ``Spec(B_i)`` obtained by inverting the image of the
other base-chart denominator.  The finite-free basis ``1,z,...,z^(n-1)`` and
the line-bundle transition ``z_i = u_ij^-1 z_j`` determine the overlap
isomorphism, so the existing finite scheme-gluing owner constructs the global
cover and its map to ``X`` without turning compatible global sections into a
fictional affine coordinate ring.

The canonical-bundle formula and the smoothness criteria of a cover are also
not constructed here: both read the module of differentials of the cover
algebra against the invertible sheaves of the divisor layer.
"""

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.arrow_categories import CommutativeSquare
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.algebras.cyclic_cover_algebras import (
    CYCLIC_COVER_VARIABLE,
    CyclicCoverAlgebra,
)
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedRings,
    _engine_ring,
    _own_ring,
)
from sage_extensions.categories.schemes.group_schemes import (
    AffineGroupSchemes,
    AffineGroupSchemeActions,
)
from sage_extensions.categories.schemes.schemes import (
    AffineGSchemes,
    Schemes,
    _affine_morphism_from_pullback,
    _affine_scheme,
    _affine_spec_morphism,
)
from sage_extensions.validation import validator

_ROOT_OF_UNITY_VARIABLE = "t"


def _relative_cyclic_cover(cyclic_algebra, *, _engine=None, construction_data=None):
    r"""Return the cyclic cover through the general relative-Spec owner."""
    data = dict(construction_data or {})
    data.setdefault("cyclic_algebra", cyclic_algebra)
    return cyclic_algebra.gluing_datum().relative_spectrum(
        _engine=_engine,
        construction_data=data,
    )


def _relative_cover_chart(cyclic_algebra, chart_index):
    r"""Read the chosen base chart from the cyclic-algebra presentation owner.

    An affine scheme may also carry a finite-atlas presentation; affineness
    alone does not choose between that presentation and a distinguished cover.
    """
    return cyclic_algebra._chart_scheme(chart_index)


def _mu_n_action_on_affine_cover(cover, group_scheme):
    r"""The action ``mu_n x X -> X`` on ``X = Spec(A[z]/(z^n - f))`` with coaction ``z |-> u z``."""
    cover_algebra = cover.coordinate_algebra()
    product = cover.scheme_category().product((group_scheme.scheme(), cover))
    product_algebra = product.coordinate_algebra()
    group_pullback = product.projection(0).coordinate_algebra_morphism()
    cover_pullback = product.projection(1).coordinate_algebra_morphism()
    group_coordinate = group_scheme.scheme().coordinate_algebra().algebra_generator("u")
    z = cover_algebra.algebra_generator(CYCLIC_COVER_VARIABLE)
    action_pullback = cover_algebra.Mor(product_algebra)(
        {CYCLIC_COVER_VARIABLE: group_pullback(group_coordinate) * cover_pullback(z)}
    )
    return AffineGroupSchemeActions(group_scheme)(
        cover,
        _affine_morphism_from_pullback(product, cover, action_pullback),
    )


def _local_relative_cyclic_deck_action(cyclic_algebra, chart_index):
    r"""Return the canonical ``mu_n`` action on one affine chart of a relative cyclic cover."""
    chart_index = cyclic_algebra.chart_index_set()(chart_index)
    local_base = _relative_cover_chart(cyclic_algebra, chart_index).coordinate_algebra()
    local_scheme = cyclic_algebra.local_algebra(chart_index).affine_spectrum()
    group_scheme = AffineGroupSchemes(local_base).roots_of_unity(int(cyclic_algebra.degree()))
    return _mu_n_action_on_affine_cover(local_scheme, group_scheme)


def _deck_scalar(cyclic_algebra, root_of_unity):
    r"""``root_of_unity`` in the scalars of the base, asserted to be an ``n``-th root of unity."""
    scalar_ring = cyclic_algebra.scheme().scheme_base_ring()
    root = scalar_ring(root_of_unity)
    assert root ** int(cyclic_algebra.degree()) == scalar_ring.one(), (
        f"the deck scalar {root} is not a {cyclic_algebra.degree()}-th root of unity"
    )
    return root


def _relative_cyclic_local_deck_transformation(
    cyclic_algebra, chart_index, root_of_unity
):
    r"""Return ``z_i |-> root*z_i`` on one affine chart of a relative cover."""
    root = _deck_scalar(cyclic_algebra, root_of_unity)
    local_algebra = cyclic_algebra.local_algebra(chart_index)
    local_base = _relative_cover_chart(cyclic_algebra, chart_index).coordinate_algebra()
    scalar = local_algebra.algebra_structure_morphism()(local_base(root))
    z = local_algebra.algebra_generator(CYCLIC_COVER_VARIABLE)
    pullback = local_algebra.Mor(local_algebra)(
        {CYCLIC_COVER_VARIABLE: scalar * z}
    )
    local_scheme = cyclic_algebra.relative_spectrum().arrow().domain().gluing_datum().chart(chart_index)
    return _affine_morphism_from_pullback(local_scheme, local_scheme, pullback)


def _relative_cyclic_deck_transformation(cyclic_algebra, root_of_unity):
    r"""Glue the chart automorphisms ``z_i -> zeta z_i`` on the relative cover."""
    root = _deck_scalar(cyclic_algebra, root_of_unity)
    relative = cyclic_algebra.relative_spectrum()
    glued = relative.arrow().domain()
    indices = cyclic_algebra.chart_index_set()
    local_automorphisms = {
        index: cyclic_algebra.local_deck_transformation(index, root)
        for index in indices
    }
    automorphism = glued.Mor(glued)(
        {index: glued.gluing_datum().chart_embedding(index) * local_automorphisms[index] for index in indices}
    )
    assert all(
        relative.arrow().local_map(index) * local_automorphisms[index]
        == relative.arrow().local_map(index)
        for index in indices
    ), (
        f"the deck transformation z -> {root} z of the cyclic cover {glued} does not commute "
        "with the cover map to the base on some chart"
    )
    return automorphism


def _cyclic_cover_base_change(cyclic_algebra, ring_map):
    return CyclicCoverBaseChangeComparison(cyclic_algebra, ring_map)


class _CyclicCoverBaseChangeSquare(CommutativeSquare):
    r"""The commuting square comparing a cyclic cover with its scalar change."""

    def __init__(
        self,
        parent,
        transformation,
        *,
        source_cyclic_algebra,
        ring_map,
        changed_line_bundle,
        changed_branch_power,
        changed_cyclic_algebra,
        local_projections,
    ) -> None:
        self._source = source_cyclic_algebra
        self._ring_map = ring_map
        self._changed_line_bundle = changed_line_bundle
        self._changed_branch_power = changed_branch_power
        self._changed_cyclic = changed_cyclic_algebra
        self._local_projections = local_projections
        super().__init__(parent, transformation)

    def source_cyclic_algebra(self):
        return self._source

    def ring_map(self):
        return self._ring_map

    def changed_line_bundle(self):
        return self._changed_line_bundle

    def changed_branch_power(self):
        return self._changed_branch_power

    def changed_cyclic_algebra(self):
        return self._changed_cyclic

    def base_projection(self):
        r"""The right edge of the cover square: the base-change projection."""
        return self.right()

    def projection(self):
        r"""The left edge of the cover square: the projection of changed covers."""
        return self.left()

    def cover_square_commutes(self):
        r"""Return the retained cover-square equation, including an undecided one."""
        return self.commutativity_decision()

    def local_projection(self, index):
        return self._local_projections[
            self.source_cyclic_algebra().chart_index_set()(index)
        ]

    def lift_commutes(self, source_lift, changed_lift) -> bool:
        if source_lift.cyclic_algebra() is not self.source_cyclic_algebra():
            raise ValueError(
                f"the lift {source_lift} is an automorphism of the cyclic cover of "
                f"{source_lift.cyclic_algebra()}, not of the original cover "
                f"{self.source_cyclic_algebra()} of this base change"
            )
        if changed_lift.cyclic_algebra() is not self.changed_cyclic_algebra():
            raise ValueError(
                f"the lift {changed_lift} is an automorphism of the cyclic cover of "
                f"{changed_lift.cyclic_algebra()}, not of the base-changed cover "
                f"{self.changed_cyclic_algebra()}"
            )
        return all(
            source_lift.local_automorphism(index) * self.local_projection(index)
            == self.local_projection(index) * changed_lift.local_automorphism(index)
            for index in self.source_cyclic_algebra().chart_index_set()
        )

    def deck_commutes(self, root_of_unity) -> bool:
        source = self.source_cyclic_algebra()
        changed = self.changed_cyclic_algebra()
        changed_root = self.ring_map()(
            source.scheme().scheme_base_ring()(root_of_unity)
        )
        return all(
            source.local_deck_transformation(index, root_of_unity)
            * self.local_projection(index)
            == self.local_projection(index)
            * changed.local_deck_transformation(index, changed_root)
            for index in source.chart_index_set()
        )

    def _repr_(self) -> str:
        return f"Cyclic-cover base-change square along {self.ring_map()} for {self.source_cyclic_algebra()}"


def CyclicCoverBaseChangeComparison(cyclic_algebra, ring_map):
    r"""Return the actual commuting square comparing a cyclic cover with its scalar change."""
    line_bundle = cyclic_algebra.line_bundle()
    changed_line_bundle = line_bundle.base_change(ring_map)
    changed_branch_power = changed_line_bundle.tensor_power(int(cyclic_algebra.degree()))
    changed_branch = changed_branch_power.pullback_compatible_section(
        cyclic_algebra.branch_section()
    )
    changed_cyclic = type(cyclic_algebra)(
        changed_line_bundle,
        changed_branch,
        cyclic_algebra.degree(),
    )

    source_relative = cyclic_algebra.relative_spectrum()
    changed_relative = changed_cyclic.relative_spectrum()
    source_cover = source_relative.arrow().domain()
    changed_cover = changed_relative.arrow().domain()
    source_atlas = line_bundle.gluing_datum()
    changed_atlas = changed_line_bundle.gluing_datum()
    base_projection = changed_line_bundle.base_change_projection()
    morphisms = base_projection.parent().mor_category()
    local_projections = {}
    local_maps_to_cover = {}
    for source_index in cyclic_algebra.chart_index_set():
        changed_index = changed_atlas.normalize_chart_index(source_index)
        changed_chart = changed_atlas.chart(changed_index)
        into_source_base = base_projection * changed_atlas.chart_embedding(changed_index)
        chart_projection = source_atlas.chart(source_index).corestriction(
            into_source_base
        )
        base_pullback = chart_projection.coordinate_algebra_morphism()
        source_local = cyclic_algebra.local_algebra(source_index)
        changed_local = changed_cyclic.local_algebra(changed_index)
        source_labels = source_local.module_generating_set()
        changed_labels = changed_local.module_generating_set()
        source_rank = source_labels.ranking_map()

        def image(
            element,
            *,
            source_algebra=source_local,
            target_algebra=changed_local,
            coefficient_map=base_pullback,
            source_ranking=source_rank,
            target_labels=changed_labels,
        ):
            coordinates = source_algebra.framing_morphism().lift(source_algebra(element))
            result = target_algebra.zero()
            for label, coefficient in coordinates.parent()._selected_module_coefficients(coordinates).items():
                position = int(source_ranking(label))
                result += target_algebra.scalar_multiple(
                    coefficient_map(coefficient),
                    target_algebra.module_generator(target_labels[position]),
                )
            return result

        # Coefficients move through the actual base pullback.  This is a
        # ring map, not a linear map over the unchanged source chart ring.
        algebra_map = OwnedRings().Mor(source_local, changed_local).elementwise(image)
        local_projection = morphisms.Mor(
            changed_cover.gluing_datum().chart(changed_index),
            source_cover.gluing_datum().chart(source_index),
        )(algebra_map)
        local_projections[source_index] = local_projection
        local_maps_to_cover[source_index] = (
            source_cover.gluing_datum().chart_embedding(source_index) * local_projection
        )
    projection = morphisms.Mor(changed_cover, source_cover)(local_maps_to_cover)
    # The final square retains this same compatibility equation.  A separate
    # local Boolean recheck would discard its unresolved commutativity datum.

    from sage_extensions.categories.sets.indexed_families import (
        finite_indexed_family,
    )

    local_projection_family = finite_indexed_family(
        cyclic_algebra.chart_index_set(),
        lambda index: local_projections[index],
        name="Local projections of a scalar-changed cyclic cover",
    )
    arrows = morphisms.ArrowCategory()
    changed_cover_map = arrows(changed_relative.arrow())
    source_cover_map = arrows(source_relative.arrow())
    return arrows.Mor(changed_cover_map, source_cover_map)._square(
        projection,
        base_projection,
        verify=False,
        element_class=_CyclicCoverBaseChangeSquare,
        construction_data={
            "source_cyclic_algebra": cyclic_algebra,
            "ring_map": ring_map,
            "changed_line_bundle": changed_line_bundle,
            "changed_branch_power": changed_branch_power,
            "changed_cyclic_algebra": changed_cyclic,
            "local_projections": local_projection_family,
        },
    )


class _RelativeCyclicCoverLiftSquare(CommutativeSquare):
    r"""A cyclic-cover lift as an endomorphism square of the cover map."""

    def __init__(
        self,
        parent,
        transformation,
        *,
        cyclic_algebra,
        linearization,
        group_element,
        local_automorphisms,
    ) -> None:
        self._cyclic_algebra = cyclic_algebra
        self._linearization = linearization
        self._group_element = linearization.acting_group()(group_element)
        self._local_automorphisms = local_automorphisms
        super().__init__(parent, transformation)

    def cyclic_algebra(self):
        return self._cyclic_algebra

    def linearization(self):
        return self._linearization

    def group_element(self):
        return self._group_element

    def base_automorphism(self):
        r"""The right edge of the lift square."""
        return self.right()

    def automorphism(self):
        r"""The left edge of the lift square."""
        return self.left()

    def local_automorphisms(self):
        return self._local_automorphisms

    def local_automorphism(self, index):
        return self.local_automorphisms()[self.cyclic_algebra().chart_index_set()(index)]

    def fiber_scalar(self):
        return self.linearization().character_value(self.group_element()).inverse_of_unit()

    @cached_method
    def branch_preservation_decision(self):
        r"""Decide the branch law of the retained linearization, or retain it.

        On a trivializing chart the selected lift has coefficient map
        ``sigma`` and sends ``z`` to ``c*z``.  Its branch equation is
        ``sigma(f) = c^n*f`` for the retained quotient ``z^n = f``.
        This is an additional premise on the selected linearization and
        branch section, not a proof inferred from membership in a ring Mor.
        """
        from sage_extensions.logic import conjunction

        cyclic = self.cyclic_algebra()
        linearization = self.linearization()
        group_element = self.group_element()
        fiber_scalar = self.fiber_scalar()
        equations = []
        for index in cyclic.chart_index_set():
            coefficient_map = linearization.local_chart_automorphism(
                group_element, index
            ).coordinate_algebra_morphism()
            base = cyclic.local_algebra(index).base_ring()
            scalar = base.algebra_structure_morphism()(fiber_scalar)
            branch = cyclic.local_branch_coefficient(index)
            equations.append(
                coefficient_map(branch) == scalar ** int(cyclic.degree()) * branch
            )
        return conjunction(equations)

    @validator
    def validate_branch_preservation(self):
        r"""Check the branch equation when requested, retaining an undecided frontier."""
        decision = self.branch_preservation_decision()
        if decision is False:
            raise ValueError(
                f"the selected linearization of {self.cyclic_algebra()} at "
                f"{self.group_element()} does not preserve its branch equation"
            )
        assert decision is True, (
            "no selected coefficient-equality algorithm decides branch preservation "
            f"for {self.cyclic_algebra()} at {self.group_element()}"
        )

    def top_form_scalar(self):
        index = next(iter(self.cyclic_algebra().chart_index_set()))
        determinant = self.linearization().local_jacobian_scalar(
            self.group_element(), index
        )
        return determinant * self.fiber_scalar().inverse_of_unit()

    @cached_method
    def fixed_subscheme(self):
        cover = self.cyclic_algebra().relative_spectrum().arrow().domain()
        return cover.chartwise_fixed_subscheme(self.local_automorphisms())

    def is_fixed_point_free(self) -> bool:
        return all(
            self.local_automorphism(index).fixed_subscheme().is_empty()
            for index in self.cyclic_algebra().chart_index_set()
        )

    def has_order_two(self) -> bool:
        return all(
            (
                self.local_automorphism(index) * self.local_automorphism(index)
                == self.local_automorphism(index).domain().categorical_identity_morphism()
            )
            for index in self.cyclic_algebra().chart_index_set()
        )

    def _repr_(self) -> str:
        return f"Lift square of {self.group_element()} on {self.cyclic_algebra()}"


def RelativeCyclicCoverLift(
    cyclic_algebra,
    linearization,
    group_element,
    base_automorphism,
    local_automorphisms,
    automorphism,
):
    r"""Construct the lift as the commuting endomorphism square of its cover map."""
    relative = cyclic_algebra.relative_spectrum()
    morphisms = base_automorphism.parent().mor_category()
    arrows = morphisms.ArrowCategory()
    cover_map = arrows(relative.arrow())
    result = arrows.Mor(cover_map, cover_map)._square(
        automorphism,
        base_automorphism,
        verify=False,
        element_class=_RelativeCyclicCoverLiftSquare,
        construction_data={
            "cyclic_algebra": cyclic_algebra,
            "linearization": linearization,
            "group_element": group_element,
            "local_automorphisms": local_automorphisms,
        },
    )
    result.validate_branch_preservation(check=False)
    return result



def _relative_cyclic_cover_lift(cyclic_algebra, linearization, group_element):
    r"""Lift one line-bundle-linearized base automorphism to the cyclic cover.

    If ``lambda_g:g^*L -> L`` is the selected linearization, the generator of
    ``L^{-1}`` transforms through ``lambda_g^{-1}``.  On every chart the ring
    pullback therefore sends ``z`` to ``lambda_g^{-1} z`` and acts on the base
    coefficients through the represented chart automorphism.  The branch
    equation is retained by the returned lift's deferred branch validator.
    """
    assert linearization.line_bundle() is cyclic_algebra.line_bundle(), (
        f"cannot lift the action to the cyclic cover of {cyclic_algebra}: {linearization} "
        f"linearizes {linearization.line_bundle()}, not the line bundle "
        f"{cyclic_algebra.line_bundle()} defining the cover"
    )
    group_element = linearization.acting_group()(group_element)
    base_automorphism = linearization.scheme_action_of(group_element)
    relative = cyclic_algebra.relative_spectrum()
    cover = relative.arrow().domain()
    fiber_scalar = linearization.character_value(group_element).inverse_of_unit()
    local_lifts = {}
    for index in cyclic_algebra.chart_index_set():
        local_base_automorphism = linearization.local_chart_automorphism(
            group_element, index
        )
        base_pullback = local_base_automorphism.coordinate_algebra_morphism()
        local_algebra = cyclic_algebra.local_algebra(index)
        local_base = local_algebra.base_ring()
        scalar = local_base.algebra_structure_morphism()(fiber_scalar)
        basis_labels = local_algebra.module_generating_set()
        ranking = basis_labels.ranking_map()

        def image(
            element,
            *,
            algebra=local_algebra,
            pullback=base_pullback,
            scale=scalar,
            rank=ranking,
        ):
            coordinates = algebra.framing_morphism().lift(algebra(element))
            result = algebra.zero()
            for label, coefficient in coordinates.parent()._selected_module_coefficients(coordinates).items():
                exponent = int(rank(label))
                result += algebra.scalar_multiple(
                    pullback(coefficient) * scale**exponent,
                    algebra.module_generator(label),
                )
            return result

        # The selected base automorphism acts on coefficients, so this
        # evaluator is generally semilinear over the chart coefficient ring.
        pullback = OwnedRings().Mor(local_algebra, local_algebra).elementwise(image)
        local_scheme = cover.gluing_datum().chart(index)
        local_lifts[index] = _affine_morphism_from_pullback(
            local_scheme, local_scheme, pullback
        )
    from sage_extensions.categories.sets.indexed_families import finite_indexed_family

    local_family = finite_indexed_family(
        cyclic_algebra.chart_index_set(),
        lambda index: local_lifts[index],
        name="Local automorphisms of a relative cyclic-cover lift",
    )
    automorphism = cover.Mor(cover)(
        {
            index: cover.gluing_datum().chart_embedding(index) * local_family[index]
            for index in cyclic_algebra.chart_index_set()
        }
    )
    # RelativeCyclicCoverLift retains the actual global cover-square law.
    return RelativeCyclicCoverLift(
        cyclic_algebra,
        linearization,
        group_element,
        base_automorphism,
        local_family,
        automorphism,
    )


def _primitive_root_of_unity(scalars, degree):
    r"""Return a primitive ``degree``-th root of unity in ``scalars``.

    The roots of ``t^n - 1`` are computed in the scalars' own polynomial ring
    and one of exact multiplicative order ``n`` is selected.  A primitive root
    exists exactly when the constant group ``C_n`` can act on the cover by
    scaling ``z``; where it does not, the deck group is the group scheme
    ``mu_n`` and this states that rather than substituting a weaker action.
    """
    engine = _engine_ring(scalars)
    assert engine.is_field(), (
        f"a primitive {degree}-th root of unity is chosen here only in a field, but "
        f"{scalars} is not a field"
    )
    characteristic = int(engine.characteristic())
    assert characteristic == 0 or degree % characteristic != 0, (
        f"the characteristic {characteristic} divides the degree {degree}, so "
        "the cover is inseparable and its deck group scheme mu_n is not the "
        "constant group C_n"
    )
    polynomials = engine[_ROOT_OF_UNITY_VARIABLE]
    variable = polynomials.gen()
    primitive = [
        root
        for root, _multiplicity in (variable**degree - polynomials.one()).roots()
        if int(root.multiplicative_order()) == degree
    ]
    assert primitive, (
        f"{scalars} contains no primitive {degree}-th root of unity, so the deck "
        f"group of a degree-{degree} cyclic cover over it is the group scheme "
        f"mu_{degree}, not the constant cyclic group C_{degree}; that case is not implemented"
    )
    return _owned_engine_element(scalars, primitive[0])


class CyclicCovers(OwnedCategory):
    r"""Degree-``n`` cyclic covers of ``Spec(A)``, with their deck action.

    An object is the affine ``A``-scheme ``Spec(A[z]/(z^n - f))`` equipped with
    the deck action of ``C_n``; its structure morphism to the terminal affine
    ``A``-scheme is the finite cover morphism, so a cover is an object of
    ``Sch/Spec(A)`` with no further construction.  The category is a
    subcategory of the affine ``C_n``-schemes over ``A``, which is where the
    common fixed locus and the quotient of an action are already owned; the
    deck fixed locus is the ramification subscheme ``V(z)``, because the
    generator's fixed ideal is generated by ``(zeta - 1) z`` and ``zeta - 1``
    is a unit.
    """

    @staticmethod
    def __classcall__(cls, base_algebra, degree):
        return Category.__classcall__(cls, _own_ring(base_algebra), int(degree))

    def __init__(self, base_algebra, degree) -> None:
        assert degree >= 1, (
            f"a cyclic cover z^n = f of Spec({base_algebra}) needs degree n >= 1, got n = {degree}"
        )
        self._base_algebra = base_algebra
        self._degree = degree
        OwnedCategory.__init__(self)

    def base_algebra(self):
        r"""Return ``A``, the coordinate algebra of the base."""
        return self._base_algebra

    def base_scheme(self):
        r"""Return ``X = Spec(A)`` as the terminal affine ``A``-scheme."""
        algebra = self.base_algebra()
        return (algebra).affine_spectrum(base_ring=algebra)

    def cover_degree(self):
        r"""Return ``n``, the degree of the covers in this category."""
        return self._degree

    @cached_method
    def deck_group(self):
        r"""Return the canonical deck group scheme ``mu_n``."""
        return AffineGroupSchemes(self.base_algebra()).roots_of_unity(
            self.cover_degree()
        )

    @cached_method
    def deck_group_scheme(self):
        r"""Return the canonical deck group scheme ``mu_n``."""
        return self.deck_group()

    @cached_method
    def constant_deck_group(self):
        r"""Return the abstract cyclic group ``C_n`` for a chosen constant realization."""
        self.deck_root_of_unity()
        return OwnedGroups().C(self.cover_degree())

    @cached_method
    def deck_root_of_unity(self):
        r"""Return the primitive ``n``-th root of unity the deck generator scales by."""
        return _primitive_root_of_unity(
            self.base_algebra().base_ring(),
            self.cover_degree(),
        )

    def super_categories(self):
        return [Schemes(self.base_algebra()).Affine()]

    def _repr_object_names(self):
        return (
            f"degree-{self.cover_degree()} cyclic covers of {self.base_scheme()}"
        )

    def an_object(self):
        r"""The trivial cover ``z^n = 1``, the ``mu_n``-torsor over ``X``."""
        return self(self.base_algebra().one())

    def _call_(self, branch_section):
        r"""Return the cyclic cover branched along ``branch_section``."""
        return self._cover_branched_along(self.base_algebra()(branch_section))

    @cached_method
    def _cover_branched_along(self, section):
        r"""``Spec(A[z]/(z^n - f))`` over ``Spec A``, one object of this category for each ``f``.

        The object is constructed through ``Schemes(A).Affine()`` with this
        placement; its level data are the branch section ``f`` and the degree
        ``n``, which with ``A`` determine the cover algebra.
        """
        algebra = self.base_algebra()
        degree = self.cover_degree()
        return _affine_scheme(
            algebra.cyclic_cover_presentation(section, degree),
            algebra,
            (self,),
            branch_section=section,
            cover_degree=degree,
        )

    class ParentMethods:
        def __init__(self, branch_section, cover_degree, **rest) -> None:
            self._branch_section = branch_section
            self._cover_degree = cover_degree
            super().__init__(**rest)

        def cover_degree(self):
            r"""Return ``n``: the cover is finite locally free of this rank."""
            return self._cover_degree

        def branch_section(self):
            r"""Return ``f``, the section of ``L^n = O_X`` the cover is branched along."""
            return self._branch_section

        def deck_root_of_unity(self):
            r"""Return a primitive root identifying ``mu_n`` with the constant ``C_n`` here."""
            return CyclicCovers(
                self.scheme_base_ring(),
                self.cover_degree(),
            ).deck_root_of_unity()

        def deck_group_scheme(self):
            r"""Return the canonical deck group scheme ``mu_n``."""
            return CyclicCovers(
                self.scheme_base_ring(),
                self.cover_degree(),
            ).deck_group_scheme()

        @cached_method
        def deck_group_scheme_action(self):
            r"""Return the canonical action ``mu_n x X -> X``, the coaction ``z |-> u z``."""
            return _mu_n_action_on_affine_cover(self, self.deck_group_scheme())

        def constant_deck_action(self):
            r"""Return the constant ``C_n`` action selected by a primitive root of unity.

            This is defined precisely when ``deck_root_of_unity()`` succeeds;
            the underlying ``mu_n`` action exists independently of that choice.
            """
            group = CyclicCovers(
                self.scheme_base_ring(),
                self.cover_degree(),
            ).constant_deck_group()
            return AffineGSchemes(group, self.scheme_base_ring())(
                self,
                self.constant_deck_transformation,
            )

        def constant_deck_transformation(self, group_element):
            r"""Return the selected constant deck automorphism of this cover."""
            root_of_unity = self.deck_root_of_unity()
            group = CyclicCovers(
                self.scheme_base_ring(),
                self.cover_degree(),
            ).constant_deck_group()
            generator = group.group_generators()[0]
            degree = self.cover_degree()
            exponents = {}
            element = group.one()
            for exponent in range(degree):
                exponents[element] = exponent
                element = element * generator
            cover_algebra = self.coordinate_algebra()
            scaling = cover_algebra(root_of_unity ** exponents[group_element])
            return _affine_morphism_from_pullback(
                self,
                self,
                cover_algebra.Mor(cover_algebra)(
                    {CYCLIC_COVER_VARIABLE: scaling * self.cover_variable()}
                ),
            )

        def cover_variable(self):
            r"""Return ``z``, whose ``n``-th power is the branch section."""
            return self.coordinate_algebra().algebra_generator(CYCLIC_COVER_VARIABLE)

        @cached_method
        def branch_subscheme(self):
            r"""Return the branch subscheme ``V(f)`` of the base.

            The cover is étale over the complement of ``V(f)`` and the deck
            action is free there; the ramification subscheme upstairs is the
            deck fixed locus ``V(z)``, which maps isomorphically onto ``V(f)``
            when ``n`` is invertible.
            """
            return self.base_scheme().closed_subscheme(self.branch_section())

        def _assert_separable_degree(self):
            characteristic = int(self.scheme_base_ring().characteristic())
            assert characteristic == 0 or self.cover_degree() % characteristic != 0, (
                f"the characteristic {characteristic} divides the degree {self.cover_degree()}: the "
                f"ramification of {self} is compared with the branch locus only when the degree is "
                f"invertible in {self.scheme_base_ring()}"
            )

        @cached_method
        def ramification_subscheme(self):
            r"""Return the Fitting ramification scheme ``V(n z^(n-1))`` upstairs.

            The cover algebra is ``B=A[z]/(z^n-f)``.  Hence
            ``Omega_{B/A}`` is generated by ``dz`` with relation
            ``n z^(n-1) dz=0``.  In relative dimension zero its nonsmooth
            scheme is therefore ``V(Fitt_0 Omega_{B/A})``.  When ``n`` is a
            unit this has support ``V(z)`` and retains the expected
            ``(n-1)``-fold different for ``n>2``.
            """
            return self.differential_rank_drop_subscheme(0)

        @cached_method
        def ramification_support_subscheme(self):
            r"""Return the reduced-support model ``V(z)`` of the ramification locus."""
            self._assert_separable_degree()
            return self.closed_subscheme(self.cover_variable())

        @cached_method
        def ramification_to_branch_morphism(self):
            r"""Return the map from the ramification support to ``V(f)`` downstairs."""
            ramification = self.ramification_support_subscheme()
            branch = self.branch_subscheme()
            into_base = self.structure_morphism() * ramification.inclusion()
            return branch.corestriction(into_base)

        def is_etale_cover(self) -> bool:
            r"""Return whether the supported finite cyclic cover is everywhere étale."""
            ramification = self.ramification_subscheme()
            ideal = ramification.defining_ideal_owned()
            return ideal.contains_ambient_element(self.coordinate_algebra().one())

        def invariant_algebra(self):
            r"""Return ``A``: the deck invariants are the degree-zero summand.

            The ``mu_n``-coaction gives ``A z^i`` weight ``i`` modulo ``n``;
            its invariants are therefore the degree-zero summand ``A``.  No
            primitive root of unity is required, and no invariant-ring
            computation is involved.
            """
            return self.scheme_base_ring()

        def invariant_algebra_inclusion(self):
            r"""Return ``A -> A[z]/(z^n - f)``, the algebra structure morphism."""
            return self.coordinate_algebra().algebra_structure_morphism()

        def affine_quotient(self):
            r"""Return ``X``: a cyclic cover is the quotient map onto its base."""
            return self.base_scheme()

        def quotient_morphism(self):
            r"""Return the cover morphism, which is the deck quotient map."""
            return self.structure_morphism()


__all__ = [
    "CyclicCoverBaseChangeComparison",
    "CyclicCovers",
    "RelativeCyclicCoverLift",
]
