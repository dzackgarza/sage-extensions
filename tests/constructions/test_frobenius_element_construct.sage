r"""The canonical finite-field Frobenius is the exponent-one topological generator."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_field_frobenius_has_exponent_one_and_inverse_minus_one() -> None:
    galois = AbsoluteGaloisGroup(GF(5))
    frobenius = galois.frobenius()
    inverse = frobenius.inverse()

    assert frobenius in galois
    assert frobenius.frobenius_exponent() == 1
    assert inverse.frobenius_exponent() == -1
    assert frobenius * inverse == galois.one()
    assert frobenius.conjugacy_class().representative() == frobenius

