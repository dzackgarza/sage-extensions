r"""The hyperbolic plane has two isometries in each definite-complement vector coset."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_definite_complement_extensions_exhaust_vector_cosets() -> None:
    lattice = NamedLattices.U
    first, second = lattice.module_generators()
    vector = first + second
    stabilizer = lattice.definite_complement_extensions(vector, vector)
    opposite = lattice.definite_complement_extensions(vector, -vector)

    assert stabilizer.cardinality() == cardinal(2)
    assert opposite.cardinality() == cardinal(2)
    assert all(isometry(vector) == vector for isometry in stabilizer)
    assert all(isometry(vector) == -vector for isometry in opposite)
