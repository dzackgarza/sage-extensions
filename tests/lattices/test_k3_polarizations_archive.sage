r"""Polarized K3 lattice complements retained from the archive suite.

A primitive degree-``2d`` polarization spans ``<2d>`` in the K3 lattice, and
its transcendental complement has anti-isometric discriminant form.  Degree
``2`` and degree ``4`` therefore have distinct order-two/order-four
discriminant groups although their complements have the same rank/signature.
"""

from sage_extensions.all import *


def _polarization_complement(vector):
    k3 = Lattices.LK3
    line = k3.subobject_on((vector,))
    return line, line.orthogonal_complement()


def test_degree_two_polarization_has_order_two_transcendental_discriminant() -> None:
    k3 = Lattices.LK3
    e, f = k3.module_generator("e1"), k3.module_generator("f1")
    polarization, transcendental = _polarization_complement(e + f)

    assert polarization.is_primitive()
    assert polarization.gram_matrix().determinant() == 2
    assert transcendental.module_rank() == 21
    invariants = transcendental.discriminant_group().invariants()
    assert invariants.cardinality() == 1
    assert invariants[0] == 2
    assert transcendental.discriminant_group().is_anti_isometric(
        polarization.discriminant_group()
    )


def test_degree_four_polarization_has_distinct_order_four_discriminant() -> None:
    k3 = Lattices.LK3
    e, f = k3.module_generator("e1"), k3.module_generator("f1")
    degree_two, transcendental_two = _polarization_complement(e + f)
    degree_four, transcendental_four = _polarization_complement(2 * e + f)

    assert degree_four.is_primitive()
    assert degree_four.gram_matrix().determinant() == 4
    assert transcendental_four.module_rank() == 21
    invariants = transcendental_four.discriminant_group().invariants()
    assert invariants.cardinality() == 1
    assert invariants[0] == 4
    assert transcendental_four.discriminant_group().is_anti_isometric(
        degree_four.discriminant_group()
    )
    assert not transcendental_four.discriminant_group().is_isomorphic(
        transcendental_two.discriminant_group()
    )
    assert degree_two.gram_matrix().determinant() == 2
