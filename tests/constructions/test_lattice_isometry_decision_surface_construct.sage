r"""A lattice exposes exact self-isometry witnesses and boolean decisions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_isometry_to_itself_has_expected_endpoints() -> None:
    lattice = NamedLattices.U
    isometry = lattice.isometry_to(lattice)

    assert isometry is not None
    assert isometry.domain() is lattice
    assert isometry.codomain() is lattice


def test_hyperbolic_plane_is_isometric_to_itself_is_true() -> None:
    lattice = NamedLattices.U

    assert lattice.is_isometric_to(lattice) is True
