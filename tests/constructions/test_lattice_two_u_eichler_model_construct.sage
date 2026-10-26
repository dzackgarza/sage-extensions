r"""An even lattice builds the represented U + U + K Eichler model."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_two_u_eichler_model_retains_orthogonal_complement() -> None:
    complement = Lattices(ZZ)("A2")
    model = complement.two_u_eichler_model()

    assert model.orthogonal_complement() is complement
    assert model.lattice().biproduct_factor(2) is complement


def test_a2_two_u_eichler_model_has_two_hyperbolic_plane_factors() -> None:
    complement = Lattices(ZZ)("A2")
    model = complement.two_u_eichler_model()

    assert model.first_hyperbolic_plane() == NamedLattices.U
    assert model.second_hyperbolic_plane() == NamedLattices.U
    assert model.lattice().rank() == cardinal(6)
