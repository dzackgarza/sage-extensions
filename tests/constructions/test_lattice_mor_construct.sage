r"""Lattice Mor objects construct and compose form-preserving maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_embedding_into_the_hyperbolic_plane() -> None:
    root_lattice = Lattices(ZZ)("A1")
    plane = Lattices(ZZ)("U")
    (root,) = root_lattice.module_generators()
    e, f = plane.module_generators()
    morphisms = root_lattice.Mor(plane)
    embedding = morphisms((e - f,))

    assert embedding.parent() is morphisms
    assert embedding.domain() is root_lattice
    assert embedding.codomain() is plane
    assert embedding(root) == e - f
    assert embedding(root) * embedding(root) == root * root


def test_identity_and_composition_in_lattice_mor() -> None:
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()
    morphisms = plane.Mor(plane)
    identity = morphisms.identity()
    swap = morphisms((f, e))

    assert identity(e) == e
    assert identity(f) == f
    assert (swap * swap) == identity
