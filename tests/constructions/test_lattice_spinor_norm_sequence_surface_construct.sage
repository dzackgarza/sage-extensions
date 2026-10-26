r"""The spinor-norm sequence retains its lattice and rational quadratic space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_spinor_norm_sequence_retains_lattice_and_space() -> None:
    lattice = NamedLattices.U
    sequence = lattice.spinor_norm_sequence()
    space = lattice.vector_space()

    assert sequence.lattice() is lattice
    assert sequence.quadratic_space() == space


def test_hyperbolic_plane_spinor_norm_sequence_has_expected_source_and_target() -> None:
    lattice = NamedLattices.U
    sequence = lattice.spinor_norm_sequence()
    space = sequence.quadratic_space()

    assert sequence.source() is space.Aut()
    assert sequence.target() is space.base_ring().square_class_group()
