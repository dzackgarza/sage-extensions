r"""Base change of schemes and the slice adjunction.

For a ring morphism ``g: R -> R'`` the base-change functor is

``- x_{Spec R} Spec R' : Sch/R -> Sch/R'``.

On an affine scheme ``Spec A`` it is ``Spec(A tensor_R R')``, computed by
scalar extension of the coordinate algebra, and the result is constructed as
the fibre product of the cospan ``Spec A -> Spec R <- Spec R'`` with its two
projections and the universal factorization.  A scheme presented by a finite
affine gluing is base-changed by this same affine construction on every chart;
the overlap maps are induced by the pullback universal properties and the
changed charts are glued with the resulting fibre-product projections.

The projections are morphisms of locally ringed spaces. Their pullbacks
retain the given scalar map; constructing them changes neither the original
scheme's scalar structure nor that of its base change.

For a morphism of schemes ``g: S' -> S`` over one ring, pullback along ``g``
is the functor ``g^*: Sch/S -> Sch/S'``, ``(X -> S) |-> (X x_S S' -> S')``,
and composition with ``g`` is ``Sigma_g: Sch/S' -> Sch/S``.  These form the
adjunction ``Sigma_g -| g^*`` whose unit at ``X -> S'`` is the cone map
``X -> X x_S S'`` and whose counit at ``Y -> S`` is the projection
``Y x_S S' -> Y`` (Stacks, Tag 01JO for the fibre product; the adjunction is
the universal property of the fibre product read in the two slices).
"""

from sage.misc.cachefunc import cached_function, cached_method

from sage_extensions.categories.algebras.finitely_presented_algebras import (
    AlgebrasWithChosenFinitePresentation,
)
from sage_extensions.categories.algebras.free_algebras import (
    SymmetricAlgebras,
)
from sage_extensions.categories.functors.algebra_scalar_change import (
    _base_change_presented_element,
    _engine_ring_map,
)
from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    _engine_element,
    _engine_ring,
    _owned_ring,
    _ring_morphism_with_engine,
)
from sage_extensions.categories.schemes.schemes import (
    AffineSpaces,
    ClosedSubschemes,
    FiberProductSchemes,
    ProductProjectiveSpaces,
    ProjectiveSpaces,
    SchemeFiberProductConstruction,
    Schemes,
    _affine_morphism_from_pullback,
    _affine_scheme,
    _affine_space,
    _affine_space_coordinates,
    _normalized_space_names,
    _projective_projection_rule,
    _projective_closed_subscheme,
    _engine_projective_subscheme,
    _engine_projective_ambient,
    _engine_polynomial_algebra,
    _engine_scheme,
    _projective_base_change_factorization,
    _projective_coordinate_morphism,
    _ProjectiveCoordinateMorphism,
    _scheme_product,
    _structure_morphism_rule,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
    indexed_family,
)
from sage_extensions.categories.schemes.ringed_spaces import LocallyRingedSpaces


def _base_changed_algebra(algebra, ring_map):
    r"""``A tensor_R R'`` for the coordinate algebras the scheme layer builds.

    Presented algebras carry their own scalar extension.  A polynomial algebra
    is ``Sym`` of a free module, and ``Sym`` commutes with base change, so
    ``R[S] tensor_R R' = R'[S]``; the ring itself extends to ``R'``.
    """
    source = _owned_ring(ring_map.domain())
    target = _owned_ring(ring_map.codomain())
    match algebra:
        case _ if algebra is source:
            return target
        case _ if algebra in AlgebrasWithChosenFinitePresentation(source):
            return algebra.base_change(ring_map)
        case _ if algebra in SymmetricAlgebras(source) and algebra.is_framed_algebra():
            return target.free_module(algebra.algebra_generating_set()).symmetric_algebra()
        case _:
            assert False, (
                f"base change of {algebra} along {ring_map} is not implemented: {algebra} must "
                f"be the scalar ring {source}, a {source}-algebra given by finitely many generators "
                f"and relations, or a polynomial algebra over {source}; it is in {algebra.category()}"
            )


def _base_changed_element(algebra, element, changed_algebra, ring_map):
    r"""The image of ``a`` under the canonical ``A -> A tensor_R R'``."""
    source = _owned_ring(ring_map.domain())
    match algebra:
        case _ if algebra is source:
            return ring_map(element)
        case _ if algebra in AlgebrasWithChosenFinitePresentation(source):
            return _base_change_presented_element(algebra, element, changed_algebra, ring_map)
        case _:
            engine_image = _engine_element(algebra, element).map_coefficients(
                _engine_ring_map(ring_map),
                new_base_ring=_engine_ring(_owned_ring(ring_map.codomain())),
            )
            return _owned_engine_element(changed_algebra, _engine_ring(changed_algebra)(engine_image))


def _base_change_unit(algebra, changed_algebra, ring_map):
    r"""The ring morphism ``A -> A tensor_R R'`` with its engine realization."""
    source = _owned_ring(ring_map.domain())
    changed_engine = _engine_ring(changed_algebra)
    match algebra:
        case _ if algebra is source:
            engine = _engine_ring_map(ring_map)
        case _:
            engine = _engine_ring(algebra).hom(
                [
                    changed_engine(_engine_element(changed_algebra, changed_algebra.algebra_generator(label)))
                    for label in algebra.algebra_generating_set()
                ],
                changed_engine,
                base_map=_engine_ring_map(ring_map),
            )
    return _ring_morphism_with_engine(
        algebra,
        changed_algebra,
        lambda element: _base_changed_element(algebra, element, changed_algebra, ring_map),
        engine,
    )


class _SchemeBaseChangeFunctor(Functor):
    r"""``- x_{Spec R} Spec R' : Sch/R -> Sch/R'`` along ``g: R -> R'``."""

    def __init__(self, ring_map) -> None:
        self._ring_map = ring_map
        self._source_ring = _owned_ring(ring_map.domain())
        self._target_ring = _owned_ring(ring_map.codomain())
        super().__init__(Schemes(self._source_ring), Schemes(self._target_ring))

    def ring_map(self):
        return self._ring_map

    @cached_method
    def base_morphism(self):
        r"""``Spec g: Spec R' -> Spec R``, the affine morphism induced by the ring map."""
        return LocallyRingedSpaces().Mor(
            Schemes(self._target_ring).base_scheme(),
            Schemes(self._source_ring).base_scheme(),
        )(self.ring_map())

    def projection(self, scheme):
        r"""The projection ``X x_{Spec R} Spec R' -> X``."""
        return self(scheme).left_projection()

    def _cospan(self, scheme):
        return (scheme.structure_morphism(), self.base_morphism())

    def _apply_object(self, scheme):
        source, target = self._source_ring, self._target_ring
        match scheme:
            case _ if scheme._is_glued_from_affine_atlas():
                changed = self._glued_object(scheme)
            case _ if scheme in ProjectiveSpaces(source):
                changed = scheme.scheme_category().fiber_product(scheme.structure_morphism(), self.base_morphism())
            case _ if scheme in ProductProjectiveSpaces(source):
                changed = self._product_projective_base_change(scheme)
            case _ if scheme in Schemes(source).Affine():
                changed = self._affine_object(scheme)
            case _ if scheme in Schemes(source).Projective() and scheme in ClosedSubschemes(source):
                changed = self._projective_closed_base_change(scheme)
            case _:
                assert False, (
                    f"base change of {scheme} along {source} -> {target} is not implemented: it is "
                    "implemented for affine schemes, projective spaces, finite products of projective "
                    "spaces, closed subschemes of projective space, and schemes glued from a finite "
                    f"affine cover; {scheme} is in {scheme.category()}"
                )
        return changed

    def _glued_overlap(self, datum, changed_charts, source_index, target_index):
        r"""Base change the represented distinguished overlap inside one changed chart."""
        source_overlap = datum.overlap(source_index, target_index)
        changed_chart = changed_charts[source_index]
        projection_pullback = changed_chart.left_projection().coordinate_algebra_morphism()
        return changed_chart.distinguished_open(
            projection_pullback(source_overlap.distinguished_open_element())
        )

    def _glued_transition(
        self,
        datum,
        changed_charts,
        changed_overlaps,
        source_index,
        target_index,
    ):
        r"""Base change one affine-atlas transition by the pullback universal property."""
        source_open = changed_overlaps[source_index, target_index]
        target_open = changed_overlaps[target_index, source_index]
        old_source_open = datum.overlap(source_index, target_index)
        old_target_open = datum.overlap(target_index, source_index)
        old_transition = datum.transition_between(source_index, target_index)

        def direction(
            changed_source_open,
            changed_target_open,
            changed_source_chart,
            changed_target_chart,
            old_source_overlap,
            old_target_overlap,
            old_map,
        ):
            to_old_source_chart = (
                changed_source_chart.left_projection()
                * changed_source_open.inclusion()
            )
            to_old_source_overlap = old_source_overlap.corestriction(
                to_old_source_chart
            )
            to_old_target_chart = (
                old_target_overlap.inclusion()
                * old_map
                * to_old_source_overlap
            )
            to_changed_target_chart = changed_target_chart.from_pullback_cone(
                to_old_target_chart,
                changed_source_open.structure_morphism(),
            )
            return changed_target_open.corestriction(to_changed_target_chart)

        forward = direction(
            source_open,
            target_open,
            changed_charts[source_index],
            changed_charts[target_index],
            old_source_open,
            old_target_open,
            old_transition.forward(),
        )
        inverse = direction(
            target_open,
            source_open,
            changed_charts[target_index],
            changed_charts[source_index],
            old_target_open,
            old_source_open,
            old_transition.inverse().forward(),
        )
        return Schemes(self._target_ring).Core().Mor(
            source_open,
            target_open,
        )(forward, inverse)

    def _glued_factorization(self, changed, to_source, to_base):
        r"""Factor a represented cone through the scalar pullback of a glued scheme."""
        from sage_extensions.categories.schemes.gluing import (
            _GluedSchemeChartEmbedding,
            _GluedSchemeChartMap,
        )

        source = to_source.domain()
        source_datum = changed.fiber_product_cospan()[0].domain().gluing_datum()
        changed_datum = changed.gluing_datum()

        match source._is_glued_from_affine_atlas():
            case True:
                domain_datum = source.gluing_datum()
                return LocallyRingedSpaces().Mor(source, changed)(
                    finite_indexed_family(
                        domain_datum.chart_index_set(),
                        lambda index: self._glued_factorization(
                            changed,
                            to_source * domain_datum.chart_embedding(index),
                            to_base * domain_datum.chart_embedding(index),
                        ),
                        name="Local factorizations into a glued scalar base change",
                    )
                )
            case False:
                pass

        match to_source:
            case _GluedSchemeChartMap() if to_source.gluing_datum() is source_datum:
                chart_index = to_source.chart_index()
                chart_map = to_source.chart_map()
            case _GluedSchemeChartEmbedding() if to_source.gluing_datum() is source_datum:
                chart_index = to_source.chart_index()
                chart_map = to_source.domain().categorical_identity_morphism()
            case _:
                raise AssertionError(
                    f"cannot induce a map into the base change {changed}: the map {to_source} into "
                    "the original scheme does not factor through one affine chart of its gluing"
                )
        changed_chart = changed_datum.chart(chart_index)
        into_changed_chart = changed_chart.from_pullback_cone(
            chart_map,
            to_base,
        )
        return changed_datum.chart_embedding(chart_index) * into_changed_chart

    def _glued_object(self, scheme):
        r"""Scalar base change of a scheme presented by one finite affine gluing datum."""
        datum = scheme.gluing_datum()
        indices = datum.chart_index_set()
        changed_charts = finite_indexed_family(
            indices,
            lambda index: self(datum.chart(index)),
            name="Affine charts of a scalar base-changed gluing",
        )
        changed_overlaps = {
            (source_index, target_index): self._glued_overlap(
                datum,
                changed_charts,
                source_index,
                target_index,
            )
            for source_index in indices
            for target_index in indices
            if source_index != target_index
        }
        transitions = {
            (source_index, target_index): self._glued_transition(
                datum,
                changed_charts,
                changed_overlaps,
                source_index,
                target_index,
            )
            for source_index, target_index in datum.transition_index_set()
        }
        left_projection_data = finite_indexed_family(
            indices,
            lambda index: (
                datum.chart_embedding(index) * changed_charts[index].left_projection()
            ),
            name="Local projections from a scalar base-changed gluing",
        )
        right_projection_data = finite_indexed_family(
            indices,
            lambda index: changed_charts[index].right_projection(),
            name="Local scalar projections from a scalar base-changed gluing",
        )

        def factor(to_source, to_base):
            return self._glued_factorization(changed, to_source, to_base)

        changed = Schemes(self._target_ring).glue_affine_atlas(
            changed_charts,
            transitions,
            placements=(FiberProductSchemes(self._target_ring),),
            fiber_product_construction=SchemeFiberProductConstruction(
                self._cospan(scheme),
                (left_projection_data, right_projection_data),
                scheme_factorization=factor,
            ),
        )
        return changed

    def _affine_object(self, scheme, *, cospan=None, scheme_on_left=True):
        r"""Construct an affine scalar pullback with the exact supplied cospan."""
        target = self._target_ring
        if scheme in AffineSpaces(self._source_ring):
            coordinates = _affine_space_coordinates(
                target, int(scheme.relative_dimension()),
                _normalized_space_names(tuple(str(label) for label in scheme.coordinate_algebra().algebra_generating_set())),
            )
            return _affine_space(
                target, coordinates, (FiberProductSchemes(target),),
                fiber_product_construction=self._affine_construction(
                    scheme, coordinates[1], cospan=cospan, scheme_on_left=scheme_on_left,
                ),
            )
        changed_algebra = _base_changed_algebra(scheme.coordinate_algebra(), self.ring_map())
        return _affine_scheme(
            changed_algebra, target, (FiberProductSchemes(target),),
            fiber_product_construction=self._affine_construction(
                scheme, changed_algebra, cospan=cospan, scheme_on_left=scheme_on_left,
            ),
        )

    def _affine_construction(self, scheme, changed_algebra, *, cospan=None, scheme_on_left=True):
        r"""The pullback construction of ``Spec(A tensor_R R')`` from the unit ``A -> A tensor_R R'``."""
        algebra = scheme.coordinate_algebra()
        source = self._source_ring

        def factor(to_scheme, to_base):
            r"""``A tensor_R R' -> C`` from ``A -> C`` and ``R' -> C`` agreeing on ``R``."""
            assert to_scheme.codomain() is to_base.codomain(), (
                f"the maps {to_scheme} and {to_base} do not form a cocone on the tensor product: "
                f"their codomains {to_scheme.codomain()} and {to_base.codomain()} differ"
            )
            match algebra:
                case _ if algebra is source:
                    return to_base
                case _:
                    target = to_scheme.codomain()
                    engine_target = _engine_ring(target)
                    native = _engine_ring(changed_algebra).hom(
                        [_engine_element(target, to_scheme(algebra.algebra_generator(label)))
                         for label in algebra.algebra_generating_set()],
                        engine_target, base_map=_engine_ring_map(to_base),
                    )
                    return _ring_morphism_with_engine(
                        changed_algebra,
                        target,
                        lambda element: _owned_engine_element(
                            target, native(_engine_element(changed_algebra, element))
                        ),
                        native,
                    )

        data = (_base_change_unit(algebra, changed_algebra, self.ring_map()), _structure_morphism_rule)
        return SchemeFiberProductConstruction(
            self._cospan(scheme) if cospan is None else cospan,
            data if scheme_on_left else tuple(reversed(data)),
            cocone_factorization=factor if scheme_on_left else lambda left, right: factor(right, left),
        )

    def _product_projective_base_change(self, scheme):
        r"""``(prod P^{n_i})_{R'}``, the product of the base-changed factors, as a fibre product."""
        factors = scheme.factors()
        factor_indices = factors.index_set()
        changed_factors = indexed_family(
            factor_indices,
            lambda label: self(factors[label]),
            name="Base-changed projective factors",
        )
        width = sum(int(factor.relative_dimension()) + 1 for factor in factors)

        def factor(to_scheme, to_base):
            changed = self(scheme)
            return changed.from_product_cone(
                indexed_family(
                    factor_indices,
                    lambda label: self(factors[label]).from_pullback_cone(scheme.projection(label) * to_scheme, to_base),
                    name="Factorwise maps into a multiprojective base change",
                )
            )

        return _scheme_product(
            changed_factors,
            placements=(FiberProductSchemes(self._target_ring),),
            fiber_product_construction=SchemeFiberProductConstruction(
                self._cospan(scheme),
                (_projective_projection_rule(0, width, self.ring_map()), _structure_morphism_rule),
                scheme_factorization=factor,
            ),
        )

    def _projective_closed_base_change(self, scheme):
        r"""Pull back the defining equations, without assuming regularity survives.

        Polynomial coefficient transport is the algebra engine's map on
        coefficients.  The projective closed-subscheme entry owns allocation;
        the complete-intersection owner decides any extra regular placement.
        """
        from sage_extensions.categories.schemes.complete_intersections import (
            ProjectiveCompleteIntersections, _complete_intersection_base_supported,
            _is_regular_sequence,
        )

        ambient = scheme.inclusion().codomain()
        changed_ambient = self(ambient)
        source_engine, _ = _engine_projective_ambient(_engine_scheme(ambient))
        source_ring = _engine_polynomial_algebra(source_engine.coordinate_ring(), self._source_ring)
        target_engine, _ = _engine_projective_ambient(_engine_scheme(changed_ambient))
        target_ring = _engine_polynomial_algebra(target_engine.coordinate_ring(), self._target_ring)
        equations = tuple(
            _base_changed_element(source_ring, equation, target_ring, self.ring_map())
            for equation in scheme.homogeneous_defining_equations(source_ring)
        )
        engine = _engine_projective_subscheme(_engine_scheme(changed_ambient), equations)
        placements = [FiberProductSchemes(self._target_ring)]
        if (scheme in ProjectiveCompleteIntersections(self._source_ring)
                and _complete_intersection_base_supported(self._target_ring)
                and _is_regular_sequence(engine)):
            placements.append(ProjectiveCompleteIntersections(self._target_ring))
            match (
                self._target_ring in OwnedFields(),
                int(changed_ambient.relative_dimension()) - len(equations),
            ):
                case (True, 2) if bool(engine.defining_ideal().is_prime()):
                    from sage_extensions.categories.schemes.varieties import Surfaces

                    placements.append(Surfaces(self._target_ring).Projective())
                case _:
                    pass

        def factor(to_source, to_base):
            # The source equations vanish after to_source; transporting their
            # coefficients by the commuting scalar leg makes the changed
            # equations vanish too.  The same coordinate factorization is
            # therefore into the changed closed scheme, chartwise for a
            # glued source, not a native map copied from the ambient space.
            return _projective_base_change_factorization(changed, to_source, to_base)

        changed = _projective_closed_subscheme(
            changed_ambient, equations, placements=tuple(placements), _engine=engine,
            fiber_product_construction=SchemeFiberProductConstruction(
                self._cospan(scheme),
                (_projective_projection_rule(0, len(target_ring.algebra_generating_set()), self.ring_map()),
                 _structure_morphism_rule),
                scheme_factorization=factor,
            ),
        )
        return changed

    def _apply_morphism(self, morphism):
        r"""The unique map of pullbacks given by the morphism and the scalar projection."""
        source = self(morphism.domain())
        target = self(morphism.codomain())
        induced = target.from_pullback_cone(
            morphism * self.projection(morphism.domain()), source.right_projection(),
        )
        return self.codomain().Mor(source, target)(induced)

    def _repr_(self):
        return f"Base change of schemes along {self.ring_map()}"


@cached_function
def _scheme_base_change_functor(ring_map) -> _SchemeBaseChangeFunctor:
    return _SchemeBaseChangeFunctor(ring_map)


class _SlicePullbackFunctor(Functor):
    r"""``g^*: Sch/S -> Sch/S'``, ``(X -> S) |-> (X x_S S' -> S')``."""

    def __init__(self, base_morphism) -> None:
        self._base_morphism = base_morphism
        schemes = Schemes(base_morphism.codomain().scheme_base_ring())
        super().__init__(
            schemes.SliceOver(base_morphism.codomain()),
            schemes.SliceOver(base_morphism.domain()),
        )

    def base_morphism(self):
        return self._base_morphism

    def _apply_object(self, family):
        base_morphism = self.base_morphism()
        pulled_back = base_morphism.codomain().scheme_category().fiber_product(family.arrow(), base_morphism)
        return self.codomain()(pulled_back.right_projection())

    def _apply_morphism(self, triangle):
        source = self(triangle.domain()).arrow().domain()
        target = self(triangle.codomain()).arrow().domain()
        induced = target.from_pullback_cone(
            triangle.left() * source.left_projection(),
            source.right_projection(),
        )
        return self.codomain().Mor(self(triangle.domain()), self(triangle.codomain()))(induced)

    def _repr_(self):
        return f"Pullback of families along {self.base_morphism()}"


class _SliceCompositionFunctor(Functor):
    r"""``Sigma_g: Sch/S' -> Sch/S``, ``(X -> S') |-> (X -> S' -> S)``."""

    def __init__(self, base_morphism) -> None:
        self._base_morphism = base_morphism
        schemes = Schemes(base_morphism.codomain().scheme_base_ring())
        super().__init__(
            schemes.SliceOver(base_morphism.domain()),
            schemes.SliceOver(base_morphism.codomain()),
        )

    def base_morphism(self):
        return self._base_morphism

    def _apply_object(self, family):
        return self.codomain()(self.base_morphism() * family.arrow())

    def _apply_morphism(self, triangle):
        return self.codomain().Mor(self(triangle.domain()), self(triangle.codomain()))(triangle.left())

    def _repr_(self):
        return f"Composition of families with {self.base_morphism()}"


class _SliceBaseChangeAdjunction(Adjunction):
    r"""``Sigma_g -| g^*`` for a base morphism ``g: S' -> S``."""

    def __init__(self, base_morphism) -> None:
        self._base_morphism = base_morphism
        super().__init__(_SliceCompositionFunctor(base_morphism), _SlicePullbackFunctor(base_morphism))

    def base_morphism(self):
        return self._base_morphism

    def _unit_component(self, family):
        r"""``X -> X x_S S'`` over ``S'``, the cone with legs ``id_X`` and ``X -> S'``."""
        composed = self.left_adjoint()(family)
        pulled_back = self.right_adjoint()(composed)
        scheme = family.arrow().domain()
        cone = pulled_back.arrow().domain().from_pullback_cone(scheme.categorical_identity_morphism(), family.arrow())
        return self.left_adjoint().domain().Mor(family, pulled_back)(cone)

    def _counit_component(self, family):
        r"""``Y x_S S' -> Y`` over ``S``, the projection to the family."""
        pulled_back = self.right_adjoint()(family)
        composed = self.left_adjoint()(pulled_back)
        projection = pulled_back.arrow().domain().left_projection()
        return self.right_adjoint().domain().Mor(composed, family)(projection)

    def _repr_(self):
        return f"Composition/pullback adjunction along {self.base_morphism()}"


@cached_function
def _slice_base_change_adjunction(base_morphism) -> _SliceBaseChangeAdjunction:
    return _SliceBaseChangeAdjunction(base_morphism)


__all__ = []
