r"""Elementary discriminant groups and the parity invariant \(\delta\)."""

from sage_extensions.all import *


def test_p_elementary_means_prime_exponent_not_prime_power_order() -> None:
    r"""\(A_{U(2)}=(\mathbb Z/2)^2\) and \(A_{E_8}=0\) are 2-elementary; \(A_{A_2}=\mathbb Z/3\)
    is 3-elementary and not 2-elementary; \(A_{\langle4\rangle}=\mathbb Z/4\) has 2-power
    order and exponent 4, so it is not 2-elementary.
    """
    assert NamedLattices.U_2.is_p_elementary(2)
    assert NamedLattices.E8.is_p_elementary(2)

    assert not NamedLattices.A2.is_p_elementary(2)
    assert NamedLattices.A2.discriminant_group().is_p_elementary(3)

    assert not NamedLattices.Z.twist(4).is_p_elementary(2)


def test_delta_of_a_two_elementary_lattice_vanishes_exactly_when_it_is_coeven() -> None:
    r"""\(\delta=0\) iff \(q_L\) takes values in \(\mathbb Z/2\mathbb Z\) (Nikulin, *Integral
    symmetric bilinear forms*, Izv. 1979, §3.6).  For \(U(2)\), \(E_8(2)\) and their sums the
    discriminant values \(x^2/4\) with \(x^2\in4\mathbb Z\) are integers, so \(\delta=0\);
    for \(A_1=\langle-2\rangle\), \(q(e/2)=-1/2\), so \(\delta=1\).
    """
    for lattice in (
        NamedLattices.U,
        NamedLattices.U_2,
        NamedLattices.E8,
        NamedLattices.E8_2,
        NamedLattices.E10_2,
        NamedLattices.TEn,
    ):
        assert EvenTwoElementaryLattices(ZZ)(lattice).delta() == 0
        assert lattice.is_coeven()

    assert EvenTwoElementaryLattices(ZZ)(NamedLattices.A1).delta() == 1
    assert not NamedLattices.A1.is_coeven()
