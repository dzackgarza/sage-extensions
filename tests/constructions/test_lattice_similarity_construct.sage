r"""An explicit lattice similarity is an isometry out of the scaled lattice."""

from sage_extensions.all import *  # noqa: F401,F403


def test_scale_one_similarity_from_explicit_images_is_the_identity_isometry() -> None:
    lattice = NamedLattices.U
    e, f = lattice.module_generators()
    similarity = lattice.similarity(ZZ.one(), images=(e, f))
    source = lattice.twist(ZZ.one())

    assert similarity.domain() == source
    assert similarity.codomain() is lattice
    assert similarity(source.module_generator(0)) == e
    assert similarity(source.module_generator(1)) == f


def test_scale_one_similarity_uses_the_similarity_mor() -> None:
    lattice = NamedLattices.U
    e, f = lattice.module_generators()
    similarity = lattice.similarity(ZZ.one(), images=(e, f))

    assert similarity.parent() == lattice.similarity_mor(lattice, ZZ.one())
