r"""The lattice correlation alias is its metric correlation morphism."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_correlation_is_correlation_morphism() -> None:
    lattice = NamedLattices.A1

    assert lattice.correlation() == lattice.correlation_morphism()
