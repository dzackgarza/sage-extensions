r"""Owned blowups and the projective-plane point-blowup specialization.

The common owner is the blowup

``b : Bl_Z(X) = Proj_X(\bigoplus_{n >= 0} I_Z^n) -> X``

of a scheme along a closed subscheme.  Its retained level data are the source
``X`` and center ``Z <= X``.  Computational specializations supply the selected
realization of the blowdown, exceptional divisor, and transforms without
moving those public operations down to the specialization.

For a point ``p`` of ``P^2`` choose the two canonical linear forms obtained by
normalizing one nonzero homogeneous coordinate.  They form a regular sequence
cutting out ``p``.  The Rees construction is the graph closure

``Bl_p(P^2) <= P^2 x P^1``

cut out by ``f V - g U``.  This is the codimension-two regular-center blowup,
not a toric specialization.  The blowup is constructed by the closed-subscheme
construction of ``P^2 x P^1`` with the placement ``ProjectivePointBlowups(R)``,
whose level data are the point ``p``, the center ``V(f, g) <= P^2`` and the
bihomogeneous coordinate datum the graph relation is written in.  The blowdown
is the first product projection restricted along the inclusion.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.modules.pure.modules import BilinearMap
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.schemes.schemes import (
    ClosedSubschemes,
    EffectiveCartierDivisors,
    ProjectiveSpaces,
    Schemes,
)
from sage_extensions.categories.schemes.varieties import Surfaces
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)


def _integers():
    return _owned_integers()


class Blowups(OwnedCategoryOverBaseRing):
    r"""Schemes represented as a selected blowup ``Bl_Z(X) -> X``.

    The level datum is the source scheme ``X`` together with the closed center
    ``Z <= X``.  The mathematical blowup is the relative Proj of the Rees
    algebra of the center ideal.  Existing specialized realizations retain the
    same datum and implement the private computational hooks below.
    """

    def _repr_object_names(self):
        return f"blowups of schemes over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring())]

    def an_object(self):
        from sage_extensions.categories.schemes.toric.blowups import (
            ToricFixedPointBlowups,
        )

        return ToricFixedPointBlowups(self.base_ring()).an_object()

    class ParentMethods:
        def __init__(self, blowup_source, blowup_center, **rest) -> None:
            base = blowup_source.scheme_base_ring()
            assert blowup_center in ClosedSubschemes(base), (
                f"the center of the blowup of {blowup_source} must be a closed subscheme over {base}, "
                f"but {blowup_center} is in {blowup_center.category()}"
            )
            assert blowup_center.inclusion().codomain() is blowup_source, (
                f"the center of the blowup of {blowup_source} must be a closed subscheme of that source, "
                f"but {blowup_center} lies in {blowup_center.inclusion().codomain()}"
            )
            self._blowup_source = blowup_source
            self._blowup_center = blowup_center
            super().__init__(**rest)

        def blowup_source(self):
            r"""Return ``X`` for this selected blowup ``Bl_Z(X)``."""
            return self._blowup_source

        def blowup_center(self):
            r"""Return the closed center ``Z <= X`` of this selected blowup."""
            return self._blowup_center

        @cached_method
        def source_picard_group(self):
            r"""Return ``Pic(X)`` for the source ``X`` of this blowup."""
            return self.blowup_source().picard_group()

        @cached_method
        def blowup_morphism(self):
            r"""Return the selected blowdown ``Bl_Z(X) -> X``."""
            return self._blowup_morphism()

        def _blowup_morphism(self):
            raise AssertionError(
                f"the blowdown of {self} exists as the relative-Proj structure morphism, but this "
                "blowup realization does not supply its represented map"
            )

        def blowdown(self, *args, **kwargs):
            return self.blowup_morphism(*args, **kwargs)

        @cached_method
        def exceptional_divisor(self):
            r"""Return the exceptional divisor ``b^{-1}(Z)`` as a closed subscheme."""
            return self._exceptional_divisor()

        def _exceptional_divisor(self):
            raise AssertionError(
                f"the exceptional divisor of {self} is the inverse image of {self.blowup_center()} under "
                f"{self.blowup_morphism()}, but this realization does not compute that non-affine fibre product"
            )

        def scheme_theoretic_inverse_image(self, closed_subscheme):
            r"""Return ``b^{-1}(Y)`` for a represented closed subscheme ``Y <= X``."""
            assert closed_subscheme in ClosedSubschemes(self.scheme_base_ring()), (
                f"the inverse image under the blowup {self} needs a closed subscheme of "
                f"{self.blowup_source()}, but {closed_subscheme} is in {closed_subscheme.category()}"
            )
            assert closed_subscheme.inclusion().codomain() is self.blowup_source(), (
                f"{closed_subscheme} is a closed subscheme of {closed_subscheme.inclusion().codomain()}, "
                f"not of the blowup source {self.blowup_source()}"
            )
            return self._scheme_theoretic_inverse_image(closed_subscheme)

        def _scheme_theoretic_inverse_image(self, closed_subscheme):
            return self.blowup_morphism().inverse_image(closed_subscheme)

        def total_transform(self, closed_subscheme):
            r"""Return the total transform ``b^{-1}(Y)`` of ``Y <= X``."""
            return self.scheme_theoretic_inverse_image(closed_subscheme)

        def strict_transform(self, closed_subscheme):
            r"""Return the strict transform of ``closed_subscheme`` under this blowup."""
            return self._strict_transform(closed_subscheme)

        def _strict_transform(self, closed_subscheme):
            raise AssertionError(
                f"the strict transform of {closed_subscheme} under {self} is defined as the closure of the "
                "inverse image away from the center, but this realization does not compute that closure"
            )

        def picard_pullback_morphism(self):
            r"""Return the represented pullback ``b^*: Pic(X) -> Pic(Bl_Z(X))``."""
            return self._picard_pullback_morphism()

        def _picard_pullback_morphism(self):
            raise AssertionError(
                f"pullback along {self.blowup_morphism()} induces Pic({self.blowup_source()}) -> Pic({self}), "
                "but this blowup realization does not yet represent that homomorphism"
            )

        def exceptional_picard_class(self):
            r"""Return the Picard class of the exceptional divisor."""
            return self.exceptional_divisor().picard_class()

        def _represented_exceptional_picard_class(self):
            raise AssertionError(
                f"the exceptional divisor of {self} has a Picard class, but this blowup realization does "
                "not yet represent it"
            )

        def pullback_line_bundle(self, source_bundle):
            r"""Return the represented invertible pullback ``b^* source_bundle``."""
            return self._pullback_line_bundle(source_bundle)

        def _pullback_line_bundle(self, source_bundle):
            raise AssertionError(
                f"the pullback of {source_bundle} along {self.blowup_morphism()} is an invertible sheaf, "
                "but this blowup realization does not yet retain an invertible presentation of it"
            )

        def exceptional_line_bundle(self):
            r"""Return ``O(E)`` for the exceptional divisor ``E``."""
            return self._exceptional_line_bundle()

        def _exceptional_line_bundle(self):
            raise AssertionError(
                f"the exceptional divisor of {self} defines O(E), but this blowup realization does not "
                "yet retain an invertible presentation of that line bundle"
            )


class ProjectivePointBlowups(OwnedCategoryOverBaseRing):
    r"""Blowups ``Bl_p(P^2)`` of the projective plane at one rational point ``p``.

    Over a field, the graph-closure realization has the declared projective
    surface placement, and its blowdown retains its exact endpoints::

        sage: from dzack_research.preamble.all import QQ, ProjectivePointBlowups, Surfaces
        sage: B = ProjectivePointBlowups(QQ).an_object()
        sage: B in ProjectivePointBlowups(QQ) and B in Surfaces(QQ).Projective()
        True
        sage: B.blowup_morphism().domain() is B
        True
        sage: B.blowup_morphism().codomain() is B.blowup_point().codomain()
        True
    """

    def _repr_object_names(self):
        return f"projective-plane point blowups over {self.base_ring()}"

    def super_categories(self):
        base = self.base_ring()
        categories = [Blowups(base), Schemes(base).Smooth()]
        match base in OwnedFields():
            case True:
                categories.append(Surfaces(base).Projective())
            case False:
                pass
        return categories

    def an_object(self):
        plane = ProjectiveSpaces(self.base_ring())(2)
        return self(plane.point_morphism((1, 1, 1)))

    def _call_(self, point):
        r"""``Bl_p(P^2)`` for a rational point ``p: Spec R -> P^2_R``."""
        assert point.codomain().scheme_base_ring() is self.base_ring(), (
            f"cannot blow up at {point} in {self}: the plane {point.codomain()} lies over "
            f"{point.codomain().scheme_base_ring()}, not over {self.base_ring()}"
        )
        return _projective_point_blowup(point.codomain(), point)

    class ParentMethods:
        def __init__(self, blowup_point, graph_section_space, **rest) -> None:
            self._blowup_point = blowup_point
            self._graph_section_space = graph_section_space
            super().__init__(**rest)

        def blowup_point(self):
            r"""The rational point ``p: Spec R -> P^2`` that is blown up."""
            return self._blowup_point

        def graph_ambient_product(self):
            r"""``P^2 x P^1``, the codomain of the graph inclusion."""
            return self.inclusion().codomain()

        def _blowup_morphism(self):
            r"""The blowdown ``Bl_p(P^2) -> P^2``: the first projection along the inclusion."""
            return self.graph_ambient_product().projection(0) * self.inclusion()

        def graph_relation(self):
            r"""The bihomogeneous equation ``f V - g U`` cutting the blowup out."""
            return next(iter(self.defining_equations()))

        def graph_section_space(self):
            r"""The sections of ``O(1, 1)`` whose coordinate ring the graph relation is written in."""
            return self._graph_section_space

        def source_coordinate_embedding(self):
            r"""The homogeneous coordinate ring of ``P^2`` inside the bihomogeneous one."""
            return self.graph_section_space().factor_coordinate_embedding(0)

        def center_equations_in_graph_ring(self):
            r"""The center equations ``f, g`` written in the bihomogeneous coordinate ring."""
            embedding = self.source_coordinate_embedding()
            return tuple(embedding(equation) for equation in self.blowup_center().defining_equations())

        def _source_hypersurface_equation_in_graph_ring(self, hypersurface):
            assert hypersurface in ClosedSubschemes(self.scheme_base_ring()), (
                f"the transform under the blowup {self} needs a closed subscheme of "
                f"{self.blowup_source()}, but {hypersurface} is in {hypersurface.category()}"
            )
            assert hypersurface.inclusion().codomain() is self.blowup_source(), (
                f"{hypersurface} is a closed subscheme of {hypersurface.inclusion().codomain()}, "
                f"not of the blown-up plane {self.blowup_source()}"
            )
            equations = hypersurface.defining_equations()
            assert int(equations.cardinality()) == 1, (
                f"the transform under {self} is computed only for a hypersurface V(f) cut out by "
                f"one equation, but {hypersurface} has {equations.cardinality()} defining equations"
            )
            source_ring = self.source_coordinate_embedding().domain()
            raised = hypersurface.homogeneous_defining_equations(source_ring)
            return self.source_coordinate_embedding()(next(iter(raised)))

        def _exceptional_divisor(self):
            r"""``E = pi^{-1}(p)``, cut out in the blowup by the center equations."""
            return self.closed_subscheme(
                self.center_equations_in_graph_ring(),
                placements=(EffectiveCartierDivisors(self),),
                effective_cartier_ideal_sheaf=self.exceptional_line_bundle().dual_sheaf(),
                effective_cartier_picard_class=self._represented_exceptional_picard_class(),
            )

        def _scheme_theoretic_inverse_image(self, hypersurface):
            r"""``pi^{-1}(C)``, cut out in the blowup by the pulled-back equation of ``C``."""
            return self.closed_subscheme(self._source_hypersurface_equation_in_graph_ring(hypersurface))

        def _strict_transform(self, hypersurface):
            r"""The strict transform: the saturation of ``(f V - g U, pi^* h)`` by the center ideal."""
            ring = self.graph_relation().parent()
            equation = self._source_hypersurface_equation_in_graph_ring(hypersurface)
            total_ideal = ring.ideal(self.graph_relation(), equation)
            exceptional_ideal = ring.ideal(*self.center_equations_in_graph_ring())
            saturated = total_ideal.saturation(exceptional_ideal)
            return self.closed_subscheme(tuple(saturated.ideal_generators()))

        def curve_multiplicity_at_center(self, curve):
            equations = curve.defining_equations()
            assert int(equations.cardinality()) == 1, (
                f"the multiplicity of {curve} at the center of {self} is computed only for a plane "
                f"curve V(f) cut out by one equation, but it has {equations.cardinality()} "
                "defining equations"
            )
            degree = int(next(iter(equations)).degree())
            bundle = self.blowup_source().O(degree)
            sections = bundle.global_sections()
            polynomial = next(
                iter(
                    curve.homogeneous_defining_equations(
                        sections.homogeneous_coordinate_ring()
                    )
                )
            )
            section = sections.section_from_homogeneous_polynomial(polynomial)
            multiplicity = 0
            for order in range(1, degree + 2):
                evaluation = bundle.jet_evaluation(self.blowup_point(), order)
                if evaluation(section) != evaluation.codomain().zero():
                    break
                multiplicity = order
            return _integers()(multiplicity)

        @cached_method
        def _picard_group(self):
            from sage_extensions.categories.divisors.picard_groups import PicardGroups

            return _integers()._fresh_free_module_on(
                finite_ordered_set(("H", "E")),
                _extra_categories=(PicardGroups(),),
                _extra_construction_data={"picard_scheme": self},
            )

        def hyperplane_picard_class(self):
            return self.picard_group().module_generator("H")

        def _represented_exceptional_picard_class(self):
            return self.picard_group().module_generator("E")

        @cached_method
        def _picard_pullback_morphism(self):
            source = self.source_picard_group()
            labels = source.module_generating_set()
            assert int(labels.cardinality()) == 1, (
                f"Pic(P^2) = ZZ H should have one module generator, but {source} has "
                f"{labels.cardinality()}"
            )
            return source.module_category().Mor(source, self.picard_group())(
                {next(iter(labels)): self.hyperplane_picard_class()}
            )

        @cached_method
        def _picard_intersection_pairing(self):
            picard = self.picard_group()
            values = _integers().regular_module()

            def value(left, right):
                match (left, right):
                    case ("H", "H"):
                        return _integers().one()
                    case ("E", "E"):
                        return -_integers().one()
                    case _:
                        return _integers().zero()

            return BilinearMap(picard, picard, values, value)

        def curve_degree(self, curve):
            equations = curve.defining_equations()
            assert int(equations.cardinality()) == 1, (
                f"the degree of {curve} as a plane divisor is computed only for a curve V(f) cut "
                f"out by one equation, but it has {equations.cardinality()} defining equations"
            )
            return _integers()(int(next(iter(equations)).degree()))

        def total_transform_picard_class(self, curve):
            return self.curve_degree(curve) * self.hyperplane_picard_class()

        def strict_transform_picard_class(self, curve):
            return (
                self.curve_degree(curve) * self.hyperplane_picard_class()
                - self.curve_multiplicity_at_center(curve)
                * self.exceptional_picard_class()
            )

        def _pullback_line_bundle(self, source_bundle):
            r"""``pi^* O_{P^2}(d) = O_{P^2 x P^1}(d, 0)|_B``."""
            assert source_bundle.projective_space() is self.blowup_source(), (
                f"{source_bundle} is not a line bundle O(d) on the blown-up plane "
                f"{self.blowup_source()}; it lives on {source_bundle.projective_space()}"
            )
            return self.graph_ambient_product().O(
                source_bundle.degree(),
                0,
            ).restrict_to(self)

        @cached_method
        def _exceptional_line_bundle(self):
            r"""Return ``O_B(E)=O_{P^2 x P^1}(1,-1)|_B``."""
            return self.graph_ambient_product().O(1, -1).restrict_to(self)

        @cached_method
        def pulled_back_source_canonical_bundle(self):
            r"""``pi^* omega_{P^2} = O_{P^2 x P^1}(-3, 0)|_B``."""
            return self.pullback_line_bundle(self.blowup_source().canonical_line_bundle())

        @cached_method
        def canonical_comparison(self):
            r"""The isomorphism ``omega_B ~= pi^* omega_{P^2} tensor O_B(E)``.

            Its domain is ``omega_B = O_{P^2 x P^1}(-2, -1)|_B`` and its codomain
            is the tensor product of the pulled-back canonical bundle with the
            exceptional line bundle.
            """
            canonical = self.graph_ambient_product().O(-2, -1).restrict_to(self)
            target = self.pulled_back_source_canonical_bundle().tensor_product(
                self.exceptional_line_bundle()
            )
            return canonical.canonical_isomorphism_to(target)

        def _canonical_line_bundle(self):
            return self.canonical_comparison().domain()

        def _is_del_pezzo(self) -> bool:
            return bool(self.anticanonical_line_bundle().is_ample())

        def _del_pezzo_degree(self):
            r"""``(-K_B)^2 = (3H - E)^2``."""
            anticanonical = (
                3 * self.hyperplane_picard_class()
                - self.exceptional_picard_class()
            )
            return self.picard_intersection_pairing()(
                anticanonical,
                anticanonical,
            )


def _projective_point_blowup(projective_plane, point):
    r"""Return ``Bl_point(P^2)`` from its regular-center Rees graph in ``P^2 x P^1``."""
    base = projective_plane.scheme_base_ring()
    assert base in OwnedFields(), (
        f"the blowup of {projective_plane} at a point is implemented only over a field, but "
        f"its base ring {base} is not a field"
    )
    assert projective_plane in ProjectiveSpaces(base) and int(projective_plane.relative_dimension()) == 2, (
        f"the blowup at a point is implemented only for the projective plane P^2, but "
        f"{projective_plane} is not P^2 over {base}"
    )
    assert point.codomain() is projective_plane and point.domain() is projective_plane.base_scheme(), (
        f"the blowup center {point} must be a rational point Spec {base} -> {projective_plane}, "
        f"but it is a morphism {point.domain()} -> {point.codomain()}"
    )

    direction = ProjectiveSpaces(base)(1, names=("U", "V"))
    product = projective_plane.scheme_category().product((projective_plane, direction))
    graph_sections = product.O(1, 1).global_sections()
    source_embedding = graph_sections.factor_coordinate_embedding(0)
    direction_embedding = graph_sections.factor_coordinate_embedding(1)
    source_ring = source_embedding.domain()
    source_labels = tuple(source_ring.algebra_generating_set())
    coordinates = tuple(point.point_coordinates())
    nonzero = tuple(index for index, coordinate in enumerate(coordinates) if coordinate != base.zero())
    assert nonzero, (
        f"the point {point} has all coordinates {coordinates} zero, so it is not a point of "
        f"{projective_plane}"
    )
    pivot = nonzero[0]
    scalar_map = source_ring.algebra_structure_morphism()
    pivot_variable = source_ring.algebra_generator(source_labels[pivot])
    center_equations = tuple(
        scalar_map(coordinates[pivot]) * source_ring.algebra_generator(source_labels[index])
        - scalar_map(coordinates[index]) * pivot_variable
        for index in range(3)
        if index != pivot
    )
    center = projective_plane.closed_subscheme(center_equations)
    f, g = center_equations

    direction_ring = direction_embedding.domain()
    direction_labels = tuple(direction_ring.algebra_generating_set())
    U = direction_ring.algebra_generator(direction_labels[0])
    V = direction_ring.algebra_generator(direction_labels[1])
    graph_relation = (
        source_embedding(f) * direction_embedding(V)
        - source_embedding(g) * direction_embedding(U)
    )
    return product.closed_subscheme(
        graph_relation,
        placements=(ProjectivePointBlowups(base),),
        blowup_point=point,
        blowup_source=projective_plane,
        blowup_center=center,
        graph_section_space=graph_sections,
    )


__all__ = [
    "Blowups",
    "ProjectivePointBlowups",
]
