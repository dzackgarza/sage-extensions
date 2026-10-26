r"""For an isotropic vector e, e-perp modulo e is its isotropic reduction."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_isotropic_vector_e_perp_mod_e_is_zero() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    reduction = e.e_perp_mod_e()

    assert reduction.module_rank() == cardinal(0)
