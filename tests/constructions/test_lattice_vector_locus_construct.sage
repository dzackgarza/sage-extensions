r"""A lattice exposes predicate loci of vectors with prescribed square."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_isotropic_vector_locus_contains_basis_vectors() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    f = lattice.basis_vector(1)
    isotropic = lattice.vector_locus(ZZ.zero())

    assert e in isotropic
    assert f in isotropic
    assert e + f not in isotropic


def test_primitive_vector_locus_excludes_nonprimitive_multiples() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    primitive_isotropic = lattice.vector_locus(ZZ.zero(), primitive=True)

    assert e in primitive_isotropic
    assert 2 * e not in primitive_isotropic
