r"""Section rings of represented divisors and projective line bundles."""

from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.algebras.semigroup_algebras import (
    AffineSemigroupAlgebras,
)
from sage_extensions.categories.modules.pure.modules import BilinearMap
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedIntegralDomains,
    _engine_element,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.set_categories import NN


class SectionRings(OwnedCategoryOverBaseRing):
    r"""Section rings \(R(X, L) = \bigoplus_{n \ge 0} H^0(X, L^{\otimes n})\).

    An object is a nonnegatively graded algebra presented as an affine
    semigroup algebra.  The algebra levels consume the presentation; this
    level adds the scheme \(X\) and the line bundle \(L\) the ring is stated
    on, given either as \(L\) itself or as a Cartier divisor \(D\) with
    \(L = \mathcal{O}_X(D)\).
    """

    def an_object(self):
        r"""The section ring of O(1) on the projective line over the base ring."""
        from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

        return ProjectiveSpaces(self.base_ring()).an_object().O(1).section_ring()

    def super_categories(self):
        return [GradedAlgebras(self.base_ring(), NN)]

    def _repr_object_names(self):
        return f"section rings over {self.base_ring()}"

    def _call_(self, source, divisor=None):
        r"""\(R(X, L)\) for a line bundle ``source``, or \(R(X, \mathcal{O}_X(D))\) for a scheme ``source`` and a divisor."""
        match divisor:
            case None:
                return _line_bundle_section_ring(self, source)
            case _:
                return _toric_divisor_section_ring(self, source, divisor)

    class ParentMethods:
        def __init__(
            self,
            section_scheme,
            section_line_bundle=None,
            section_divisor=None,
            **rest,
        ) -> None:
            assert (section_line_bundle is None) != (section_divisor is None), (
                f"a section ring of {section_scheme} is the ring of sections of exactly one line "
                f"bundle L or one divisor D, but was given line bundle {section_line_bundle} "
                f"and divisor {section_divisor}"
            )
            self._section_scheme = section_scheme
            self._section_line_bundle = section_line_bundle
            self._section_divisor = section_divisor
            super().__init__(**rest)

        def section_scheme(self):
            r"""The scheme \(X\) whose sections form this ring."""
            return self._section_scheme

        def section_divisor(self):
            r"""The divisor \(D\) with \(L = \mathcal{O}_X(D)\), when the ring was stated on a divisor."""
            assert self._section_divisor is not None, (
                f"{self} is the section ring of the line bundle {self._section_line_bundle}, "
                "which was not given as O_X(D) for a divisor D"
            )
            return self._section_divisor

        def section_line_bundle(self):
            r"""The line bundle \(L\), when the ring was stated on a line bundle."""
            assert self._section_line_bundle is not None, (
                f"{self} is the section ring of the divisor {self._section_divisor}; ask for "
                "section_divisor() instead of a line bundle"
            )
            return self._section_line_bundle

        @cached_method
        def section_semigroup_generators(self):
            return self.affine_semigroup_generator_coordinates()

        def generator_degree(self, label):
            point = self.section_semigroup_generators()[label]
            final_position = int(point.cardinality().finite_value()) - 1
            return NN(int(point[final_position]))

        def homogeneous_degree(self, element):
            r"""Return the nonnegative degree of one homogeneous section-ring element."""
            element = self(element)
            assert element != self.zero(), (
                f"the zero element of {self} has no degree: it is homogeneous of every degree"
            )
            presentation = self.presentation_ring()
            representative = self.lift_to_presentation(element)
            backend = _engine_element(presentation, representative)
            labels = tuple(self.algebra_generating_set())
            degrees = []
            for exponents, coefficient in backend.dict().items():
                if not coefficient:
                    continue
                degree = 0
                for position, exponent in enumerate(exponents):
                    degree += int(exponent) * int(self.generator_degree(labels[position]))
                degrees.append(degree)
            selected = degrees[0]
            assert all(degree == selected for degree in degrees[1:]), (
                f"{element} in {self} has no single degree: it is not homogeneous, its terms have "
                f"degrees {sorted(set(degrees))}"
            )
            return NN(selected)

        @cached_method
        def graded_piece(self, degree):
            r"""The section module \(H^0(X, L^{\otimes n})\) in nonnegative degree ``n``."""
            degree = NN(degree)
            match self._section_line_bundle:
                case None:
                    divisor = self.section_divisor()
                    integers = divisor.parent().base_ring()
                    return self.section_scheme().divisor_section_space(
                        integers(int(degree)) * divisor
                    )
                case bundle:
                    return bundle.tensor_power(int(degree)).global_sections()

        def section_multiplication(self, left_degree, right_degree):
            r"""Multiply sections in two graded pieces of a projective line-bundle ring."""
            self.section_line_bundle()
            left_degree = NN(left_degree)
            right_degree = NN(right_degree)
            left = self.graded_piece(left_degree)
            right = self.graded_piece(right_degree)
            target = self.graded_piece(NN(int(left_degree) + int(right_degree)))
            left_exponents = _section_exponent_data(left)
            right_exponents = _section_exponent_data(right)
            target_exponents = _section_exponent_data(target)
            target_by_exponents = {
                exponents: monomial for monomial, exponents in target_exponents.items()
            }

            def product(left_monomial, right_monomial):
                exponents = tuple(
                    a + b
                    for a, b in zip(
                        left_exponents[left_monomial],
                        right_exponents[right_monomial],
                        strict=True,
                    )
                )
                return target.module_generator(target_by_exponents[exponents])

            return BilinearMap(left, right, target, product)

        @cached_method
        def homogeneous_component_map(self, degree):
            r"""Return the map ``H^0(X,L^n) -> R(L)`` into the degree-``n`` component."""
            bundle = self.section_line_bundle()
            degree = NN(degree)
            piece = self.graded_piece(degree)
            count = int(degree)
            degree_one = bundle.global_sections()
            degree_one_exponents = _section_exponent_data(degree_one)
            generator_by_exponents = {
                tuple(exponents): label
                for label, exponents in zip(
                    self.algebra_generating_set(),
                    (
                        degree_one_exponents[label]
                        for label in degree_one.module_generating_set()
                    ),
                    strict=True,
                )
            }
            base_degree, block_widths = _line_bundle_section_data(bundle)
            base_degree = tuple(int(value) for value in base_degree)
            block_widths = tuple(int(value) for value in block_widths)
            piece_exponents = _section_exponent_data(piece)

            def basis_image(label):
                if count == 0:
                    return self.one()
                parts = _split_section_exponents(
                    piece_exponents[label],
                    base_degree,
                    block_widths,
                    count,
                )
                value = self.one()
                for exponents in parts:
                    value *= self.algebra_generator(generator_by_exponents[exponents])
                return value

            target_module = self.underlying_module()
            return piece.module_category().Mor(piece, target_module)(
                {
                    label: target_module(basis_image(label))
                    for label in piece.module_generating_set()
                }
            )

        def homogeneous_component_element(self, degree, section):
            r"""Return one homogeneous section as the corresponding section-ring element."""
            return self(self.homogeneous_component_map(degree)(section))


def _section_exponent_data(section_space):
    r"""The flat exponent vector of each framing monomial of a polynomial section space."""
    from sage_extensions.categories.divisors.linear_systems import (
        HomogeneousPolynomialSectionSpaces,
        MultihomogeneousPolynomialSectionSpaces,
    )

    ring = section_space.base_ring()
    labels = tuple(section_space.module_generating_set())
    match section_space:
        case _ if section_space in MultihomogeneousPolynomialSectionSpaces(ring):
            return {
                monomial: tuple(
                    int(value)
                    for block in section_space.monomial_exponents(monomial)
                    for value in block
                )
                for monomial in labels
            }
        case _ if section_space in HomogeneousPolynomialSectionSpaces(ring):
            return {
                monomial: tuple(
                    int(value) for value in section_space.monomial_exponents(monomial)
                )
                for monomial in labels
            }
        case _:
            assert False, (
                f"cannot read monomial exponents from {section_space}: it must be a space of "
                "homogeneous or multihomogeneous polynomials, but it is in "
                f"{section_space.category()}"
            )


def _split_block(exponents, part_total, count):
    remaining = list(exponents)
    parts = []
    for _ in range(count):
        need = int(part_total)
        part = []
        for position, available in enumerate(remaining):
            take = min(int(available), need)
            part.append(take)
            remaining[position] -= take
            need -= take
        assert need == 0, (
            f"cannot split the monomial exponent {tuple(exponents)} into {count} monomials of "
            f"degree {part_total}: its total degree is too small"
        )
        parts.append(tuple(part))
    assert not any(remaining), (
        f"cannot split the monomial exponent {tuple(exponents)} into {count} monomials of "
        f"degree {part_total}: its total degree is too large, {tuple(remaining)} is left over"
    )
    return tuple(parts)


def _split_section_exponents(exponents, base_degree, block_widths, count):
    r"""Split a degree-``count`` monomial into ``count`` degree-one monomials.

    Each projective factor is one independent exponent block.  A block of total
    degree ``count*d_i`` is split into ``count`` blocks of degree ``d_i``; the
    corresponding pieces are then concatenated factorwise.  This is a selected
    factorization in the affine semigroup.  Different choices represent the
    same section-ring element by the toric relations.
    """
    exponents = tuple(int(value) for value in exponents)
    base_degree = tuple(int(value) for value in base_degree)
    block_widths = tuple(int(value) for value in block_widths)
    count = int(count)
    assert len(base_degree) == len(block_widths), (
        f"cannot factor a section monomial: the multidegree {base_degree} and the "
        f"projective factor widths {block_widths} must have the same number of factors"
    )
    assert len(exponents) == sum(block_widths), (
        f"cannot factor the section monomial with exponent {exponents}: a product of "
        f"projective spaces with coordinate counts {block_widths} needs "
        f"{sum(block_widths)} exponents"
    )
    if count == 0:
        assert not any(exponents), (
            f"the section monomial with exponent {exponents} is said to have degree 0 in the "
            "section ring, but it is not the constant monomial"
        )
        return ()

    split_blocks = []
    offset = 0
    for degree, width in zip(base_degree, block_widths, strict=True):
        block = exponents[offset : offset + width]
        assert sum(block) == count * degree, (
            f"cannot write the monomial with exponent {exponents} as a product of {count} "
            f"sections of multidegree {base_degree}: its block {block} has total degree "
            f"{sum(block)}, not {count} * {degree}"
        )
        split_blocks.append(_split_block(block, degree, count))
        offset += width

    return tuple(
        tuple(
            exponent
            for block_parts in split_blocks
            for exponent in block_parts[position]
        )
        for position in range(count)
    )


def _line_bundle_section_data(bundle):
    r"""The degree and the coordinate width of each projective factor of ``bundle``.

    Both are read off the degree-one section space of the bundle, which is a
    homogeneous polynomial space on a projective space or a multihomogeneous
    one on a product of projective spaces.
    """
    from sage_extensions.categories.divisors.linear_systems import (
        HomogeneousPolynomialSectionSpaces,
        MultihomogeneousPolynomialSectionSpaces,
    )

    integers = _owned_integers()
    sections = bundle.global_sections()
    ring = sections.base_ring()
    match sections:
        case _ if sections in HomogeneousPolynomialSectionSpaces(ring):
            width = int(sections.homogeneous_coordinate_ring().algebra_generating_set().cardinality())
            return (integers(sections.homogeneous_degree()),), (width,)
        case _ if sections in MultihomogeneousPolynomialSectionSpaces(ring):
            multidegree = sections.multidegree()
            labels = tuple(multidegree.index_set())
            degrees = tuple(multidegree[label] for label in labels)
            widths = tuple(
                stop - start
                for start, stop in (
                    sections.coordinate_block(position) for position in range(len(labels))
                )
            )
            return degrees, widths
        case _:
            assert False, (
                f"cannot form the section ring of {bundle}: section rings of line bundles are "
                "implemented only for O(d) on a projective space or a product of projective "
                f"spaces, whose sections are polynomials; its sections {sections} are not"
            )


def _line_bundle_section_ring(category, bundle):
    r"""Construct the Veronese/Segre-Veronese section algebra of ``bundle``."""
    assert bundle.scheme().scheme_base_ring() is category.base_ring(), (
        f"cannot form the section ring of {bundle} over {category.base_ring()}: the bundle's "
        f"scheme is over {bundle.scheme().scheme_base_ring()}, a different ring"
    )
    base_degree, _block_widths = _line_bundle_section_data(bundle)
    assert all(degree >= 0 for degree in base_degree), (
        f"cannot form the section ring of {bundle}: it is implemented only for O(d) with "
        f"every degree nonnegative, but the multidegree is {base_degree}"
    )
    degree_one = bundle.global_sections()
    exponent_data = _section_exponent_data(degree_one)
    semigroup_generators = tuple(
        (*exponent_data[label], 1)
        for label in degree_one.module_generating_set()
    )
    assert semigroup_generators, (
        f"the section ring of {bundle} has no generators: the bundle has no global sections "
        f"in degree one, although its multidegree {base_degree} is nonnegative"
    )
    names = tuple(f"s{position}" for position in range(len(semigroup_generators)))
    return AffineSemigroupAlgebras(category.base_ring())(
        semigroup_generators,
        names=names,
        extra_categories=(category,),
        extra_construction_data=(
            ("section_scheme", bundle.scheme()),
            ("section_line_bundle", bundle),
        ),
    )


def _toric_divisor_section_ring(category, scheme, divisor):
    r"""Construct the cone-over-polytope section algebra of a toric Cartier divisor."""
    from sage.geometry.cone import Cone as _SageCone

    from sage_extensions.categories.schemes.toric.fans import _engine_vector

    assert scheme.scheme_base_ring() is category.base_ring(), (
        f"cannot form the section ring of {divisor} over {category.base_ring()}: the scheme "
        f"{scheme} is over {scheme.scheme_base_ring()}, a different ring"
    )
    assert scheme.fan().is_complete(), (
        f"cannot form the section ring of {divisor} on the toric variety {scheme}: section "
        "rings of toric divisors are implemented only for complete toric varieties, and "
        "its fan is not complete"
    )
    assert scheme.is_cartier(divisor), (
        f"cannot form the section ring of {divisor} on {scheme}: the divisor must be "
        "Cartier, and it is not"
    )
    assert scheme.is_basepoint_free(divisor), (
        f"cannot form the section ring of {divisor} on {scheme}: section rings of toric "
        "divisors are implemented only for basepoint-free divisors, and this one has base points"
    )

    polytope = scheme.divisor_polytope(divisor)
    lattice = polytope.ambient_lattice()
    cone_rays = tuple(
        (*tuple(_engine_vector(lattice, vertex)), 1)
        for vertex in polytope.vertices()
    )
    hilbert_basis = tuple(
        tuple(int(entry) for entry in vector)
        for vector in _SageCone(cone_rays).Hilbert_basis()
    )
    return AffineSemigroupAlgebras(category.base_ring())(
        hilbert_basis,
        names=tuple(f"s{position}" for position in range(len(hilbert_basis))),
        extra_categories=(category, OwnedIntegralDomains()),
        extra_construction_data=(
            ("section_scheme", scheme),
            ("section_divisor", divisor),
        ),
    )


__all__ = ["SectionRings"]
