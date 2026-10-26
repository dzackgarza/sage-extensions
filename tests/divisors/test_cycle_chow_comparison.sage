r"""Divisors, codimension-one cycles and the class group of the affine plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_weil_divisor_cycle_isomorphism_preserves_prime_and_principal_multiplicity() -> None:
    r"""On ``A^2_Q``: ``div(x) = [V(x)]`` as a codimension-one cycle, and back."""
    ring = QQ['x,y']
    x = ring('x')
    plane = ring.affine_spectrum()
    weil = plane.weil_divisor_group()
    comparison = plane.weil_cycle_isomorphism()
    prime = ring.spectrum()(ring.ideal(x))

    divisor = weil.principal_divisor(x)
    cycle = comparison.forward()(divisor)

    assert cycle == comparison.forward().codomain().prime_cycle(prime)
    assert comparison.inverse()(cycle) == divisor
    assert weil.principal_divisor(x**2) == 2 * divisor


def test_class_group_and_first_chow_group_of_the_affine_plane_vanish() -> None:
    r"""``Cl(A^2_Q) = CH^1(A^2_Q) = 0``: ``Q[x, y]`` is a UFD.

    Hartshorne, *Algebraic Geometry*, II.6.2: ``A`` Noetherian normal is a UFD
    iff ``Cl(Spec A) = 0``.
    """
    ring = QQ['x,y']
    x, y = ring('x'), ring('y')
    plane = ring.affine_spectrum()
    weil = plane.weil_divisor_group()
    line = weil.prime_divisor(ring.spectrum()(ring.ideal(x - y**2)))

    assert plane.class_group().cardinality() == 1
    assert plane.chow_group(1).cardinality() == 1
    assert line == weil.principal_divisor(x - y**2)
    assert plane.class_group_projection()(line) == plane.class_group().zero()
