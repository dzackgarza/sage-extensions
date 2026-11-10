r"""The coordinate null 3-plane in 3U + <-6> has full discriminant image.

The discriminant group is Z/6 and its automorphism group is {1,-1}.
Negating the last summand fixes the null plane and realizes -1, so the
stabilizer image has exactly two elements.
"""

from sage_extensions.all import *


def test_rank_three_null_stabilizer_realizes_both_discriminant_automorphisms():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic + Lattices(ZZ)([[-6]])
    basis = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    space = ambient.primitive_isotropic_subobject(*basis[:6:2])
    witness = ambient.Aut()(dict(zip(labels, (*basis[:-1], -basis[-1]), strict=True)))
    assert space.stabilizes(witness)
    discriminant = ambient.discriminant_group()
    assert discriminant.cardinality() == cardinal(6)
    rho = ambient.discriminant_representation()
    assert all(rho(witness)(point) == -point for point in discriminant)
    image = space.stabilizer_discriminant_image()
    assert image.cardinality() == cardinal(2)
    assert rho(witness) in image


def test_rank_three_null_stabilizer_of_twisted_hyperbolic_sum_fixes_one_isotropic_line():
    r"""L = U + U + U(3), I = <e1, e2, e3>. A_L = (Z/3)^2 with the hyperbolic form.

    Its orthogonal group has order four: +-1 fix both isotropic lines, and +-swap exchange
    them. Stab(I) fixes the isotropic line (I_Q meet L^dual)/I, so its image lies in {+-1},
    and -1 on L lies in Stab(I) and acts by -1, which is not the identity on (Z/3)^2.
    """
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic.twist(3)
    basis = tuple(ambient.module_generators())
    labels = tuple(ambient.module_generating_set())
    space = ambient.primitive_isotropic_subobject(*basis[::2])
    minus = ambient.Aut()(dict(zip(labels, tuple(-b for b in basis), strict=True)))
    assert space.stabilizes(minus)
    rho = ambient.discriminant_representation()
    image = space.stabilizer_discriminant_image()
    assert image.cardinality() == cardinal(2)
    assert rho(minus) in image
