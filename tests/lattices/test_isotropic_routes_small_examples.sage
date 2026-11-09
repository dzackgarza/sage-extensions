r"""Small examples with hand-derived answers for the general isotropic routes.

L=U+<-2>, square -2: by the Eichler criterion primitive vectors are classified
by their class in the discriminant group, which has order two, and both a
divisor-two vector (x) and a divisor-one vector (e-f) exist. Two orbits.

L=2U+U(3), rank-three null planes: I has associated order-three isotropic
subgroup H of the discriminant group, one of the two isotropic lines of the
hyperbolic form on (Z/3)^2, exchanged by O(L). The overlattice for H is 3U, and
GL(I') is transitive on lines of I'/3I', so one orbit.

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
    r"""L = 2U + U(3) has one orbit of primitive isotropic rank-three sublattices.

    Let I be one. Since I = I^perp, the cokernel C of L/I -> I^dual has
    |C|^2 = |A_L| = 9, so H = (I_Q meet L^dual)/I is an isotropic line in A_L.
    A_L has two isotropic lines, and the U(3) exchange swaps them. Fix H and
    let M = L + H, so M = 3U and L = {x in M : b(x, t) = 0 mod 3} for a t in
    M isotropic modulo 3. The saturation I' of I in M is a Lagrangian with
    I = I' meet L of index three, so b(I', t) is nonzero modulo 3. O(M) is
    transitive on Lagrangians. Write t = (a, phi) in I' + I'^dual with phi
    nonzero and phi(a) = 0 modulo 3. GL(I') moves phi to a fixed covector up
    to scalar, and a skew shear s has s(phi) ranging over ker(phi), which
    clears a. So the stabilizer of I' is transitive on such lines t, and the
    stabilizer of L in O(M) is transitive on the I'.
    """
    ambient = _hyperbolic(2) + Lattices(ZZ)("U").twist(3)
    assert ambient.O().isotropic_orbit_representatives(3).cardinality() == cardinal(1)


def test_partial_flags_of_type_one_three_split_under_so():
    ambient = _hyperbolic(3)
    type_ = FlagType((1, 3))
    assert ambient.O().isotropic_orbit_representatives(type_, flag=True).cardinality() == cardinal(1)
    assert ambient.SO().isotropic_orbit_representatives(type_, flag=True).cardinality() == cardinal(2)
