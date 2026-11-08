r"""Finite lattice pairings retain named framings and their coefficient rings."""

from sage_extensions.all import *


def test_the_identity_pairing_uses_its_named_module_framing() -> None:
    lattice = Lattices(ZZ)(ZZ.free_module(["left", "right"]))
    left, right = lattice.module_generators()

    assert lattice.b(2 * left + 3 * right, 5 * left - 7 * right) == ZZ(-11)
    assert lattice.q(2 * left + 3 * right) == ZZ(13)


def test_the_zero_lattice_pairing_has_the_owned_zero_value() -> None:
    lattice = Lattices(ZZ)(ZZ.free_module(0))

    assert lattice.b(lattice.zero(), lattice.zero()) == ZZ.zero()
    assert lattice.b(lattice.zero(), lattice.zero()).parent() is ZZ


def test_a_polynomial_valued_pairing_retains_its_form_coefficients() -> None:
    ring = QQ.polynomial_ring("t")
    t = ring.algebra_generator("t")
    lattice = Lattices(ring)([[ring.one(), t], [t, ring.one() + t**2]])
    first, second = lattice.module_generators()

    assert lattice.b(first, first + second) == ring.one() + t
    assert lattice.q(first + second) == ring(2) + ring(2) * t + t**2
