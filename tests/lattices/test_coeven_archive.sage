r"""Archive reconciliation for coeven and coodd integral lattices."""

from sage_extensions.all import *


def test_coevenness_is_the_integrality_of_the_full_discriminant_quadratic_form() -> None:
    assert NamedLattices.U.is_coeven()
    assert NamedLattices.E8.is_coeven()
    assert NamedLattices.U_2.is_coeven()

    assert not NamedLattices.A2.is_coeven()
    assert NamedLattices.A2.is_coodd()


def test_two_elementary_delta_is_the_specialized_coeven_condition() -> None:
    for lattice in (
        NamedLattices.U,
        NamedLattices.U_2,
        NamedLattices.E8,
        NamedLattices.E8_2,
        NamedLattices.E10_2,
        NamedLattices.TEn,
    ):
        assert lattice.is_coeven() == (EvenTwoElementaryLattices(ZZ)(lattice).delta() == 0)
        assert lattice.is_coodd() == (EvenTwoElementaryLattices(ZZ)(lattice).delta() == 1)
