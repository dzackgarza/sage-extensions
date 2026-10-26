"""Owned varieties, curves, and surfaces.

A variety over ``S`` is an integral separated scheme of finite type over
``S``; a curve and a surface are the varieties of relative dimension one and
two.  Constructors which establish those hypotheses place the result in the
corresponding full subcategory; membership never recomputes them afterwards.

Projectivity, properness, smoothness, the K3 condition and the del Pezzo
condition are properties, so they are axioms on these categories, and
``Surfaces(k).Projective()`` is the category Sage computes from the axiom
rather than a class of its own (``CAT-17``, ``CAT-27``).
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    _owned_integers,
)
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.validation import validator
from sage_extensions.categories.schemes.schemes import (
    AffineSpaces,
    ProjectiveSpaces,
    Schemes,
    _engine_projective_subscheme,
    _engine_scheme,
    _projective_closed_subscheme,
    _projective_equation_family,
)
from sage_extensions.owned_category_bases import CategoryWithAxiom


class Varieties(OwnedCategoryOverBaseRing):
    r"""Integral separated schemes of finite type over the stated base.

    The base is any ring, so a variety over ``QQbar`` or over ``CC`` is an
    object here as one over ``QQ`` is: over a field ``k`` it is an integral
    separated scheme of finite type over ``Spec k`` (Huybrechts, *Lectures on
    K3 Surfaces* [Huy16], Ch. 1, before Def. 1.1).
    """

    def an_object(self):
        r"""The affine line over the base ring."""
        from sage_extensions.categories.schemes.schemes import _integral_placement

        assert _integral_placement(self.base_ring()), (
            f"the affine line over {self.base_ring()} is a variety only when the base is an integral domain"
        )
        return AffineSpaces(self.base_ring())(1)

    def _repr_object_names(self):
        return f"varieties over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring()).Integral().Separated().FiniteType()]

    class Projective(CategoryWithAxiom):
        r"""Projective varieties over the stated base."""

        def an_object(self):
            r"""The projective line."""
            return ProjectiveSpaces(self.base_ring())(1)

        def polarized_varieties(self):
            r"""The full subcategory of ``int Pic`` on the pairs ``(X, L)`` with ``L`` ample.

            ``Pic : C^op -> Mod_ZZ`` is this category's ``picard_functor()``,
            inherited from the category of schemes it refines.
            """
            return self.picard_functor().category_of_elements().Ample()


class _DimensionSubcategoryOfVarieties(OwnedCategoryOverBaseRing):
    r"""The varieties over ``S`` of one relative dimension.

    Relative dimension is the invariant that separates a curve from a
    surface, so the two categories differ only in the number they compare
    against and share every other statement.
    """

    relative_dimension = None

    def super_categories(self):
        return [Varieties(self.base_ring())]


class Curves(_DimensionSubcategoryOfVarieties):
    r"""Varieties of relative dimension one over the stated base."""

    relative_dimension = 1

    def an_object(self):
        r"""The projective line, of relative dimension one."""
        from sage_extensions.categories.schemes.schemes import _integral_placement

        assert _integral_placement(self.base_ring()), (
            f"the projective line over {self.base_ring()} is a curve only when the base is integral"
        )
        return ProjectiveSpaces(self.base_ring())(1)

    def _repr_object_names(self):
        return f"curves over {self.base_ring()}"

    def from_equation(self, equation, ambient=None, placements=(), **level_data):
        r"""Return the integral curve over this base cut out by ``equation``.

        With an explicit ambient scheme this uses its closed-subscheme
        construction.  With no ambient, ``equation`` lies in a polynomial
        algebra over this category's base ring with chosen algebra generators;
        their labels determine the affine space in which the curve is cut out.
        A curve constructed with further data -- a chosen normalization --
        states those categories in ``placements``, with their level data.

        The closed subscheme is constructed once, as an object of this
        category.  Its two hypotheses are decided on the data that determine
        them: the ideal of the equation is prime, which makes ``V(f)``
        integral, and the relative dimension is one.  Separatedness and finite
        type come from the ambient.  A reducible or otherwise non-variety
        one-dimensional subscheme is rejected rather than being placed here
        merely because its dimension is one.
        """
        base = self.base_ring()
        match ambient:
            case None:
                source = equation.parent()
                assert source.is_framed_algebra(), (
                    f"cannot cut a curve over {base} out of {equation} without a given scheme to "
                    f"contain it: {equation} must lie in a polynomial ring over {base} with named "
                    f"variables, but it lies in {source}, which is in {source.category()}"
                )
                labels = tuple(source.algebra_generating_set())
                ambient = AffineSpaces(base)(
                    len(labels),
                    names=tuple(str(label) for label in labels),
                )
                target = ambient.coordinate_algebra()
                match source is target:
                    case True:
                        ambient_equation = equation
                    case False:
                        images = {label: target.algebra_generator(str(label)) for label in labels}
                        ambient_equation = source.Mor(target)(images)(equation)
            case _:
                assert ambient.scheme_base_ring() is base, (
                    f"a curve over {base} cannot be cut out of {ambient}: {ambient} lies over "
                    f"{ambient.scheme_base_ring()}, not over {base}"
                )
                ambient_equation = equation
        assert ambient in Schemes(base).Separated() and ambient in Schemes(base).FiniteType(), (
            f"a curve over {base} must be cut out of a separated scheme of finite type over "
            f"{base}, but {ambient} is not known to be both; it is in {ambient.category()}"
        )
        match ambient:
            case _ if ambient in Schemes(base).Affine():
                algebra = ambient.coordinate_algebra()
                ideal = algebra.ideal(ambient_equation)
                assert ideal.is_prime(), (
                    f"V({ambient_equation}) in {ambient} is not an integral curve: the ideal "
                    f"{ideal} is not prime"
                )
                quotient_data = algebra._quotient_by_algebra_elements((ambient_equation,))
                quotient, _ = quotient_data
                assert quotient.krull_dimension() - base.krull_dimension() == 1, (
                    f"V({ambient_equation}) in {ambient} is not a curve: its relative dimension over "
                    f"{base} is {quotient.krull_dimension() - base.krull_dimension()}, not 1"
                )
                return ambient.closed_subscheme(
                    ambient_equation, placements=(self, *placements),
                    _quotient_data=quotient_data, **level_data,
                )
            case _:
                assert ambient in Schemes(base).Projective(), (
                    f"cannot cut a curve out of {ambient} by the equation {ambient_equation}: the "
                    f"scheme must be affine or projective over {base}, but it is in {ambient.category()}"
                )
                equations = _projective_equation_family((ambient_equation,))
                engine = _engine_projective_subscheme(_engine_scheme(ambient), equations)
                assert engine.defining_ideal().is_prime(), (
                    f"V({ambient_equation}) in {ambient} is not an integral curve: its homogeneous "
                    "ideal is not prime"
                )
                assert engine.dimension_relative() == 1, (
                    f"V({ambient_equation}) in {ambient} is not a curve: its relative dimension over "
                    f"{base} is {engine.dimension_relative()}, not 1"
                )
                return _projective_closed_subscheme(
                    ambient, equations, placements=(self, self.Projective(), *placements),
                    _engine=engine, **level_data,
                )

    class ParentMethods:
        def __init__(self, normalization_curve=None, normalization_coordinates=None,
                     local_delta_contributions=None, **rest) -> None:
            self._normalization_curve = normalization_curve
            self._normalization_coordinates = normalization_coordinates
            self._local_delta_contributions = local_delta_contributions
            super().__init__(**rest)

        @cached_method
        def normalization_data(self):
            r"""Return this curve with its retained normalization and local-defect construction data."""
            self.normalization_curve()
            self.local_delta_contributions()
            return self

        def curve(self):
            r"""Compatibility spelling for a curve carrying chosen normalization data."""
            return self

        @cached_method
        def normalization_morphism(self):
            r"""Corestrict the chosen normalization coordinates to this curve."""
            assert self._normalization_coordinates is not None, (
                f"no normalization coordinate formula was given when {self} was constructed"
            )
            return self.corestriction(
                self.normalization_curve().projective_morphism_from_coordinates(
                    self.inclusion().codomain(), tuple(self._normalization_coordinates),
                )
            )

        def normalization_curve(self):
            assert self._normalization_curve is not None, (
                f"no normalization was given when {self} was constructed"
            )
            return self._normalization_curve

        def local_delta_contributions(self):
            assert self._local_delta_contributions is not None, (
                f"no local delta invariants of the singular points were given when {self} was constructed"
            )
            return self._local_delta_contributions

        local_contributions = local_delta_contributions

        def total_delta_contribution(self):
            return sum(
                (int(contribution.weighted_contribution()) for contribution in self.local_delta_contributions()),
                0,
            )

        def is_geometrically_integral(self) -> bool:
            r"""The selected normalization by ``P^1`` certifies geometric integrality in this representation."""
            normalization = self.normalization_curve()
            assert (
                normalization in ProjectiveSpaces(self.scheme_base_ring())
                and int(normalization.relative_dimension()) == 1
            ), (
                f"geometric integrality of {self} is not decided by the selected "
                f"normalization {normalization}: only a projective-line normalization "
                "has a represented certificate here"
            )
            return True

        def normalization_is_connected(self) -> bool:
            r"""A chosen integral normalization is connected, whether or not it is ``P^1``."""
            normalization = self.normalization_curve()
            assert normalization in Curves(self.scheme_base_ring()), (
                f"connectedness of the normalization of {self} requires a selected integral curve, "
                f"but the chosen normalization {normalization} is not placed in Curves"
            )
            return True

    class Projective(CategoryWithAxiom):
        r"""Integral projective curves over the base.

        Over a field the arithmetic genus ``p_a(C) = 1 - P_C(0)`` is read off
        the Hilbert polynomial of a projective embedding, so the genus
        operations live at this axiom, the weakest structure that states them.
        """

        def an_object(self):
            r"""The projective line."""
            return ProjectiveSpaces(self.base_ring())(1)

        class ParentMethods:
            def arithmetic_genus(self):
                r"""Return the arithmetic genus ``p_a(C)=1-P_C(0)``.

                For a projective curve the Hilbert polynomial is the defining
                projective invariant whose constant term gives ``1-p_a``.  The
                computation therefore belongs to the projective presentation and
                remains distinct from normalization/geometric-genus algorithms.
                """
                base = self.scheme_base_ring()
                assert base in OwnedFields(), (
                    f"the numerical Hilbert-polynomial arithmetic genus of {self} requires a field base, not {base}"
                )
                integers = _owned_integers()
                if self in ProjectiveSpaces(base):
                    return integers.zero()
                defining_ideal = self.defining_ideal_owned()
                return integers.one() - integers(
                    defining_ideal.hilbert_polynomial_value(0)
                )

            @cached_method
            def genus_comparison(self):
                from sage_extensions.categories.schemes.curve_genus import _CurveGenusComparison

                return _CurveGenusComparison(self)

            def geometric_genus(self):
                r"""The genus of the normalization, or the arithmetic genus when smooth."""
                match self._normalization_curve:
                    case None:
                        assert self.is_smooth(), (
                            f"the geometric genus of {self} needs its normalization: {self} is not "
                            "known to be smooth and no normalization was given"
                        )
                        return self.arithmetic_genus()
                    case _:
                        normalized = self.normalization_curve()
                        base = self.scheme_base_ring()
                        assert normalized in Curves(base).Projective(), (
                            f"the geometric genus of {self} is the arithmetic genus of its normalization "
                            f"{normalized}, which must be a projective curve over {base}, but it is in "
                            f"{normalized.category()}"
                        )
                        return normalized.arithmetic_genus()

            def genus(self):
                r"""Return geometric genus, never arithmetic genus by convention."""
                return self.geometric_genus()


class Surfaces(_DimensionSubcategoryOfVarieties):
    r"""Varieties of relative dimension two over the stated base."""

    relative_dimension = 2

    def an_object(self):
        r"""The projective plane, of relative dimension two."""
        from sage_extensions.categories.schemes.schemes import _integral_placement

        assert _integral_placement(self.base_ring()), (
            f"the projective plane over {self.base_ring()} is a surface only when the base is integral"
        )
        return ProjectiveSpaces(self.base_ring())(2)

    def _repr_object_names(self):
        return f"surfaces over {self.base_ring()}"

    class ParentMethods:
        def is_del_pezzo(self) -> bool:
            r"""Decide whether the surface ``X`` is smooth and projective with ``omega_X^{-1}`` ample.

            Domain: a surface ``X`` over a field.  Codomain: a truth value.
            A del Pezzo surface is projective [Dol12, Rem. 8.1.19], so the
            decision is made on projective surfaces by
            :meth:`Surfaces.Projective.ParentMethods.is_del_pezzo`; a surface
            not placed projective reaches this stub.
            """
            assert False, f"is_del_pezzo on Surfaces: not implemented for {self} outside projective surfaces"

        def _is_del_pezzo(self) -> bool:
            r"""Ampleness of ``-K_X`` on a smooth projective surface; realizations supply it.

            This default sorts after every realization category (complete
            intersections, projective spaces, point blowups), so it is reached
            only by a surface whose realization decides nothing.
            """
            assert False, f"ampleness of -K_X on Surfaces: not implemented for {self}"

        def _is_gorenstein_del_pezzo(self) -> bool:
            r"""Normality, the Gorenstein property and ampleness of ``-K_X`` on a singular projective surface."""
            assert False, f"the Gorenstein del Pezzo condition on Surfaces: not implemented for {self}"

        def _del_pezzo_degree(self):
            r"""The self-intersection ``K_X^2`` of a Gorenstein del Pezzo surface; realizations supply it."""
            assert False, f"K_X^2 on Surfaces: not implemented for {self}"

    class SubcategoryMethods:
        def K3(self):
            r"""Return this category with the axiom that its objects are K3 surfaces."""
            return self._with_axiom("K3")

        def DelPezzo(self):
            r"""Return this category with the axiom that its objects are smooth del Pezzo surfaces."""
            return self._with_axiom("DelPezzo")

    class Proper(CategoryWithAxiom):
        r"""Proper integral surfaces over the base.

        Over a field, two invertible sheaves on a proper surface have an
        integer-valued numerical intersection number (Stacks Project, Tag 0BEP).
        This is therefore the common owner of the Picard intersection pairing
        for represented proper surfaces.  Computational families implement
        only the private hook.
        """

        def an_object(self):
            r"""The projective plane, hence a proper integral surface."""
            return ProjectiveSpaces(self.base_ring())(2)

        class ParentMethods:
            @cached_method
            def picard_intersection_pairing(self):
                r"""Return ``Pic(X) x Pic(X) -> ZZ`` by numerical intersection."""
                base = self.scheme_base_ring()
                assert base in OwnedFields(), (
                    f"the integer-valued numerical intersection pairing on Pic({self}) is owned here for "
                    f"proper surfaces over a field, but the base ring is {base}"
                )
                return self._picard_intersection_pairing()

    class Projective(CategoryWithAxiom):
        r"""Projective integral surfaces over the base.

        Two del Pezzo conventions are stated here.  A smooth del Pezzo surface
        is a smooth projective surface whose anticanonical sheaf is ample,
        that is a Fano variety of dimension two (Dolgachev, *Classical
        Algebraic Geometry* [Dol12], Rem. 8.1.19); those surfaces are the
        objects of the ``DelPezzo`` axiom.  A Gorenstein del Pezzo surface is
        a normal Gorenstein projective surface whose anticanonical sheaf is
        ample, the convention of Hidaka--Watanabe, *Tokyo J. Math.* 4 (1981),
        319--330; it admits singular points.

        Each realization (projective space, complete intersection, toric
        surface, point blowup) supplies the private hooks ``_is_del_pezzo``
        (ampleness of ``-K_X`` on a smooth surface), ``_is_gorenstein_del_pezzo``
        and ``_del_pezzo_degree`` on its own category.  Their assert-gated
        defaults live on ``Surfaces``: this axiom category sorts ahead of the
        realization categories, so a default here would shadow them.
        """

        def an_object(self):
            r"""The projective plane, a projective integral surface."""
            return ProjectiveSpaces(self.base_ring())(2)

        class ParentMethods:
            def is_del_pezzo(self) -> bool:
                r"""Decide whether ``X`` is smooth with ``omega_X^{-1}`` ample [Dol12, Rem. 8.1.19]."""
                base = self.scheme_base_ring()
                assert base in OwnedFields(), (
                    f"the represented del Pezzo predicate for {self} is owned for projective surfaces over "
                    f"a field, but the base ring is {base}"
                )
                match bool(self.is_smooth()):
                    case False:
                        return False
                    case True:
                        return bool(self._is_del_pezzo())

            def is_gorenstein_del_pezzo(self) -> bool:
                r"""Decide whether ``X`` is normal Gorenstein with ``omega_X^{-1}`` ample (Hidaka--Watanabe)."""
                base = self.scheme_base_ring()
                assert base in OwnedFields(), (
                    f"the represented Gorenstein del Pezzo predicate for {self} is owned for projective "
                    f"surfaces over a field, but the base ring is {base}"
                )
                match bool(self.is_smooth()):
                    case True:
                        # A smooth surface is normal and Gorenstein.
                        return self.is_del_pezzo()
                    case False:
                        return bool(self._is_gorenstein_del_pezzo())

            def del_pezzo_degree(self):
                r"""Return the anticanonical self-intersection ``K_X^2`` of a Gorenstein del Pezzo surface.

                Domain: a Gorenstein del Pezzo surface ``X`` over a field, smooth
                or not, where ``K_X`` is Cartier and ``K_X^2`` is an integer
                (Hidaka--Watanabe, *Tokyo J. Math.* 4 (1981), 319--330).
                Codomain: the positive integers.
                """
                assert self.is_gorenstein_del_pezzo(), (
                    f"the degree K_X^2 is defined for Gorenstein del Pezzo surfaces, and {self} is not one"
                )
                return self._del_pezzo_degree()

    class K3(CategoryWithAxiom):
        r"""K3 surfaces over the base.

        Huybrechts, *Lectures on K3 Surfaces* [Huy16], Ch. 1, Def. 1.1: a K3
        surface over a field ``k`` is a complete nonsingular variety ``X`` of
        dimension two with ``Omega^2_{X/k} ~= O_X`` and ``H^1(X, O_X) = 0``.
        A surface is a variety of dimension two, and complete, nonsingular and
        ``Omega^2 ~= O_X`` together are the Calabi--Yau axiom, the immediate
        supercategory; the vanishing of ``H^1(X, O_X)`` is the property this
        axiom adds.  Applying the category is the caller's statement of it;
        :meth:`ParentMethods.validate_k3` is the check.
        """

        def extra_super_categories(self):
            return [Surfaces(self.base_ring()).CalabiYau()]

        def _repr_object_names(self):
            return f"K3 surfaces over {self.base_ring()}"

        def an_object(self):
            r"""The Fermat quartic ``V_+(x_0^4 + x_1^4 + x_2^4 + x_3^4) <= P^3`` [Huy16, Ch. 1, Ex. 1.3], when ``2`` is a unit of the base."""
            from sage_extensions.categories.schemes.complete_intersections import (
                ProjectiveCompleteIntersections,
            )

            return ProjectiveCompleteIntersections(self.base_ring()).Smooth().K3().an_object()

        def _call_(self, surface):
            r"""Place the Calabi--Yau surface ``surface`` here, as the caller states."""
            from sage_extensions.refine import refine

            base = self.base_ring()
            assert surface in Surfaces(base).CalabiYau(), (
                f"only a Calabi--Yau surface over {base} is a K3 surface, but {surface} is in "
                f"{surface.category()}"
            )
            return refine(surface, self)

        class ParentMethods:
            def is_k3(self):
                return True

            @validator
            def validate_k3(self) -> None:
                r"""Check the caller's statement that ``H^1(X, O_X) = 0`` [Huy16, Ch. 1, Def. 1.1]."""
                assert False, (
                    f"the vanishing of H^1(X, O_X) for the K3 surface {self}: not implemented"
                )

    class DelPezzo(CategoryWithAxiom):
        r"""Smooth del Pezzo surfaces over the base.

        A smooth projective surface ``X`` whose anticanonical sheaf
        ``omega_X^{-1}`` is ample (Dolgachev [Dol12], Rem. 8.1.19).
        Projectivity and smoothness are the immediate supercategories;
        ampleness of ``omega_X^{-1}`` is the property this axiom adds.
        Applying the category to a projective surface is the caller's
        statement of that property; :meth:`ParentMethods.validate_del_pezzo`
        checks it.
        """

        def extra_super_categories(self):
            base = self.base_ring()
            return [Surfaces(base).Projective(), Surfaces(base).Smooth()]

        def _repr_object_names(self):
            return f"del Pezzo surfaces over {self.base_ring()}"

        def an_object(self):
            r"""The projective plane, whose anticanonical sheaf ``O(3)`` is ample."""
            return self(ProjectiveSpaces(self.base_ring())(2))

        def _call_(self, surface):
            r"""Place the projective surface ``surface`` here, as the caller states."""
            from sage_extensions.refine import refine

            base = self.base_ring()
            assert surface in Surfaces(base).Projective(), (
                f"only a projective surface over {base} is a del Pezzo surface, but {surface} is in "
                f"{surface.category()}"
            )
            return refine(surface, self)

        class ParentMethods:
            @validator
            def validate_del_pezzo(self) -> None:
                r"""Check the caller's statement that ``X`` is smooth with ``omega_X^{-1}`` ample."""
                assert self.is_del_pezzo(), (
                    f"{self} was placed as a del Pezzo surface, but it is not smooth with ample "
                    "anticanonical sheaf"
                )


__all__ = ["Curves", "Surfaces", "Varieties"]

