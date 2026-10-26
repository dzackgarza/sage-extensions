r"""A lattice retains the defining covectors of a rational polyhedral cone."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_cone_retains_ambient_lattice_and_halfspace_covector() -> None:
    lattice = NamedLattices.U
    covector = lattice.basis_vector(0).to_covector()
    cone = lattice.rational_polyhedral_cone((covector,))

    assert cone.ambient_lattice() is lattice
    assert cone.halfspace_covectors().cardinality() == cardinal(1)
    assert cone.halfspace_covectors()[0] == covector


def test_hyperbolic_plane_cone_retains_equation_covectors() -> None:
    lattice = NamedLattices.U
    equation = lattice.basis_vector(1).to_covector()
    cone = lattice.rational_polyhedral_cone((), equation_covectors=(equation,))

    assert cone.equation_covectors().cardinality() == cardinal(1)
    assert cone.equation_covectors()[0] == equation
