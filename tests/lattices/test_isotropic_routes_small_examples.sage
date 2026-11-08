r"""Small examples with hand-derived answers for the general isotropic routes.

L=U+<-2>, square -2: by the Eichler criterion primitive vectors are classified
by their class in the discriminant group, which has order two, and both a
divisor-two vector (x) and a divisor-one vector (e-f) exist. Two orbits.

L=2U+U(3), rank-three null planes: I has associated order-three isotropic
subgroup H of the discriminant group, one of the two isotropic lines of the
hyperbolic form on (Z/3)^2, exchanged by O(L). The overlattice for H is 3U, and
GL(I') is transitive on lines of I'/3I', so one orbit.

L=3U+<-6>, maximal null plane in 3U: minus one on <-6> is in the stabilizer and
is -1 on the discriminant group Z/6, whose orthogonal group is {+-1}.

3U, flags of type (1,3): a stabilizer element of a maximal null plane acts by A
on I and A^{-T} on L/I, so has determinant one. O(L)-orbits (one) split in two.
"""

from sage_extensions.all import *


def _hyperbolic(count):
    ambient = Lattices(ZZ)("U")
    for _ in range(count - 1):
        ambient = ambient + Lattices(ZZ)("U")
    return ambient


def test_spacelike_lorentzian_vector_orbits():
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    representatives = tuple(ambient.O().vector_orbit_representatives(-2))
    assert len(representatives) == 2
    assert sorted(int(point.divisor()) for point in representatives) == [1, 2]


def test_rank_three_null_planes_with_proper_levi_image():
    ambient = _hyperbolic(2) + Lattices(ZZ)("U").twist(3)
    assert ambient.O().isotropic_orbit_representatives(3).cardinality() == cardinal(1)


def test_rank_three_discriminant_image():
    ambient = _hyperbolic(3) + Lattices(ZZ)("A1").twist(3)
    plane = ambient.primitive_isotropic_subobject(*tuple(ambient.module_generators())[:6:2])
    assert plane.stabilizer_discriminant_image().cardinality() == cardinal(2)


def test_partial_flags_of_type_one_three_split_under_so():
    ambient = _hyperbolic(3)
    type_ = FlagType((1, 3))
    assert ambient.O().isotropic_orbit_representatives(type_, flag=True).cardinality() == cardinal(1)
    assert ambient.SO().isotropic_orbit_representatives(type_, flag=True).cardinality() == cardinal(2)
