r"""Relative affine families and their fibres over a local base.

An affine family ``X -> Spec T`` presented by equations over ``T`` is the
affine ``T``-scheme ``Spec T[x_1,...,x_n]/(f_1,...,f_r)``: an object of
``Sch/T`` is a scheme together with its structure morphism to ``Spec T``, and
that structure morphism is the family.  Fibres are fibre products along
morphisms into ``Spec T``, flatness and the relative nonsmooth locus are the
affine scheme's own operations, and the slice object is
``Schemes(T).as_slice_object(X)``.  Nothing here is a second object beside
the scheme.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.arrow_categories import SliceCategory
from sage_extensions.categories.rings.ring_foundation import OwnedFields
from sage_extensions.categories.schemes.schemes import Schemes


class _SchemeSlice(SliceCategory):
    r"""The slice ``Sch_R/Y``: families ``f: X -> Y`` of ``R``-schemes over ``Y``, with their fibres.

    This is the implementation of ``Schemes(R).SliceOver(Y)`` that the
    ``SliceCategory`` cache selects, not a second category.  An object is a
    scheme ``X`` with its chosen morphism ``f: X -> Y``; a one-parameter
    family is an object of the slice over a curve ``C``.  The fibre over a
    point is the fibre product with the point (Hartshorne, *Algebraic
    Geometry*, II.3, the fibre ``X_y = X x_Y Spec k(y)``).
    """

    @staticmethod
    def __classcall__(cls, base_category, base_object):
        return SliceCategory(base_category, base_object)

    @classmethod
    def _slice_category_class_for(cls, base_category, base_object):
        return cls

    class ParentMethods:
        @cached_method
        def fibre(self, point):
            r"""The fibre ``X_y = X x_Y Spec K`` of the family ``f: X -> Y`` over the point ``Spec K -> Y``.

            Domain: a morphism ``y: Spec K -> Y`` from the spectrum of a field
            ``K``.  The scheme-theoretic fibre over a point ``y`` of ``Y`` is
            the case ``K = k(y)`` with ``y`` the canonical morphism; a
            ``k``-rational point is ``Y.point_morphism(coordinates)``.
            Codomain: the fibre product ``X x_Y Spec K``, an object of
            ``Schemes(R)`` with its two projections.
            """
            family = self.arrow()
            base = family.codomain()
            assert point.codomain() is base, (
                f"the fibre of {family} is taken over a point of its base {base}, but {point} ends at "
                f"{point.codomain()}"
            )
            residue = point.domain()
            assert residue in Schemes(residue.scheme_base_ring()).Affine(), (
                f"a point of {base} is a morphism from the spectrum of a field, but {point} starts at {residue}"
            )
            assert residue.coordinate_algebra() in OwnedFields(), (
                f"a point of {base} is a morphism from the spectrum of a field, but {point} starts at "
                f"Spec {residue.coordinate_algebra()}"
            )
            return self.scheme_category().fiber_product(family, point)


def _projective_hypersurface_family(plane, parameter_space, equation, *, name):
    r"""The family ``f: X -> C`` of hypersurfaces ``X = V(F) <= P^n x C``, with ``f`` the second projection.

    ``P^n`` and ``C`` are ``k``-schemes, ``C`` affine with coordinate algebra
    ``T``, and ``F`` is an element of ``T[x_0,...,x_n]`` homogeneous of degree
    ``d`` in the ``x_i``.  The product ``P^n x C`` is glued from the charts
    ``D_+(x_j) x C``.  On such a chart ``V(F)`` is cut out by the
    dehomogenization ``F(x_0/x_j,...,x_n/x_j)``, read through the two
    projections of the chart.  Two dehomogenizations differ on an overlap by
    the unit ``(x_j/x_i)^d``, so the local closed subschemes glue to ``X``.
    The fibre of ``f`` over a ``k``-point ``t = a`` of ``C`` is the hypersurface
    ``V(F(x, a)) <= P^n_k``.
    """
    from sage_extensions.categories.schemes.schemes import (
        _evaluate_owned_homogeneous_polynomial_on_coordinates,
    )

    product = Schemes(plane.scheme_base_ring()).product((plane, parameter_space))
    datum = product.gluing_datum()
    presentation_ring = equation.parent()

    def local_hypersurface(label):
        chart = datum.chart(label)
        plane_projection = chart.projection(0)
        index = next(
            index
            for index in range(int(plane.relative_dimension()) + 1)
            if plane.standard_affine_chart(index) is plane_projection.codomain()
        )
        coordinates = tuple(
            plane_projection.coordinate_algebra_morphism()(coordinate)
            for coordinate in plane.standard_affine_chart_embedding(index).homogeneous_coordinates()
        )
        return chart.closed_subscheme(
            _evaluate_owned_homogeneous_polynomial_on_coordinates(
                equation,
                presentation_ring,
                coordinates,
                coefficient_map=chart.projection(1).coordinate_algebra_morphism(),
            )
        )

    total = product.chartwise_closed_subscheme(
        {label: local_hypersurface(label) for label in datum.chart_indices()},
        name=name,
    )
    return product.projection(1) * total.inclusion()


def _relative_affine_family(parameter_algebra, relative_variables, equations):
    r"""``Spec T[x_1,...,x_n]/(f_1,...,f_r)`` as an object of ``Schemes(T).Affine()``.

    ``equations`` is a function of the presentation ring ``T[x_1,...,x_n]``
    returning the family ``f_1, ..., f_r`` of its elements, since the
    presentation ring does not exist before this construction names it.
    """
    presentation_ring = parameter_algebra.polynomial_ring(relative_variables)
    total_algebra = presentation_ring.quotient_by_relations(
        tuple(presentation_ring(equation) for equation in equations(presentation_ring))
    )
    return total_algebra.affine_spectrum(base_ring=parameter_algebra)


def _special_fiber_comparison(family):
    r"""The isomorphism ``(X_{R^})_k -> X_k`` of the two special fibres over a local base.

    ``R`` is the base ring of ``X``, ``m`` its maximal ideal, ``R^`` the
    ``m``-adic completion and ``k = R/m = R^/m^``.  Both special fibres are
    fibre products over ``Spec k``; the comparison is built from their
    pullback cones, and its inverse from the cone of ``X_k`` into
    ``X_{R^}``, so the two maps are the universal factorizations and are
    mutually inverse by uniqueness.
    """
    base = family.scheme_base_ring()
    completion = base.adic_completion(base.maximal_ideal())
    category = family.scheme_category()
    direct = category.base_change_functor(base.residue_map())(family)
    completed_total = category.base_change_functor(completion.completion_map())(family)
    completed_residue = completed_total.scheme_category().base_change_functor(
        completion.residue_map()
    )
    completed_special = completed_residue(completed_total)

    forward = direct.from_pullback_cone(
        completed_total.left_projection() * completed_special.left_projection(),
        completed_special.right_projection(),
    )
    direct_to_completed_total = completed_total.from_pullback_cone(
        direct.left_projection(),
        completed_residue.base_morphism() * direct.right_projection(),
    )
    inverse = completed_special.from_pullback_cone(
        direct_to_completed_total,
        direct.right_projection(),
    )
    return Schemes(direct.scheme_base_ring()).Core().Mor(completed_special, direct)(
        forward, inverse
    )


__all__ = []
