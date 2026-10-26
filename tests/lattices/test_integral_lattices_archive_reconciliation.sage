r"""The discriminant group ``A_L = L^#/L`` of an integral lattice."""

from sage_extensions.all import *


def test_A2_discriminant_group_has_order_three_and_the_lattice_maps_to_zero_in_it() -> None:
    r"""``|A_{A_2}| = |det A_2| = 3``, and ``L -> L^# -> L^#/L`` is the zero map.

    Conway--Sloane, SPLAG, Ch. 4, Sec. 6.1: ``det A_n = n + 1``.
    """
    lattice = Lattices(ZZ)("A2")
    discriminant = lattice.discriminant_module()
    projection = lattice.discriminant_projection()
    correlation = lattice.correlation_morphism()

    assert discriminant.cardinality() == 3
    assert all(
        projection(correlation(root)) == discriminant.zero()
        for root in lattice.module_generators()
    )
