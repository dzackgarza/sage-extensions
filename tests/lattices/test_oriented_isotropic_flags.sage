r"""Oriented primitive isotropic sublattices and flags.

The Levi factor of the parabolic of the maximal null plane I in 2U is
GL(I), which contains determinant -1. So the two orientations of I are
equivalent and the oriented stabilizer has index two in P_I.
"""

from sage_extensions.all import *


def test_oriented_maximal_null_plane_has_one_class_and_index_two_stabilizer():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    group = ambient.O()
    assert group.oriented_isotropic_orbit_representatives(FlagType((2,))).cardinality() == cardinal(1)
    e1, f1, e2, f2 = tuple(ambient.module_generators())
    positive = OrientedIsotropicFlag(ambient, (e1, e2))
    negative = OrientedIsotropicFlag(ambient, (e2, e1))
    witness = group.oriented_isotropic_equivalence_witness(positive, negative)
    assert witness is not None
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in (e1, f1, e2, f2) for y in (e1, f1, e2, f2))
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    assert plane.inclusion().is_in_image(witness(e1)) and plane.inclusion().is_in_image(witness(e2))
    swap = ambient.Aut()(dict(zip(tuple(ambient.module_generating_set()), (e2, f2, e1, f1), strict=True)))
    oriented = tuple(group.oriented_isotropic_stabilizer_generators(positive))
    assert all(plane.inclusion().is_in_image(element(point)) for element in oriented for point in (e1, e2))

    def determinant(element):
        coordinates = tuple(plane.inclusion().lift(element(point)).to_vector() for point in (e1, e2))
        labels = tuple(plane.inclusion().domain().module_generating_set())
        return coordinates[0](labels[0])*coordinates[1](labels[1]) - coordinates[0](labels[1])*coordinates[1](labels[0])

    assert determinant(swap) == -1
    assert all(determinant(element) == 1 for element in oriented)


def test_oriented_complete_flag_in_three_hyperbolic_planes_has_one_class():
    r"""Complete null flags of 3U form one O(3U)-class: hyperbolic completion gives an
    adapted basis e1, f1, e2, f2, e3, f3. The Levi diag(s1, s2, s3) on e1, e2, e3,
    extended by the same signs on f1, f2, f3, stabilizes the flag and acts on the
    graded pieces by (s1, s2, s3), so every orientation is attained and the oriented
    flags form one class. The oriented stabilizer is the kernel of the graded sign map.
    """
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    group = ambient.O()
    complete = FlagType.complete(3)
    assert group.oriented_isotropic_orbit_representatives(complete).cardinality() == cardinal(1)
    e1, f1, e2, f2, e3, f3 = tuple(ambient.module_generators())
    basis = (e1, f1, e2, f2, e3, f3)
    positive = OrientedIsotropicFlag(ambient, (e1, e2, e3), flag_type=complete)
    reversed_first = OrientedIsotropicFlag(ambient, (-e1, e2, e3), flag_type=complete)
    witness = group.oriented_isotropic_equivalence_witness(positive, reversed_first)
    assert witness is not None
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in basis for y in basis)
    assert witness(e1) == -e1
    line = ambient.primitive_isotropic_subobject(e1)
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    assert line.inclusion().is_in_image(witness(e2) - e2)
    assert plane.inclusion().is_in_image(witness(e3) - e3)
    oriented = tuple(group.oriented_isotropic_stabilizer_generators(positive))
    for element in oriented:
        assert element(e1) == e1
        assert line.inclusion().is_in_image(element(e2) - e2)
        assert plane.inclusion().is_in_image(element(e3) - e3)
