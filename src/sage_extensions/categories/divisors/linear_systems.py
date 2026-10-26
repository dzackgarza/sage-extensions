r"""Complete linear systems represented by their section spaces."""

from itertools import product as cartesian_product
from math import comb

from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.algebras.algebras import (
    AlgebrasWithChosenFinitePresentation,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.schemes.schemes import (
    ProductProjectiveSpaces,
    ProjectiveSpaces,
    Schemes,
    _projective_space,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets


class CompleteLinearSystems(OwnedCategoryOverBaseRing):
    r"""Complete linear systems ``|D|``: the linear system of all of ``H^0(X, O_X(D))``.

    A complete linear system is the linear system whose section subspace is
    the whole space, ``W = H^0(X, O_X(D))`` with ``i = id``.  This level adds
    the scheme ``X`` and the divisor ``D``; the section space, its lines and
    their quotient-convention realization are those of the general linear
    system.
    """

    def an_object(self):
        r"""The hyperplane system on the toric projective line over the base ring."""
        from sage_extensions.categories.schemes.toric.toric_schemes import ToricSchemes

        projective_line = ToricSchemes(self.base_ring()).an_object()
        return projective_line.complete_linear_system(projective_line.hyperplane_divisor())

    def _repr_object_names(self):
        return f"complete linear systems over {self.base_ring()}"

    def super_categories(self):
        return [ProjectiveLinearSystems(self.base_ring())]

    class ParentMethods:
        def __init__(self, linear_system_scheme, linear_system_divisor, **rest) -> None:
            self._linear_system_scheme = linear_system_scheme
            self._linear_system_divisor = linear_system_divisor
            super().__init__(**rest)

        def linear_system_scheme(self):
            return self._linear_system_scheme

        def linear_system_divisor(self):
            return self._linear_system_divisor

        def section_space(self):
            r"""``H^0(X, O_X(D))``, which is the whole section space of this system."""
            return self.ambient_section_space()

        def complete_linear_system(self):
            r"""A complete linear system is its own completion."""
            return self

        def associated_morphism(self):
            r"""Return the map defined by this complete linear system when basepoint-free."""
            return self.linear_system_scheme().associated_projective_morphism(
                self.linear_system_divisor()
            )


class HomogeneousPolynomialSectionSpaces(OwnedCategoryOverBaseRing):
    r"""Degree-\(d\) homogeneous polynomial section spaces \(H^0(\mathbb{P}^n_R, \mathcal{O}(d))\).

    For a commutative ring \(R\) and \(S = R[x_0, \dots, x_n]\) graded by total
    degree, \(\Gamma(\mathbb{P}^n_R, \mathcal{O}(d)) \cong S_d\), the degree-\(d\)
    homogeneous piece, for every \(d \in \mathbb{Z}\), and \(S_d = 0\) for
    \(d < 0\) (Hartshorne, Proposition II.5.13).  \(S_d\) is a free \(R\)-module:
    the monomials \(x^a\) with \(|a| = d\) give the chosen framing
    \(R^{(\{x^a\})} \cong S_d\).  So an object is a framed free module in
    ``Modules(R)`` over any \(R\).  The free-module level
    consumes the monomials; this level adds the projective scheme \(X\), the
    degree \(d\), the graded coordinate algebra \(S\) whose degree-\(d\) piece
    this is, and the exponent vector of each monomial.
    """

    def _repr_object_names(self):
        return f"homogeneous polynomial section spaces over {self.base_ring()}"

    def an_object(self):
        r"""The linear forms on the projective line over the base ring."""
        return ProjectiveSpaces(self.base_ring()).an_object().O(1).global_sections()

    def super_categories(self):
        r"""The monomial basis is a chosen framing of a free module over the same ring."""
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        return [FramedFreeModules(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            section_scheme,
            homogeneous_degree,
            homogeneous_coordinate_ring,
            monomial_exponents,
            **rest,
        ) -> None:
            self._section_scheme = section_scheme
            self._homogeneous_degree = homogeneous_degree
            self._homogeneous_coordinate_ring = homogeneous_coordinate_ring
            self._monomial_exponents = dict(monomial_exponents)
            super().__init__(**rest)

        def section_scheme(self):
            r"""The projective scheme whose sections these are."""
            return self._section_scheme

        def homogeneous_degree(self):
            r"""The degree \(d\) of the homogeneous polynomials."""
            return self._homogeneous_degree

        def homogeneous_coordinate_ring(self):
            r"""The homogeneous coordinate algebra whose monomials frame this space."""
            return self._homogeneous_coordinate_ring

        def monomial_exponents(self, monomial):
            r"""The exponent vector of the framing monomial ``monomial``."""
            return self._monomial_exponents[monomial]

        def homogeneous_polynomial(self, section):
            r"""Return the homogeneous polynomial represented by ``section``."""
            section = self(section)
            coordinates = self._framing_lift(self(section))
            ring = self.homogeneous_coordinate_ring()
            scalar_map = ring.algebra_structure_morphism()
            return sum(
                (
                    scalar_map(coordinates(monomial)) * monomial
                    for monomial in coordinates.support().domain()
                ),
                ring.zero(),
            )

        def section_from_homogeneous_polynomial(self, polynomial):
            r"""Return the section represented by one homogeneous polynomial of this degree."""
            ring = self.homogeneous_coordinate_ring()
            polynomial = ring(polynomial)
            backend = _engine_element(ring, polynomial)
            engine = _engine_ring(ring)
            base = self.base_ring()
            engine_base = _engine_ring(base)
            by_exponents = {
                tuple(self.monomial_exponents(monomial)): monomial
                for monomial in self.module_generating_set()
            }
            # The engine keys a univariate polynomial by its degree and a
            # multivariate one by its exponent tuple; the number of homogeneous
            # coordinates selects which representation the coordinate algebra has.
            univariate = int(ring.algebra_generating_set().cardinality()) == 1
            coefficients = {}
            for exponent, coefficient in engine(backend).monomial_coefficients().items():
                powers = (
                    (int(exponent),)
                    if univariate
                    else tuple(int(value) for value in exponent)
                )
                assert powers in by_exponents, (
                    f"{polynomial} is not homogeneous of degree {self.homogeneous_degree()}: it has a "
                    f"monomial with exponents {powers}, so it is not a section of O({self.homogeneous_degree()})"
                )
                coefficients[by_exponents[powers]] = _owned_engine_element(base,
                    engine_base(coefficient)
                )
            return self.linear_combination(coefficients)

        def pullback(self, morphism):
            r"""Pull homogeneous sections back along a represented product projection.

            If ``pi_i : prod_j P_j -> P_i``, a degree-``d`` monomial keeps its
            exponent vector in the ``i``-th block and has exponent zero in all
            other blocks.  This is the section map underlying
            ``pi_i^* O(d) = O(0,...,d,...,0)``.
            """
            source_scheme = self.section_scheme()
            assert morphism.codomain() is source_scheme, (
                f"cannot pull back sections of O({self.homogeneous_degree()}) on {source_scheme} along "
                f"{morphism}: its codomain is {morphism.codomain()}, not {source_scheme}"
            )
            pulled_bundle = source_scheme.O(self.homogeneous_degree()).pullback(morphism)
            target = pulled_bundle.global_sections()
            product = morphism.domain()
            label = product.projection_label(morphism)
            labels = tuple(product.factors().index_set())
            label = product.factors().index_set()(label)
            target_by_exponents = {
                tuple(tuple(block) for block in target.monomial_exponents(monomial)): monomial
                for monomial in target.module_generating_set()
            }

            def target_exponents(monomial):
                selected = tuple(self.monomial_exponents(monomial))
                blocks = []
                for factor_label in labels:
                    factor = product.factors()[factor_label]
                    width = int(factor.relative_dimension()) + 1
                    blocks.append(selected if factor_label == label else (0,) * width)
                return tuple(blocks)

            return self.module_category().Mor(self, target)(
                {
                    monomial: target.module_generator(
                        target_by_exponents[target_exponents(monomial)]
                    )
                    for monomial in self.module_generating_set()
                }
            )

        def pullback_by_projective_automorphism(self, morphism):
            r"""Return ``morphism^*:H^0(P,O(d))->H^0(P,O(d))`` by homogeneous substitution.

            The retained projective-coordinate morphism gives one linear
            homogeneous coordinate for each target coordinate.  Substitution
            is therefore an endomorphism of the owned homogeneous coordinate
            algebra, and restricting it to the degree-``d`` piece is the
            contravariant pullback on sections.
            """
            scheme = self.section_scheme()
            assert morphism.domain() is scheme and morphism.codomain() is scheme, (
                f"cannot pull back sections on {scheme} along {morphism}: it is a morphism "
                f"{morphism.domain()} -> {morphism.codomain()}, not an automorphism of {scheme}"
            )
            coordinates = tuple(morphism.homogeneous_coordinates())
            ring = self.homogeneous_coordinate_ring()
            labels = tuple(ring.algebra_generating_set())
            assert len(coordinates) == len(labels), (
                f"{morphism} is given by {len(coordinates)} homogeneous coordinates, but {scheme} has "
                f"{len(labels)}: an automorphism of projective space has one coordinate per variable"
            )
            assert all(coordinate.parent() is ring for coordinate in coordinates), (
                f"the coordinates {coordinates} of {morphism} are not all polynomials in the homogeneous "
                f"coordinate ring {ring} of {scheme}"
            )
            substitution = ring.Mor(ring)(
                {label: coordinate for label, coordinate in zip(labels, coordinates, strict=True)}
            )
            return self.module_category().Mor(self, self)(
                {
                    monomial: self.section_from_homogeneous_polynomial(
                        substitution(self.homogeneous_polynomial(self.module_generator(monomial)))
                    )
                    for monomial in self.module_generating_set()
                }
            )


class MultihomogeneousPolynomialSectionSpaces(OwnedCategoryOverBaseRing):
    r"""Multihomogeneous section spaces \(H^0(\prod_i \mathbb{P}^{n_i}, \mathcal{O}(d_1, \dots, d_r))\).

    An object is the free module on the monomials of multidegree
    \((d_1, \dots, d_r)\) of the coordinate algebra of a product of projective
    spaces.  The free-module level consumes the monomials; this level adds the
    product, the multidegree, the coordinate algebra, the exponent blocks of
    each monomial, and the variable block of each factor.
    """

    def _repr_object_names(self):
        return f"multihomogeneous polynomial section spaces over {self.base_ring()}"

    def an_object(self):
        r"""The bidegree-(1,1) sections on a product of two projective lines."""
        return ProductProjectiveSpaces(self.base_ring()).an_object().O(1, 1).global_sections()

    def super_categories(self):
        r"""The monomial basis is a chosen framing of a free module over the same ring."""
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        return [FramedFreeModules(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            section_scheme,
            multidegree,
            homogeneous_coordinate_ring,
            monomial_exponents,
            coordinate_blocks,
            **rest,
        ) -> None:
            self._section_scheme = section_scheme
            self._multidegree = multidegree
            self._homogeneous_coordinate_ring = homogeneous_coordinate_ring
            self._monomial_exponents = dict(monomial_exponents)
            self._coordinate_blocks = coordinate_blocks
            super().__init__(**rest)

        def section_scheme(self):
            r"""The product of projective spaces whose sections these are."""
            return self._section_scheme

        def multidegree(self):
            r"""The multidegree, indexed by the factors of the product."""
            return self._multidegree

        def homogeneous_coordinate_ring(self):
            r"""The multihomogeneous coordinate algebra whose monomials frame this space."""
            return self._homogeneous_coordinate_ring

        def monomial_exponents(self, monomial):
            r"""The exponent blocks, one per factor, of the framing monomial ``monomial``."""
            return self._monomial_exponents[monomial]

        def coordinate_block(self, position):
            r"""The variable range ``(start, stop)`` of the factor at ``position``."""
            return self._coordinate_blocks[position]

        @cached_method
        def factor_coordinate_embedding(self, factor_label):
            r"""Embed one factor's homogeneous coordinate algebra into the product algebra.

            This is the polynomial-algebra map induced by the inclusion of the
            factor's coordinate variables into its exact variable block.  The
            product's retained factor labels, rather than factor equality, select
            the block, so repeated projective factors keep distinct roles.
            """
            product = self.section_scheme()
            factors = product.factors()
            indices = factors.index_set()
            factor_label = indices(factor_label)
            labels = tuple(indices)
            position = next(
                index for index, known in enumerate(labels) if known == factor_label
            )
            factor = factors[factor_label]
            source = factor.O(1).global_sections().homogeneous_coordinate_ring()
            target = self.homogeneous_coordinate_ring()
            start, stop = self.coordinate_block(position)
            source_labels = tuple(source.algebra_generating_set())
            target_labels = tuple(target.algebra_generating_set())
            assert stop - start == len(source_labels), (
                f"the coordinate block {start}..{stop} of factor {factor_label} in {product} has "
                f"{stop - start} variables, but the factor {factor} has {len(source_labels)} homogeneous "
                "coordinates"
            )
            return source.Mor(target)(
                {
                    source_label: target.algebra_generator(target_labels[start + offset])
                    for offset, source_label in enumerate(source_labels)
                }
            )


class ProjectiveLinearSystems(OwnedCategoryOverBaseRing):
    r"""Linear systems: the projective space of lines of ``W`` for ``i: W -> H^0(X, L)``.

    A linear system on a scheme ``X`` is a submodule ``W`` of the global
    sections of an invertible sheaf ``L``; its points are the lines of ``W``.
    This level adds the inclusion ``i``, from which ``W`` is its domain and
    ``H^0(X, L)`` its codomain.  The complete linear system ``|L|`` is the case
    ``W = H^0(X, L)``, and a linear system with imposed multiplicity is the case
    ``W = ker(H^0(X, L) -> J)`` for a jet evaluation; both specialize this one.
    """

    def _repr_object_names(self):
        return f"projective linear systems over {self.base_ring()}"

    def an_object(self):
        r"""The complete projective linear system of O(1) on the projective line."""
        return ProjectiveSpaces(self.base_ring()).an_object().O(1).linear_system()

    def super_categories(self):
        return [ProjectiveSpaces(self.base_ring())]

    class ParentMethods:
        def __init__(self, section_embedding, **rest) -> None:
            self._section_embedding = section_embedding
            super().__init__(**rest)

        def line_bundle(self):
            r"""``L``, for sections that are homogeneous polynomials: ``O(d)`` on ``P^n``."""
            sections = self.ambient_section_space()
            assert sections in HomogeneousPolynomialSectionSpaces(self.base_ring()), (
                "line_bundle on ProjectiveLinearSystems(R) whose sections are not homogeneous "
                f"polynomials on a projective space, such as {sections}: not implemented"
            )
            return sections.section_scheme().O(sections.homogeneous_degree())

        def ambient_section_space(self):
            return self.section_embedding().codomain()

        @cached_method
        def complete_linear_system(self):
            r"""Return ``|L|``, the linear system of all of ``H^0(X, L)``."""
            return self.line_bundle().linear_system()

        def projective_dimension(self):
            return self.relative_dimension()

        def selected_section_space(self):
            return self.section_embedding().domain()

        def section_embedding(self):
            return self._section_embedding

        def selected_sections(self):
            embedding = self.section_embedding()
            source = self.selected_section_space()
            return indexed_family(
                source.module_generating_set(),
                lambda label: embedding(source.module_generator(label)),
                name="Selected sections of the linear system",
            )

        @cached_method
        def quotient_projectivization(self):
            r"""Return the quotient-convention realization of the selected lines.

            This projective linear system parametrizes lines in its selected
            section subspace V.  With the repository's quotient convention
            that is P_quot(V^*), not P_quot(V).
            """
            return self.selected_section_space().dual_module().projectivization()

        @cached_method
        def quotient_projectivization_comparison(self):
            r"""Return the chartwise isomorphism from P_quot(V^*) to this system."""
            projectivization = self.quotient_projectivization().arrow().domain()
            return projectivization.projective_space_comparison(self)

        def closed_immersion_into_complete_linear_system(self):
            r"""Return the closed immersion of this system into ``|L| = P(H^0(X, L)^*)``.

            The selected subspace ``i: W -> H^0(X, L)`` dualizes to the surjection
            ``i^*: H^0(X, L)^* -> W^*``, and a surjection ``E -> F`` of quasi-coherent
            sheaves induces the closed immersion ``P(F) -> P(E)`` that sends a rank-one
            quotient of ``F`` to its composite with ``E -> F`` (EGA II, 4.1.2).  The
            lines of ``W`` are therefore a linear subspace of the lines of
            ``H^0(X, L)``, and the immersion is an element of ``self.Mor(|L|)``.

            In coordinates, the homogeneous coordinate ``x_j`` of this system is
            the ``j``-th basis vector ``w_j`` of ``W`` and that of ``|L|`` is the
            ``m``-th framing vector ``v_m`` of ``H^0(X, L)``.  The line spanned by
            ``sum_j a_j w_j`` goes to the line spanned by ``sum_j a_j i(w_j)``,
            whose ``m``-th coordinate is the linear form
            ``sum_j v_m^*(i(w_j)) x_j``, with ``v_m^*`` the dual basis.  Since
            ``i`` is injective these forms have no common zero.
            """
            complete = self.complete_linear_system()
            embedding = self.section_embedding()
            selected = self.selected_section_space()
            sections = self.ambient_section_space()
            linear_forms = self.O(1).global_sections()
            variable = {
                tuple(linear_forms.monomial_exponents(monomial)).index(1): monomial
                for monomial in linear_forms.module_generating_set()
            }
            images = tuple(
                embedding(selected.module_generator(label))
                for label in selected.module_generating_set()
            )
            dual_basis = sections.dual_basis()
            coordinates = tuple(
                linear_forms.homogeneous_polynomial(
                    linear_forms.linear_combination(
                        {
                            variable[position]: dual_basis[label](image)
                            for position, image in enumerate(images)
                        }
                    )
                )
                for label in sections.module_generating_set()
            )
            return self.projective_morphism_from_coordinates(complete, coordinates)

        def restriction_map(self, closed_subscheme):
            return _projective_section_restriction(
                self.line_bundle(),
                closed_subscheme,
                source=self.selected_section_space(),
                into_complete=self.section_embedding(),
            )

        @cached_method
        def base_locus(self):
            r"""The common zero locus of the sections of ``W`` in ``X``."""
            sections = self.ambient_section_space()
            assert sections in HomogeneousPolynomialSectionSpaces(self.base_ring()), (
                "base_locus on ProjectiveLinearSystems(R) whose sections are not homogeneous "
                f"polynomials on a projective space, such as {sections}: not implemented"
            )
            return sections.section_scheme().closed_subscheme(
                tuple(
                    sections.homogeneous_polynomial(section)
                    for section in self.selected_sections()
                )
            )

        def is_basepoint_free(self) -> bool:
            return self.base_locus().is_empty()

        @cached_method
        def domain_of_definition(self):
            if self.is_basepoint_free():
                return self.line_bundle().scheme()
            return self.base_locus().open_complement()

        @cached_method
        def associated_morphism(self):
            domain = self.domain_of_definition()
            source_sections = self.ambient_section_space()
            coordinates = tuple(
                source_sections.homogeneous_polynomial(section)
                for section in self.selected_sections()
            )
            return domain.projective_morphism_from_coordinates(self, coordinates)


class ProjectiveJetSpaces(OwnedCategoryOverBaseRing):
    r"""Finite local jet realizations ``O(d)_p / m_p^r O(d)_p`` on projective space.

    An object is the free module on the centered monomials of total degree
    below \(r\) in an affine chart containing \(p\), realizing
    \(\mathcal{O}(d)_p / \mathfrak{m}_p^r \mathcal{O}(d)_p\).  The free-module
    level consumes the monomials; this level adds the line bundle, the order
    \(r\), the point, the chart, the point of the chart's spectrum, and the
    local quotient \(\mathcal{O}_{\mathbb{P},p}/\mathfrak{m}_p^r\).
    """

    def _repr_object_names(self):
        return f"projective jet spaces over {self.base_ring()}"

    def an_object(self):
        r"""The first jet of O(1) at a coordinate point of the projective line."""
        projective_line = ProjectiveSpaces(self.base_ring()).an_object()
        return projective_line.coordinate_point_jet_evaluation(1, 0, 1).codomain()

    def super_categories(self):
        r"""The monomial basis is a chosen framing of a free module over the same ring."""
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        return [FramedFreeModules(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            jet_line_bundle,
            jet_order,
            jet_point,
            jet_affine_chart,
            jet_spectrum_point,
            jet_local_quotient,
            **rest,
        ) -> None:
            self._jet_line_bundle = jet_line_bundle
            self._jet_order = jet_order
            self._jet_point = jet_point
            self._jet_affine_chart = jet_affine_chart
            self._jet_spectrum_point = jet_spectrum_point
            self._jet_local_quotient = jet_local_quotient
            super().__init__(**rest)

        def jet_line_bundle(self):
            return self._jet_line_bundle

        def jet_projective_space(self):
            return self.jet_line_bundle().projective_space()

        def jet_homogeneous_degree(self):
            return self.jet_line_bundle().degree()

        def jet_order(self):
            return self._jet_order

        def jet_point(self):
            return self._jet_point

        def jet_affine_chart(self):
            return self._jet_affine_chart

        def jet_spectrum_point(self):
            return self._jet_spectrum_point

        def jet_local_quotient(self):
            return self._jet_local_quotient

        def jet_stalk(self):
            r"""The local ring \(\mathcal{O}_{\mathbb{P},p}\) the jet quotient is taken of."""
            return self.jet_local_quotient().quotient_source()

        def jet_maximal_ideal(self):
            return self.jet_stalk().maximal_ideal()

        def jet_residue_field(self):
            return self.jet_spectrum_point().residue_field()

        def jet_coordinate_index(self):
            coordinates = tuple(self.jet_point().point_coordinates())
            nonzero = tuple(
                index
                for index, coordinate in enumerate(coordinates)
                if coordinate != self.base_ring().zero()
            )
            assert len(nonzero) == 1, (
                f"the point {coordinates} is not a coordinate point: it has {len(nonzero)} nonzero "
                "homogeneous coordinates, and a coordinate point has exactly one"
            )
            return nonzero[0]


class ImposedMultiplicityLinearSystems(OwnedCategoryOverBaseRing):
    r"""Linear systems of the sections vanishing to order ``r`` at a point ``p``.

    For the jet evaluation ``e: H^0(X, L) -> L_p / m_p^r L_p`` this is the
    linear system with ``W = ker(e)`` and ``i`` the kernel inclusion.  This
    level adds ``e``.
    """

    def _repr_object_names(self):
        return f"linear systems with imposed multiplicity over {self.base_ring()}"

    def an_object(self):
        r"""Sections of O(1) on the projective line vanishing at one coordinate point."""
        projective_line = ProjectiveSpaces(self.base_ring()).an_object()
        return projective_line.imposed_multiplicity_linear_system(1, 0, 1)

    def super_categories(self):
        return [ProjectiveLinearSystems(self.base_ring())]

    class ParentMethods:
        def __init__(self, jet_evaluation, **rest) -> None:
            self._jet_evaluation = jet_evaluation
            super().__init__(**rest)

        def constrained_section_space(self):
            r"""``ker(e)``, the section subspace of this linear system."""
            return self.selected_section_space()

        def imposed_jet_evaluation(self):
            return self._jet_evaluation

        def imposed_vanishing_order(self):
            return self.imposed_jet_evaluation().codomain().jet_order()


def _weak_compositions(total, length):
    if length == 0:
        if total == 0:
            yield ()
        return
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in _weak_compositions(total - first, length - 1):
            yield (first, *tail)


def _homogeneous_polynomial_section_space(projective_scheme, degree, *, coordinate_names=None):
    r"""Return the degree-``d`` homogeneous piece ``S_d`` of ``S = R[x_0..x_n]`` on ``P^n_R``.

    Basis labels are the actual monomials in an owned homogeneous-coordinate
    polynomial algebra, not anonymous positions.  No monomial has negative
    total degree, so for ``d < 0`` the piece is the zero module on the empty
    framing.
    """
    base = projective_scheme.scheme_base_ring()
    degree = int(degree)
    width = int(projective_scheme.relative_dimension()) + 1
    names = (
        tuple(f"x{index}" for index in range(width))
        if coordinate_names is None
        else tuple(coordinate_names)
    )
    assert len(names) == width, (
        f"{len(names)} coordinate names {names} were given for {projective_scheme}, which has "
        f"relative dimension {width - 1} and so {width} homogeneous coordinates"
    )
    ring = base.polynomial_ring(names)
    labels = tuple(ring.algebra_generating_set())
    monomials = []
    exponent_data = {}
    for exponents in _weak_compositions(degree, width) if degree >= 0 else ():
        monomial = ring.one()
        for position, exponent in enumerate(exponents):
            if exponent:
                monomial *= ring.algebra_generator(labels[position]) ** exponent
        monomials.append(monomial)
        exponent_data[monomial] = exponents
    return base._fresh_free_module_on(
        finite_ordered_set(tuple(monomials)),
        _extra_categories=(HomogeneousPolynomialSectionSpaces(base),),
        _extra_construction_data={
            "section_scheme": projective_scheme,
            "homogeneous_degree": degree,
            "homogeneous_coordinate_ring": ring,
            "monomial_exponents": exponent_data,
        },
    )


def _multihomogeneous_polynomial_section_space(projective_product, degrees):
    r"""Return ``H^0(prod P^{n_i}, O(d_1, ..., d_r))`` for any integer multidegree.

    ``degrees`` is the multidegree as a family indexed by the product's own
    factor index set.  Basis labels are the actual multihomogeneous monomials
    in one owned polynomial coordinate algebra, so repeated isomorphic factors
    keep distinct roles.  By the Kuenneth formula the space is the tensor
    product of the ``H^0(P^{n_i}, O(d_i))``, and a factor with ``d_i < 0`` has no
    sections (Hartshorne, Proposition II.5.13), so a negative degree gives the
    zero module on the empty framing.
    """
    base = projective_product.scheme_base_ring()
    assert projective_product in ProductProjectiveSpaces(base), (
        f"{projective_product} is not a product of projective spaces over {base}, so it has no "
        "space of multihomogeneous polynomials"
    )
    factors = projective_product.factors()
    factor_indices = factors.index_set()
    factor_labels = tuple(factor_indices)
    assert degrees.index_set() is factor_indices, (
        f"the multidegree {degrees} is indexed by {degrees.index_set()}, but the factors of "
        f"{projective_product} are indexed by {factor_indices}"
    )
    degree_values = tuple(_owned_integers()(degrees[label]) for label in factor_labels)
    multidegree = finite_indexed_family(
        factor_indices,
        lambda label: degree_values[
            next(
                position
                for position, known_label in enumerate(factor_labels)
                if known_label == label
            )
        ],
        name="Projective multidegree",
    )
    widths = tuple(
        int(factors[label].relative_dimension()) + 1
        for label in factor_labels
    )
    coordinate_names = tuple(
        f"x{factor_position}_{coordinate}"
        for factor_position, width in enumerate(widths)
        for coordinate in range(width)
    )
    ring = base.polynomial_ring(coordinate_names)
    ring_labels = tuple(ring.algebra_generating_set())
    block_offsets = []
    offset = 0
    for width in widths:
        block_offsets.append((offset, offset + width))
        offset += width

    monomials = []
    exponent_data = {}
    block_exponents = tuple(
        tuple(_weak_compositions(int(degree), width)) if degree >= 0 else ()
        for degree, width in zip(degree_values, widths, strict=True)
    )
    for blocks in cartesian_product(*block_exponents):
        flat = tuple(power for block in blocks for power in block)
        monomial = ring.one()
        for position, exponent in enumerate(flat):
            if exponent:
                monomial *= ring.algebra_generator(ring_labels[position]) ** exponent
        monomials.append(monomial)
        exponent_data[monomial] = tuple(tuple(block) for block in blocks)

    return base._fresh_free_module_on(
        finite_ordered_set(tuple(monomials)),
        _extra_categories=(MultihomogeneousPolynomialSectionSpaces(base),),
        _extra_construction_data={
            "section_scheme": projective_product,
            "multidegree": multidegree,
            "homogeneous_coordinate_ring": ring,
            "monomial_exponents": exponent_data,
            "coordinate_blocks": tuple(block_offsets),
        },
    )


def _coordinate_hyperplane_section_restriction(projective_space, degree, coordinate_index):
    r"""Restrict degree-``d`` sections of ``P^n`` to ``x_i=0``.

    This is the exact map ``H^0(P^n,O(d)) -> H^0(P^{n-1},O(d))`` for the
    coordinate hyperplane.  The kernel is the forms divisible by ``x_i`` and
    the map is surjective for ``d >= 0``.
    """
    degree = int(degree)
    coordinate_index = int(coordinate_index)
    dimension = int(projective_space.relative_dimension())
    assert dimension >= 1, (
        f"{projective_space} has relative dimension {dimension}, so it has no coordinate "
        "hyperplane: this requires dimension at least 1"
    )
    assert 0 <= coordinate_index <= dimension, (
        f"coordinate index {coordinate_index} is out of range for {projective_space}, whose "
        f"homogeneous coordinates are x0, ..., x{dimension}"
    )
    source_names = tuple(f"x{index}" for index in range(dimension + 1))
    source = _homogeneous_polynomial_section_space(
        projective_space,
        degree,
        coordinate_names=source_names,
    )
    equation = tuple(projective_space.homogeneous_coordinate_generators())[coordinate_index]
    hyperplane = projective_space.hypersurface(equation)
    target_names = tuple(
        name for index, name in enumerate(source_names) if index != coordinate_index
    )
    target = _homogeneous_polynomial_section_space(
        hyperplane,
        degree,
        coordinate_names=target_names,
    )
    target_by_exponents = {
        tuple(target.monomial_exponents(monomial)): monomial
        for monomial in target.module_generating_set()
    }

    def image(monomial):
        exponents = source.monomial_exponents(monomial)
        if exponents[coordinate_index]:
            return target.zero()
        restricted = exponents[:coordinate_index] + exponents[coordinate_index + 1 :]
        return target.module_generator(target_by_exponents[restricted])

    return source.module_category().Mor(source, target)(
        {
            monomial: image(monomial)
            for monomial in source.module_generating_set()
        }
    )


def _projective_section_restriction(
    line_bundle,
    closed_subscheme,
    *,
    source=None,
    into_complete=None,
):
    r"""Restrict a represented section space to a projective closed subscheme.

    The codomain is the exact image of the selected source under restriction,
    not an assertion that the homogeneous coordinate quotient computes all of
    ``H^0(Z,L|_Z)``.  The closed subscheme's homogeneous equations define a
    chosen quotient of the homogeneous coordinate algebra.  Canonical normal
    forms in that quotient supply a finite ambient monomial space, and the
    module image construction corestricts to the true restriction image.
    """
    scheme = line_bundle.projective_space()
    assert closed_subscheme.inclusion().codomain() is scheme, (
        f"cannot restrict sections of {line_bundle} to {closed_subscheme}: it is a closed "
        f"subscheme of {closed_subscheme.inclusion().codomain()}, not of {scheme}"
    )
    base = scheme.scheme_base_ring()
    assert base in OwnedFields(), (
        f"cannot compute the restriction of sections of {line_bundle} to {closed_subscheme}: "
        f"the base ring {base} is not a field, and this computation requires a field"
    )
    complete = line_bundle.global_sections()
    source = complete if source is None else source
    if source is complete:
        into_complete = complete.module_category().Mor(complete, complete).identity()
    assert into_complete is not None, (
        f"the section space {source} is not the space of all global sections of {line_bundle}, "
        "so its inclusion into that space must be given"
    )
    assert into_complete.domain() is source and into_complete.codomain() is complete, (
        f"{into_complete} is a map {into_complete.domain()} -> {into_complete.codomain()}, not the "
        f"inclusion {source} -> {complete} of sections of {line_bundle}"
    )

    coordinate_ring = complete.homogeneous_coordinate_ring()
    equations = closed_subscheme.homogeneous_defining_equations(coordinate_ring)
    quotient = AlgebrasWithChosenFinitePresentation(base)(
        coordinate_ring,
        tuple(equations),
    )

    source_labels = source.module_generating_set()
    assert source_labels.is_finite() is True, (
        f"computing the restriction image of {source} needs a selected finite "
        "section generating family"
    )
    normal_forms = indexed_family(
        source_labels,
        lambda label: quotient.presentation_normal_form_terms(
            quotient(complete.homogeneous_polynomial(
                into_complete(source.module_generator(label))
            ))
        ),
        name="Selected presentation coefficients of restricted sections",
    )
    monomial_labels = finite_ordered_set(())
    for coordinates in normal_forms:
        monomial_labels = monomial_labels.union(coordinates.support().domain())

    ambient = base._fresh_free_module_on(monomial_labels)
    ambient_map = source.module_category().Mor(source, ambient)(
        indexed_family(
            source_labels,
            lambda label: sum(
                (ambient.scalar_multiple(
                    normal_forms[label](monomial_label),
                    ambient.module_generator(monomial_label),
                ) for monomial_label in normal_forms[label].support().domain()),
                ambient.zero(),
            ),
            name="Restriction images in the selected monomial coefficient module",
        )
    )
    image = ambient_map.image()
    restriction_images = {
        label: image.inclusion().lift(
            ambient_map(source.module_generator(label))
        )
        for label in source.module_generating_set()
    }
    return source.module_category().Mor(source, image)(
        restriction_images,
        projective_section_restriction_data={
            "line_bundle": line_bundle,
            "closed_subscheme": closed_subscheme,
            "coordinate_quotient": quotient,
            "ambient_normal_form_space": ambient,
            "image_inclusion": image.inclusion(),
        },
    )


def _projective_linear_system(line_bundle, sections):
    r"""Return the projective linear system spanned by independent sections of ``line_bundle``."""
    scheme = line_bundle.projective_space()
    ambient = line_bundle.global_sections()
    base = scheme.scheme_base_ring()
    sections = tuple(ambient(section) for section in sections)
    assert sections, (
        f"no sections of {line_bundle} were given: a linear system is the projectivization "
        "of a nonzero space of sections"
    )
    labels = Sets.Δ[len(sections) - 1]
    selected = base._fresh_free_module_on(labels)
    images = {
        label: sections[int(labels.ranking_map()(label))]
        for label in labels
    }
    selected_map = selected.module_category().Mor(selected, ambient)(images)
    assert int(selected_map.kernel().dimension()) == 0, (
        f"the sections {sections} of {line_bundle} are linearly dependent over {base}: a linear "
        "system is given by a basis of its space of sections"
    )
    embedding = selected.Mono(ambient)(images)
    return _projective_space(
        base,
        len(sections) - 1,
        None,
        (ProjectiveLinearSystems(base),),
        section_embedding=embedding,
    )


def _centered_jet_basis(base, dimension, jet_order):
    names = tuple(f"v{index}" for index in range(dimension))
    ring = base.polynomial_ring(names)
    labels = tuple(ring.algebra_generating_set())
    monomials = []
    by_exponents = {}
    for total in range(jet_order):
        for exponents in _weak_compositions(total, dimension):
            monomial = ring.one()
            for position, exponent in enumerate(exponents):
                if exponent:
                    monomial *= ring.algebra_generator(labels[position]) ** exponent
            monomials.append(monomial)
            by_exponents[tuple(exponents)] = monomial
    return ring, tuple(monomials), by_exponents


def _projective_point_jet_evaluation(line_bundle, point, jet_order):
    r"""Return ``H^0(P,L) -> L_p / m_p^r L_p`` at a represented rational point.

    The local quotient is the defining object: choose a standard affine chart
    containing ``p``, form its spectrum point, localize to ``O_{P,p}``, and
    quotient by the ``r``-th power of its maximal ideal.  Centered affine
    monomials of total degree below ``r`` give the finite free realization used
    by the section map.  Thus a non-coordinate point changes the evaluation
    coefficients without changing the mathematical jet object.
    """
    projective_space = line_bundle.projective_space()
    base = projective_space.scheme_base_ring()
    assert base in OwnedFields(), (
        f"cannot compute jets of sections of {line_bundle}: the base ring {base} is not a field, "
        "and jet evaluation is computed here only over a field"
    )
    assert point.codomain() is projective_space, (
        f"cannot evaluate jets of {line_bundle} at {point}: it is a point of {point.codomain()}, "
        f"not of {projective_space}"
    )
    assert point.domain() is projective_space.base_scheme(), (
        f"cannot evaluate jets of {line_bundle} at {point}: it is a point over "
        f"{point.domain()}, not a rational point over {projective_space.base_scheme()}; jets "
        "are computed here only at rational points"
    )
    jet_order = int(jet_order)
    assert jet_order >= 1, (
        f"the jet order {jet_order} is not positive: the jet space L_p / m_p^r L_p is taken "
        "for r >= 1"
    )

    coordinates = tuple(point.point_coordinates())
    dimension = int(projective_space.relative_dimension())
    assert len(coordinates) == dimension + 1, (
        f"the point {point} has {len(coordinates)} homogeneous coordinates, but "
        f"{projective_space} has relative dimension {dimension} and so {dimension + 1}"
    )
    pivot = next(
        (index for index, coordinate in enumerate(coordinates) if coordinate != base.zero()),
        None,
    )
    assert pivot is not None, (
        f"the homogeneous coordinates {coordinates} of {point} are all zero, which is not a "
        "point of projective space"
    )
    pivot_inverse = coordinates[pivot].inverse_of_unit()
    affine_values = tuple(
        coordinates[index] * pivot_inverse
        for index in range(dimension + 1)
        if index != pivot
    )

    chart = projective_space.standard_affine_chart(pivot)
    chart_algebra = chart.coordinate_algebra()
    chart_coordinates = tuple(
        projective_space._standard_chart_coordinate(pivot, index)
        for index in range(dimension + 1)
        if index != pivot
    )
    scalar_map = chart_algebra.algebra_structure_morphism()
    point_ideal = chart_algebra.ideal(
        *(
            coordinate - scalar_map(value)
            for coordinate, value in zip(chart_coordinates, affine_values, strict=True)
        )
    )
    spectrum_point = chart.underlying_space()(point_ideal)
    stalk = spectrum_point.local_ring()
    maximal_ideal = stalk.maximal_ideal()
    local_quotient = stalk.quotient_ring(maximal_ideal.power(jet_order))

    _centered_ring, local_monomials, local_by_exponents = _centered_jet_basis(
        base,
        dimension,
        jet_order,
    )
    source = line_bundle.global_sections()
    target = base._fresh_free_module_on(
        finite_ordered_set(local_monomials),
        _extra_categories=(ProjectiveJetSpaces(base),),
        _extra_construction_data={
            "jet_line_bundle": line_bundle,
            "jet_order": _owned_integers()(jet_order),
            "jet_point": point,
            "jet_affine_chart": chart,
            "jet_spectrum_point": spectrum_point,
            "jet_local_quotient": local_quotient,
        },
    )
    nonpivot = tuple(index for index in range(dimension + 1) if index != pivot)

    def image(monomial):
        homogeneous_exponents = source.monomial_exponents(monomial)
        local_powers = tuple(homogeneous_exponents[index] for index in nonpivot)
        coefficients = {}
        choices = tuple(
            range(power + 1)
            for power in local_powers
        )
        for centered_exponents in cartesian_product(*choices):
            if sum(centered_exponents) >= jet_order:
                continue
            coefficient = base.one()
            for power, centered_power, value in zip(
                local_powers,
                centered_exponents,
                affine_values,
                strict=True,
            ):
                coefficient *= base(comb(power, centered_power)) * value ** (
                    power - centered_power
                )
            if coefficient != base.zero():
                coefficients[local_by_exponents[tuple(centered_exponents)]] = coefficient
        return target.linear_combination(coefficients)

    return source.module_category().Mor(source, target)(
        {
            monomial: image(monomial)
            for monomial in source.module_generating_set()
        }
    )


def _coordinate_point_jet_evaluation(projective_space, degree, coordinate_index, jet_order):
    r"""Coordinate-point realization of the projective point-jet evaluation."""
    coordinate_index = int(coordinate_index)
    dimension = int(projective_space.relative_dimension())
    assert 0 <= coordinate_index <= dimension, (
        f"coordinate index {coordinate_index} is out of range for {projective_space}, whose "
        f"homogeneous coordinates are x0, ..., x{dimension}"
    )
    base = projective_space.scheme_base_ring()
    coordinates = tuple(
        base.one() if index == coordinate_index else base.zero()
        for index in range(dimension + 1)
    )
    return _projective_point_jet_evaluation(
        projective_space.O(degree),
        projective_space.point_morphism(coordinates),
        jet_order,
    )


def _imposed_point_multiplicity_linear_system(line_bundle, point, vanishing_order):
    r"""Projectivize sections vanishing to order at least ``r`` at ``point``."""
    evaluation = _projective_point_jet_evaluation(line_bundle, point, vanishing_order)
    kernel = evaluation.kernel()
    dimension = int(kernel.dimension())
    assert dimension != 0, (
        f"no nonzero section of {line_bundle} vanishes to order {vanishing_order} at {point}, "
        "so the linear system is empty and has no projectivization"
    )
    base = line_bundle.projective_space().scheme_base_ring()
    return _projective_space(
        base,
        dimension - 1,
        None,
        (ImposedMultiplicityLinearSystems(base),),
        jet_evaluation=evaluation,
        section_embedding=kernel.inclusion(),
    )


def _coordinate_imposed_multiplicity_linear_system(projective_space, degree, coordinate_index, vanishing_order):
    r"""Coordinate-point realization of the imposed-multiplicity linear system."""
    coordinate_index = int(coordinate_index)
    dimension = int(projective_space.relative_dimension())
    assert 0 <= coordinate_index <= dimension, (
        f"coordinate index {coordinate_index} is out of range for {projective_space}, whose "
        f"homogeneous coordinates are x0, ..., x{dimension}"
    )
    base = projective_space.scheme_base_ring()
    point = projective_space.point_morphism(
        tuple(
            base.one() if index == coordinate_index else base.zero()
            for index in range(dimension + 1)
        )
    )
    return _imposed_point_multiplicity_linear_system(
        projective_space.O(degree),
        point,
        vanishing_order,
    )


def _complete_linear_system(scheme, divisor, section_space):
    r"""Return the complete linear system of ``divisor`` on ``scheme``.

    The represented convention is the projective space of nonzero global
    sections modulo scalars.  Hence a section space of dimension ``r`` gives
    ``P^(r-1)``; the empty section space has no projectivization and is refused.
    """
    base = scheme.scheme_base_ring()
    assert scheme in Schemes(base), (
        f"{scheme} is not a scheme over {base}, so it has no complete linear system |{divisor}|"
    )
    assert section_space.base_ring() is base, (
        f"the space of sections of {divisor} is over {section_space.base_ring()}, but {scheme} is "
        f"over {base}"
    )
    dimension = int(section_space.dimension())
    assert dimension != 0, (
        f"{divisor} has no nonzero global sections on {scheme}, so its complete linear system "
        "is empty and has no projectivization"
    )
    return _projective_space(
        base,
        dimension - 1,
        None,
        (CompleteLinearSystems(base),),
        linear_system_scheme=scheme,
        linear_system_divisor=divisor,
        section_embedding=section_space.Mono(section_space)(
            {
                label: section_space.module_generator(label)
                for label in section_space.module_generating_set()
            }
        ),
    )


__all__ = [
    "CompleteLinearSystems",
    "HomogeneousPolynomialSectionSpaces",
    "ImposedMultiplicityLinearSystems",
    "ProjectiveJetSpaces",
    "ProjectiveLinearSystems",
]
