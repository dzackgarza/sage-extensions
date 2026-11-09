r"""Consumers on L = U + <0>, with e, f the hyperbolic basis and r the radical.

O(L) has blocks [A B; 0 D]: A in O(U), D = +-1, B in Hom(U, R). For v = (c, s r)
with c of content d, the shears move s by multiples of d, so the primitive
classes of square n are pairs (O(U)-class of c, class of s in (Z/d)^*/+-1).
Square 2: only +-(e+f), one class. Square 50: (1,25) of content 1, and (5,5) of
content 5 with s in {1, 2}; together with the imprimitive 5(e+f), four classes.
The image modulo 3 has order 4 * 2 * 9 = 72; the shear e -> e + 3r lies in Gamma(3).
"""

from sage_extensions.all import *


def _lattice():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0]])
    return lattice, tuple(lattice.module_generators())


def test_degenerate_vector_classes_of_square_two_and_fifty():
    lattice, (e, f, r) = _lattice()
    group = lattice.O()
    assert len(tuple(group.vector_orbit_representatives(2))) == int(1)
    classes = tuple(group.vector_orbit_representatives(50))
    assert len(classes) == int(4)
    assert all(lattice.q(point) == 50 for point in classes)
    assert sum(int(1) for point in classes if point.content() == 5) == int(1)
    five_glued = [point for point in classes if point.content() == 1 and abs(int(point.to_vector()(tuple(lattice.module_generating_set())[0]))) == 5]
    last = tuple(lattice.module_generating_set())[2]
    assert sorted(abs(int(point.to_vector()(last))) for point in five_glued) == [int(1), int(2)]


def test_congruence_image_and_kernel_generators():
    lattice, (e, f, r) = _lattice()
    group = lattice.O()
    representation = group.congruence_representation(3)
    assert int(representation.codomain().cardinality()) == int(72)
    gamma = group.congruence_preimage(3)
    generators = tuple(gamma.group_generators())
    identity = representation.codomain().one()
    assert all(representation(group(g)) == identity for g in generators)
    labels = tuple(lattice.module_generating_set())
    shear = group(lambda label: lattice.module_generator(label) + (lattice.scalar_multiple(3, r) if label == labels[0] else lattice.zero()))
    assert shear in gamma
    assert representation(shear) == identity
