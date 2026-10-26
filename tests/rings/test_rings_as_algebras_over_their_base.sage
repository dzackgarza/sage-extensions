r"""A commutative ring is an algebra over any ring mapping to it.

Every ring is uniquely a ``Z``-algebra, since ``Z`` is initial: ``Z/6`` is a
``Z``-algebra whose structure map sends ``7`` to ``1``, and ``Q`` is a ``Z``-algebra.
``Q[x]`` is already a ``Q``-algebra and is its own ``Q``-algebra.  There is no ring
map ``Q -> Z`` (the image of ``1/2`` would be an inverse of ``2`` in ``Z``), so ``Z``
is not a ``Q``-algebra.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_six_is_a_z_algebra() -> None:
    residues = ZZ.ideal(ZZ(6)).quotient_ring()
    algebra = residues.as_ZZ_algebra()
    structure = algebra.algebra_structure_morphism()

    assert algebra in Algebras(ZZ)
    assert structure(ZZ(7)) == algebra.one()
    assert structure(ZZ(6)) == algebra.zero()


def test_the_rationals_are_a_z_algebra() -> None:
    algebra = QQ.as_ZZ_algebra()
    structure = algebra.algebra_structure_morphism()

    assert algebra in Algebras(ZZ)
    assert structure(ZZ(3)) * algebra(QQ(1) / QQ(3)) == algebra.one()


def test_a_polynomial_ring_over_q_is_its_own_q_algebra() -> None:
    polynomials = QQ["x"]

    assert polynomials.as_algebra_over(QQ) is polynomials


def test_the_integers_are_not_an_algebra_over_the_rationals() -> None:
    with pytest.raises(ValueError):
        ZZ.as_algebra_over(QQ)
