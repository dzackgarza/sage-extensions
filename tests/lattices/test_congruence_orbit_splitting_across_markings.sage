r"""Gamma-orbits of every marking of 2U = U + U, split through the finite image modulo three.

The image F of O(2U) in Aut(2U/3) is O^+(4, 3), of order 1152, and O(2U)
is transitive on each marking type below. For Gamma = rho^-1(S) the
Gamma-orbits in an O(2U)-orbit G/P are the double cosets S \ F / rho(P).
The stabilizer images rho(P) are the full stabilizers in F of the reduction,
since each integral parabolic or orthogonal factor maps onto its finite
counterpart:

- a primitive null vector e: O(e^perp/e) and the Eichler transvections give
  O(U/3) (order 4) times F_3^2, order 36, so Gamma(3) has 1152/36 = 32 orbits;
- the line Ze adds the sign: 72 and 16 orbits;
- the plane <e, u>: GL_2(ZZ) and the skew unipotents map onto GL_2(F_3) and
  F_3, order 144, 8 orbits; the flag Ze < <e, u> has the Borel, order 36, 32 orbits;
- the nondegenerate summand U: O(U) x O(U), order 16, 72 orbits.

Gamma(3) acts trivially on 2U/3, so distinct reductions certify distinct orbits.
-id lies in Gamma(2) and not in Gamma(3), so e and -e are equivalent exactly
under the first. For S = rho(P_e), the non-normal stabilizer of the residue of
e, the Gamma-orbits of null vectors are the S-orbits on the 32 isotropic
vectors: +e, -e, the 12 others orthogonal to e, and b(e, w) = 1 or 2 (9 each).
"""

from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.finite_rings.finite_field_constructor import GF as SageGF

from sage_extensions.all import *


def _ambient():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    return ambient, ambient.O(), tuple(ambient.module_generators()), tuple(ambient.module_generating_set())


def _residue(labels, point):
    return tuple(int(point.to_vector()(label)) % 3 for label in labels)


def _span(labels, points):
    return sage_matrix(SageGF(3), [_residue(labels, point) for point in points]).row_space()


def _pointed_category(ambient):
    source = Lattices(ZZ)([[0]])
    category = Lattices(ZZ).CosliceUnder(source)
    generator = source.module_generator(next(iter(source.module_generating_set())))
    marking = lambda vector: category.object(source.Mor(ambient)(lambda _label: vector))
    return category, generator, marking


def _arrow_images(marked):
    arrow = marked.arrow()
    return tuple(arrow(point) for point in arrow.domain().module_generators())


def test_based_null_vectors_split_into_thirty_two_gamma_three_orbits():
    ambient, group, (e, _f, _u, _v), labels = _ambient()
    category, generator, marking = _pointed_category(ambient)
    representatives = tuple(group.split_orbit(marking(e), group.congruence_preimage(3)))
    vectors = [category.arrow(representative)(generator) for representative in representatives]
    assert len(representatives) == 32
    assert len({_residue(labels, vector) for vector in vectors}) == 32


def test_a_based_vector_and_its_negative_under_gamma_three_and_gamma_two():
    ambient, group, (e, _f, _u, _v), _labels = _ambient()
    category, _generator, marking = _pointed_category(ambient)
    plus, minus = marking(e), marking(-e)
    isomorphisms = category.Core().Mor(plus, minus)
    assert isomorphisms.an_element_in(group.congruence_preimage(3)) is None
    assert isomorphisms.an_element_in(group.congruence_preimage(2)) is not None


def test_based_vector_stabilizer_in_gamma_three_fixes_the_vector():
    ambient, group, (e, _f, _u, _v), _labels = _ambient()
    gamma = group.congruence_preimage(3)
    generators = tuple(gamma.stabilizer(e).group_generators())
    assert all(g in gamma and g(e) == e for g in generators)


def test_null_vectors_under_the_preimage_of_a_non_normal_stabilizer():
    ambient, group, (e, _f, _u, _v), labels = _ambient()
    representation = group.congruence_representation(3)
    target = representation.codomain().subgroup(tuple(representation(g) for g in group.stabilizer(e).group_generators()))
    assert target.cardinality() == cardinal(36)
    category, generator, marking = _pointed_category(ambient)
    representatives = tuple(group.split_orbit(marking(e), group.congruence_preimage(3, target)))
    vectors = [category.arrow(representative)(generator) for representative in representatives]

    def kind(vector):
        residue = _residue(labels, vector)
        if residue == _residue(labels, e):
            return "e"
        if residue == _residue(labels, -e):
            return "-e"
        return int(ambient.b(e, vector)) % 3

    assert sorted(map(str, map(kind, vectors))) == ["-e", "0", "1", "2", "e"]


def test_null_lines_split_into_sixteen_gamma_three_orbits():
    ambient, group, (e, f, _u, _v), labels = _ambient()
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    gamma = group.congruence_preimage(3)
    marked = arrows.object(ambient.primitive_isotropic_subobject(e).inclusion())
    representatives = tuple(group.split_orbit(marked, gamma))
    assert len(representatives) == 16
    assert len({_span(labels, _arrow_images(r)) for r in representatives}) == 16
    other = arrows.object(ambient.primitive_isotropic_subobject(f).inclusion())
    assert arrows.Core().Mor(marked, other).an_element_in(gamma) is None


def test_null_planes_split_into_eight_gamma_three_orbits_with_stabilizers():
    ambient, group, (e, f, u, v), labels = _ambient()
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    gamma = group.congruence_preimage(3)
    plane = ambient.primitive_isotropic_subobject(e, u)
    marked = arrows.object(plane.inclusion())
    representatives = tuple(group.split_orbit(marked, gamma))
    assert len(representatives) == 8
    assert len({_span(labels, _arrow_images(r)) for r in representatives}) == 8
    opposite = arrows.object(ambient.primitive_isotropic_subobject(f, v).inclusion())
    assert arrows.Core().Mor(marked, opposite).an_element_in(gamma) is None
    generators = tuple(gamma.stabilizer(plane, action="setwise").group_generators())
    assert all(g in gamma and plane.stabilizes(g) for g in generators)


def test_null_flags_split_into_thirty_two_gamma_three_orbits():
    ambient, group, (e, _f, u, _v), _labels = _ambient()
    flags = Cat().Mor(FiniteOrdinalCategory(3), Lattices(ZZ))
    line = ambient.subobject_on([e])
    plane = ambient.subobject_on([e, u])
    line_into_plane = line.Emb(plane)(line.inclusion().factor_through(plane.inclusion()))
    marked = flags((line_into_plane, plane.inclusion()))
    representatives = tuple(group.split_orbit(marked, group.congruence_preimage(3)))
    assert len(representatives) == 32
    assert all(representative in flags for representative in representatives)


def test_hyperbolic_summands_split_into_seventy_two_gamma_three_orbits():
    ambient, group, (e, f, _u, _v), labels = _ambient()
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    marked = arrows.object(ambient.subobject_on([e, f]).inclusion())
    representatives = tuple(group.split_orbit(marked, group.congruence_preimage(3)))
    assert len(representatives) == 72
    assert len({_span(labels, _arrow_images(r)) for r in representatives}) == 72
