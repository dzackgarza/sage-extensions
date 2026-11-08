r"""Every lift of the positive A1 squared plus 5A2 discriminant image is exact.

The two norm-one axes span the unimodular summand. Its orthogonal group
has order eight and acts trivially on the discriminant. The scaled A2
summand has a faithful dihedral discriminant action of order twelve.
"""

from sage_extensions.all import *


def test_scaled_a2_discriminant_image_lifts_every_element_exactly():
    positive_one = Lattices(ZZ)([[ZZ(1)]])
    scaled_a2 = Lattices(ZZ)("A2").twist(ZZ(-5))
    lattice = positive_one + positive_one + scaled_a2
    group = lattice.O()
    image = group.discriminant_image()
    assert group.cardinality() == cardinal(96)
    assert image.cardinality() == cardinal(12)
    for automorphism in lattice.discriminant_group().orthogonal_group():
        lift = group.discriminant_lift(automorphism)
        if automorphism in image:
            assert lift in group
            assert lift.discriminant_morphism() == automorphism
        else:
            assert lift is None
