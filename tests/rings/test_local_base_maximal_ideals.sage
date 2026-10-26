r"""The maximal ideal of a ring built on a local base.

For a local base ``(R, m)`` the ring ``R[[t_1, ..., t_n]]`` is local with
maximal ideal ``m A + (t_1, ..., t_n)``, and so is ``R[e]/(e^2)`` with maximal
ideal ``m A + (e)``.  Both parts are needed: over ``Z_3`` the scalar ``3`` is a
non-unit of the power-series ring, and in two variables both variables are.
"""

from sage_extensions.all import *






def test_power_series_over_a_local_base_retain_the_base_maximal_ideal() -> None:
    base = Zp(3)
    (base_uniformizer,) = base.maximal_ideal().ideal_generators()
    ring = base.power_series_ring("t")

    assert ring.maximal_ideal() == ring.ideal(ring(base_uniformizer), ring.algebra_generator("t"))
    assert ring.residue_field() is base.residue_field()
    assert int(ring.residue_field().cardinality()) == 3


def test_dual_numbers_over_a_local_base_retain_the_base_maximal_ideal() -> None:
    base = Zp(3)
    (base_uniformizer,) = base.maximal_ideal().ideal_generators()
    ring = base.dual_numbers()

    assert ring.maximal_ideal() == ring.ideal(ring(base_uniformizer), ring.algebra_generator("epsilon"))
    assert ring.residue_field() is base.residue_field()




def test_padic_principal_quotient_cardinality_is_residue_size_to_valuation() -> None:
    ring = Zp(2)
    quotient = ring.quotient_ring(ring.ideal(ring(6)))

    assert quotient.cardinality() == 2
