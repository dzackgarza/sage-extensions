r"""Projective complete intersections with their selected regular sequence.

A complete intersection ``X = V_+(f_1, ..., f_r) <= P^n_R`` is a closed
subscheme of projective space together with the homogeneous equations cutting
it out, where ``f_1, ..., f_r`` is a regular sequence.  It is constructed by
the closed-subscheme construction of ``P^n_R`` with the placement
``ProjectiveCompleteIntersections(R)``; the category adds no datum of its own:
its codimension, multidegree and ambient are read off the equations and the
inclusion.

The base change ``X_{R'} = X x_{Spec R} Spec R'`` along ``g: R -> R'`` is the
closed subscheme of ``P^n_{R'}`` cut out by the base-changed equations, and it
is constructed as an object of ``FiberProductSchemes(R')``: its left projection
is ``X_{R'} -> X`` and its right projection is the structure morphism.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.algebras.free_algebras import SymmetricAlgebras
from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    OwnedCategoryOverBaseRing,
    OwnedFields,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.schemes.schemes import (
    ClosedSubschemes,
    FiberProductSchemes,
    ProjectiveSpaces,
    SchemeFiberProductConstruction,
    SchemeMorphism,
    Schemes,
    _engine_projective_subscheme,
    _projective_closed_subscheme,
    _projective_equation_family,
    _engine_scheme,
    _equation_family,
    _native_scheme_mor,
    _scheme_mor_category,
    _structure_morphism_rule,
)
from sage_extensions.categories.schemes.varieties import Curves, Surfaces, Varieties
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.owned_category_bases import CategoryWithAxiom


def _complete_intersection_base_supported(base) -> bool:
    r"""Whether the base is a field, a localization of one, or a polynomial algebra over one.

    Over these bases the homogeneous coordinate ring is regular.  The selected
    sequence is checked by successive nonzerodivisors, not just final height.
    """
    match base:
        case _ if base in OwnedFields():
            return True
        case _ if base in LocalizationRings():
            return _complete_intersection_base_supported(base.localization_source())
        case _ if base.base_ring() in OwnedFields():
            return base in SymmetricAlgebras(base.base_ring())
        case _:
            return False


def _projective_complete_intersection(ambient, equations, placements=(), **level_data):
    r"""``V_+(f_1, ..., f_r) <= P^n_R`` as a complete intersection.

    The equations are the selected regular sequence.  The closed subscheme is
    constructed once, with its complete-intersection placement and any further
    placement a construction states (the fibre-product placement of a base
    change); the regular-sequence criterion is checked on the native ideal
    before the object is constructed.
    """
    base = ambient.scheme_base_ring()
    assert ambient in ProjectiveSpaces(base), (
        f"a complete intersection V_+(f_1, ..., f_r) is constructed here only inside projective "
        f"space P^n over {base}, but {ambient} is in {ambient.category()}"
    )
    assert _complete_intersection_base_supported(base), (
        f"the regular-sequence test for a complete intersection in {ambient} is implemented only "
        f"over a field, a localization of a supported ring, or a polynomial ring over a field, "
        f"but the base ring is {base}"
    )
    family = _projective_equation_family(_equation_family(equations))
    assert family.cardinality() > 0, (
        f"a complete intersection in {ambient} needs at least one equation, but none were given"
    )
    engine = _engine_projective_subscheme(_engine_scheme(ambient), family)
    # A single nonzero homogeneous polynomial is a nonzerodivisor in the
    # polynomial ring over a field.  This is the length-one case of the
    # regular-sequence definition (Stacks, Tag 00LF).
    regular = (
        family.cardinality() == 1
        and base in OwnedFields()
        and bool(engine.defining_polynomials()[0])
    ) or _is_regular_sequence(engine)
    assert regular, (
        f"the equations {family} do not form a regular sequence in the homogeneous coordinate "
        f"ring of {ambient}, so V_+ of them is not a complete intersection"
    )
    decided = [ProjectiveCompleteIntersections(base)]
    expected_dimension = int(ambient.relative_dimension()) - int(family.cardinality())
    # Integrality is placement (CON-07), never computed here (OWN-22): the
    # caller states Schemes(k).Integral(), or states smoothness, and a smooth
    # complete intersection of positive dimension is connected (Hartshorne,
    # Exercise III.5.5), hence integral.  An integral projective scheme over a
    # field is a projective variety (Hartshorne I.2, II.4).
    stated_integral = any(category.is_subcategory(Schemes(base).Integral()) for category in placements)
    stated_smooth = any(
        category.is_subcategory(ProjectiveCompleteIntersections(base).Smooth()) for category in placements
    )
    integral = stated_integral or (stated_smooth and expected_dimension >= 1)
    match base:
        case _ if base in OwnedFields():
            match expected_dimension:
                case 1 if integral:
                    decided.append(Curves(base).Projective())
                case 2 if integral:
                    decided.append(Surfaces(base).Projective())
                case _ if integral:
                    decided.append(Varieties(base).Projective())
                case _:
                    pass
        case _:
            pass
    return _projective_closed_subscheme(
        ambient, family, placements=(*decided, *placements),
        _engine=engine, **level_data,
    )


def _is_regular_sequence(engine):
    r"""Decide regularity of the selected equations before allocating the scheme.

    Engine adapter (``OWN-06``): flatten a polynomial coefficient tower by
    Sage's polynomial-ring isomorphism, then use its ideal-quotient engine.
    No parameter is inverted: this tests the sequence over the stated base,
    not over its fraction field.

    If ``I`` is generated by the preceding equations, multiplication by
    ``f`` on ``S/I`` has kernel ``(I : (f))/I``.  It is injective exactly when
    ``I : (f) = I``.  The final quotient must also be nonzero (Stacks, 00LF).
    Final height alone does not suffice for a chosen global sequence:
    ``t*x, t*y, 1-t`` has height three, but ``x`` annihilates ``t*y`` modulo
    ``(t*x)``.  Sage's maintained ``MPolynomialIdeal.quotient`` computes each
    colon ideal; no local Groebner or regular-sequence algorithm is copied.
    """
    original = engine.ambient_space().coordinate_ring()
    flatten = original.flattening_morphism()
    ring = flatten.codomain()
    prefix = ring.ideal(ring.zero())
    for equation in engine.defining_polynomials():
        principal = ring.ideal(flatten(equation))
        match prefix.quotient(principal) == prefix:
            case False:
                return False
            case True:
                prefix = prefix + principal
    return ring.one() not in prefix


class ProjectiveCompleteIntersections(OwnedCategoryOverBaseRing):
    r"""Closed complete intersections in projective space over a regular base.

    Over a field, a localization, and a polynomial parameter algebra over a
    field, the homogeneous coordinate ring is regular.  Each selected equation
    must be a nonzerodivisor modulo its predecessors, and the final quotient
    must be nonzero; the engine checks those exact conditions before placement.
    """

    def an_object(self):
        r"""The point ``V_+(x) <= P^1``, cut out by one linear form."""
        line = ProjectiveSpaces(self.base_ring())(1)
        x, _y = line.homogeneous_coordinate_generators()
        return self(line, x)

    def _call_(self, ambient, *equations, placements=()):
        r"""``V_+(f_1, ..., f_r) <= P^n_R`` for a regular sequence of homogeneous equations.

        The equations are given one by one or as one finite family.  A caller
        that knows the scheme integral states ``Schemes(R).Integral()`` in
        ``placements``.
        """
        assert ambient.scheme_base_ring() is self.base_ring(), (
            f"cannot construct a complete intersection of {self} in {ambient}: it lies over "
            f"{ambient.scheme_base_ring()}, not over {self.base_ring()}"
        )
        return _projective_complete_intersection(ambient, equations, placements=placements)

    def _repr_object_names(self):
        return f"projective complete intersections over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring()).Projective(), ClosedSubschemes(self.base_ring())]

    class Smooth(CategoryWithAxiom):
        r"""Projective complete intersections smooth over the base.

        Smoothness is a property, so it is placement (``CON-07``): applying
        this category to ``(P^n, f_1, ..., f_r)`` is the caller's statement
        that ``V_+(f_1, ..., f_r) -> Spec R`` is smooth, and the object is
        constructed here without computing it (``OWN-22``).  The check is the
        validator :meth:`ParentMethods.validate_smoothness`, called by hand.
        """

        def an_object(self):
            r"""The point ``V_+(x) <= P^1``, smooth because it is ``Spec R``."""
            line = ProjectiveSpaces(self.base_ring())(1)
            x, _y = line.homogeneous_coordinate_generators()
            return self(line, x)

        def _call_(self, ambient, *equations):
            r"""``V_+(f_1, ..., f_r) <= P^n_R``, stated smooth by the caller."""
            assert ambient.scheme_base_ring() is self.base_ring(), (
                f"cannot construct a complete intersection of {self} in {ambient}: it lies over "
                f"{ambient.scheme_base_ring()}, not over {self.base_ring()}"
            )
            return _projective_complete_intersection(ambient, equations, placements=(self,))

        class SubcategoryMethods:
            def K3(self):
                r"""Return this category with the axiom that its objects are K3 surfaces."""
                return self._with_axiom("K3")

        class K3(CategoryWithAxiom):
            r"""Smooth projective complete intersections that are K3 surfaces.

            The objects of ``Surfaces(R).K3()`` (Huybrechts [Huy16], Ch. 1,
            Def. 1.1) that are complete intersections; a smooth quartic in
            ``P^3`` is the standard specimen.
            Applying the category to a complete intersection is the caller's
            statement that it is a K3 surface.  The integral topology and the
            Hodge structure are computed by realizations which assert their
            own regime (a smooth quartic over ``QQ``).
            """

            def extra_super_categories(self):
                return [Surfaces(self.base_ring()).K3()]

            def an_object(self):
                r"""The Fermat quartic ``V_+(x_0^4 + x_1^4 + x_2^4 + x_3^4) <= P^3``, when ``2`` is a unit of ``R``.

                The partial derivatives are ``4 x_i^3``, so the quartic is smooth over
                ``R`` exactly when ``2`` is invertible in ``R``; in characteristic ``2``
                it is ``(x_0 + x_1 + x_2 + x_3)^4``, the fourfold plane.
                """
                base = self.base_ring()
                assert base(2).is_unit(), (
                    f"the Fermat quartic is smooth over {base} only when 2 is a unit of {base}; "
                    f"an object of {self} over a base where 2 is not a unit: not implemented"
                )
                ambient = ProjectiveSpaces(self.base_ring())(3)
                x = tuple(ambient.homogeneous_coordinate_generators())
                return self(ProjectiveCompleteIntersections(self.base_ring()).Smooth()(ambient, sum(v**4 for v in x)))

            def _call_(self, scheme):
                r"""State that the retained projective closed subscheme is a smooth K3 complete intersection."""
                from sage_extensions.refine import refine

                base = self.base_ring()
                assert scheme in ClosedSubschemes(base), (
                    f"a stated K3 complete intersection over {base} needs its closed immersion, but "
                    f"{scheme} is in {scheme.category()}"
                )
                assert scheme.inclusion().codomain() in ProjectiveSpaces(base), (
                    f"a stated K3 complete intersection needs an ambient projective space over {base}, "
                    f"but {scheme} lies in {scheme.inclusion().codomain()}"
                )
                return refine(scheme, self)

            class ParentMethods:
                @cached_method
                def integral_topology(self):
                    from sage_extensions.categories.schemes.geometric_cohomology import _QuarticK3IntegralTopology
                    return _QuarticK3IntegralTopology(self)

                @cached_method
                def _hodge_structure(self):
                    r"""The Hodge structure on ``H^*(X(CC); ZZ)`` of the quartic K3 surface.

                    The required value is ``⊕_k H^k(X(CC); ZZ)`` as an object of
                    ``MixedHodgeStructures(ZZ)`` whose weight filtration splits with
                    ``Gr^W_k = H^k`` in ``HodgeStructures(ZZ, k)``; ``H^2`` is polarized
                    by the intersection form (Deligne, Théorie de Hodge II, (2.1.1),
                    (2.1.15), (2.3.1)).
                    """
                    from sage_extensions.categories.schemes.geometric_cohomology import (
                        _quartic_k3_hodge_structure,
                    )

                    return _quartic_k3_hodge_structure(self)

        class ParentMethods:
            def validate_smoothness(self) -> None:
                r"""Check the caller's statement that ``X -> Spec k`` is smooth.

                Hartshorne, *Algebraic Geometry* [Har10a], III Thm. 10.2:
                ``X -> Spec k`` is smooth of relative dimension ``m`` exactly
                when ``X_{kbar}`` is equidimensional of dimension ``m`` and
                regular.  By I §5 (the definition before Thm. 5.1, and
                Thm. 5.1) with Ex. I.5.8 for the projective form, a point of
                ``V_+(f_1, ..., f_r) <= P^n_{kbar}`` of dimension ``n - r``
                is regular exactly when the Jacobian matrix
                ``(df_i/dx_j)`` has rank ``r`` there.  Sage's maintained
                ``is_smooth`` of the projective subscheme computes this
                criterion.  The answer is an untrusted computation and a
                diagnostic for the caller; construction does not run it.
                """
                base = self.scheme_base_ring()
                assert base in OwnedFields(), (
                    f"the Jacobian criterion for the smoothness of {self} is applied over a "
                    f"field, but the base ring is {base}"
                )
                assert bool(_engine_scheme(self).is_smooth()), (
                    f"{self} was constructed as smooth over {base}, but the Jacobian criterion "
                    "finds a singular point"
                )

    class ParentMethods:
        def is_complete_intersection(self) -> bool:
            return True

        def complete_intersection_ambient(self):
            r"""The projective space ``P^n_R`` this complete intersection is cut out of."""
            return self.inclusion().codomain()

        def defining_degrees(self):
            r"""The degrees ``d_1, ..., d_r`` of the selected regular sequence."""
            integers = _owned_integers()
            return finite_family(
                tuple(
                    integers(int(equation.degree()))
                    for equation in self.defining_equations()
                ),
                name="Complete-intersection defining degrees",
            )

        def complete_intersection_codimension(self):
            return self.defining_equations().cardinality()

        def expected_dimension(self):
            return self.complete_intersection_ambient().relative_dimension() - _own_ring(
                SageZZ
            )(int(self.complete_intersection_codimension()))

        def family_base_scheme(self):
            return self.base_scheme()

        def family_morphism(self):
            r"""Return the relative projective complete-intersection morphism to its base."""
            return self.structure_morphism()

        def base_change_source_complete_intersection(self):
            r"""``X`` for ``X_{R'} = X x_{Spec R} Spec R'``: the domain of the left cospan leg."""
            assert self in FiberProductSchemes(self.scheme_base_ring()), (
                f"{self} was not constructed as a base change X x_(Spec R) Spec R', so it has "
                "no original complete intersection X"
            )
            return self.fiber_product_cospan()[0].domain()

        def base_change_projection(self):
            r"""The projection ``X_{R'} -> X`` of the scalar base-change pullback."""
            assert self in FiberProductSchemes(self.scheme_base_ring()), (
                f"{self} was not constructed as a base change X x_(Spec R) Spec R', so it has "
                "no projection to an original complete intersection X"
            )
            return self.left_projection()

        def adjunction_twist_degree(self):
            r"""Return ``sum(d_i) - n - 1`` in ``K_X = O_X(sum d_i-n-1)``.

            This is the integer in the projective complete-intersection
            adjunction formula.  The canonical bundle and the adjunction
            isomorphism are returned by :meth:`canonical_line_bundle` and
            :meth:`adjunction_isomorphism`.
            """
            integers = _owned_integers()
            ambient_dimension = integers(
                int(self.complete_intersection_ambient().relative_dimension())
            )
            return (
                sum(self.defining_degrees(), integers.zero())
                - ambient_dimension
                - integers.one()
            )

        def is_gorenstein(self) -> bool:
            r"""Return ``True``: a quotient of a regular ring by a regular sequence is Gorenstein."""
            return True

        def is_normal(self) -> bool:
            r"""Decide normality by Serre's criterion in characteristic zero.

            A complete intersection is Cohen--Macaulay, hence satisfies ``S_2``.
            Thus normality is equivalent to ``R_1``.  Sage's projective
            Jacobian ideal is computed on the affine cone: if ``X`` has
            dimension ``d >= 1``, ``R_1`` says its projective singular locus
            has dimension at most ``d-2``, equivalently the affine-cone
            Jacobian locus has dimension at most ``d-1``.  In dimension zero,
            characteristic zero makes normality equivalent to smoothness.
            """
            base = self.scheme_base_ring()
            assert base in OwnedFields(), (
                f"normality of the complete intersection {self} is decided here only over a field, "
                f"but its base ring {base} is not a field"
            )
            assert int(_engine_ring(base).characteristic()) == 0, (
                f"normality of the complete intersection {self} is decided here only in "
                f"characteristic zero, but {base} has characteristic {_engine_ring(base).characteristic()}"
            )
            dimension = int(self.expected_dimension())
            if dimension == 0:
                return bool(self.is_smooth())
            singular_cone_dimension = int(_engine_scheme(self).Jacobian().dimension())
            return singular_cone_dimension <= dimension - 1

        def projective_degree(self):
            r"""Return the complete-intersection degree ``prod d_i``."""
            degree = _owned_integers().one()
            for value in self.defining_degrees():
                degree *= value
            return degree

        def anticanonical_twist_degree(self):
            r"""Return ``n + 1 - sum(d_i)`` for ``-K_X``."""
            return -self.adjunction_twist_degree()

        @cached_method
        def restricted_ambient_canonical_bundle(self):
            r"""``omega_P|_X = O_X(-n-1)``, the restricted canonical bundle of the ambient."""
            return self.complete_intersection_ambient().canonical_line_bundle().restrict_to(self)

        @cached_method
        def normal_determinant_line_bundle(self):
            r"""``det N_{X/P} = O_X(sum d_i)`` for the selected regular sequence."""
            return self.O(sum(self.defining_degrees()))

        @cached_method
        def adjunction_isomorphism(self):
            r"""The adjunction isomorphism ``omega_X ~= omega_P|_X tensor det N_{X/P}``.

            Its domain is the canonical bundle ``O_X(sum d_i - n - 1)`` and its
            codomain is the tensor product of the restricted ambient canonical
            bundle with the determinant of the normal bundle.
            """
            canonical = self.O(self.adjunction_twist_degree())
            target = self.restricted_ambient_canonical_bundle().tensor_product(
                self.normal_determinant_line_bundle()
            )
            return canonical.canonical_isomorphism_to(target)

        def adjunction_target(self):
            r"""``omega_P|_X tensor det N_{X/P}``, the codomain of the adjunction isomorphism."""
            return self.adjunction_isomorphism().codomain()

        def canonical_line_bundle(self):
            return self.adjunction_isomorphism().domain()

        canonical_bundle = canonical_line_bundle

        @cached_method
        def anticanonical_line_bundle(self):
            return self.canonical_line_bundle().dual_sheaf()

        def anticanonical_bundle(self, *args, **kwargs):
            return self.anticanonical_line_bundle(*args, **kwargs)

        def _is_del_pezzo(self) -> bool:
            r"""Decide ampleness of ``-K_X`` for a smooth integral CI surface.

            Adjunction constructs ``-K_X`` as an actual restricted projective
            line bundle; :meth:`Surfaces.Projective.ParentMethods.is_del_pezzo`
            has already decided smoothness.
            """
            base = self.scheme_base_ring()
            assert self in Surfaces(base).Projective(), (
                f"the complete-intersection del Pezzo algorithm applies only after {self} is known to "
                f"be an integral projective surface, but it is in {self.category()}"
            )
            return bool(self.anticanonical_line_bundle().is_ample())

        def _is_gorenstein_del_pezzo(self) -> bool:
            r"""Decide the normal Gorenstein del Pezzo condition for an integral CI surface.

            A complete intersection is Gorenstein, so normality is the
            remaining singularity hypothesis, and ampleness is delegated to
            the anticanonical line bundle (Hidaka--Watanabe, *Tokyo J. Math.*
            4 (1981), 319--330).
            """
            base = self.scheme_base_ring()
            assert self in Surfaces(base).Projective(), (
                f"the complete-intersection Gorenstein del Pezzo algorithm applies only after {self} is "
                f"known to be an integral projective surface, but it is in {self.category()}"
            )
            return bool(self.is_normal() and self.anticanonical_line_bundle().is_ample())

        def integral_singular_cohomology(self, degree):
            r"""``H^degree(X(CC); ZZ)``, the cohomology of the complex realization along ``QQ -> CC``."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _integral_singular_cohomology_over_rationals,
            )
            return _integral_singular_cohomology_over_rationals(self, degree)

        def _picard_group(self):
            r"""``Pic(X)``, the isomorphism classes of invertible ``O_X``-modules, with unit ``[O_X(0)]``."""
            from sage_extensions.categories.divisors.picard_groups import (
                _invertible_sheaf_class_group,
            )

            return _invertible_sheaf_class_group(self, self.O(0))

        def hyperplane_class(self):
            r"""``[O_X(1)] = i^*[O_P(1)]`` in ``Pic(X)``, for the inclusion ``i: X -> P^n``.

            ``O_X(1)`` is very ample, so ``(X, [O_X(1)])`` is a polarized
            variety (Hartshorne, *Algebraic Geometry*, II.5.16.1 and II.7).
            """
            picard = self.picard_group()
            return picard(picard.underlying_set()(self.O(1)))

        def _del_pezzo_degree(self):
            r"""Return ``(-K_X)^2 = (n + 1 - sum d_i)^2 prod d_i`` for a del Pezzo complete intersection."""
            coefficient = self.anticanonical_twist_degree()
            return coefficient**2 * self.projective_degree()


__all__ = [
    "ProjectiveCompleteIntersections",
]
