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
