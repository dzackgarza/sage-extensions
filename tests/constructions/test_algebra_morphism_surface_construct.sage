r"""An algebra identity retains the selected generator map and generator images."""

from sage_extensions.all import *  # noqa: F401,F403


def _polynomial_algebra_identity():
    algebra = QQ.polynomial_ring("x")
    identity = algebra.Mor(algebra).identity()
    return algebra, identity


def test_algebra_identity_retains_generator_images() -> None:
    algebra, identity = _polynomial_algebra_identity()
    labels = algebra.algebra_generating_set()
    label = labels[0]
    x = algebra.algebra_generator(label)
    images = identity.algebra_generator_images()

    assert images.index_set() is labels
    assert images[label] == x


def test_algebra_identity_retains_generator_morphism() -> None:
    algebra, identity = _polynomial_algebra_identity()
    labels = algebra.algebra_generating_set()
    label = labels[0]
    x = algebra.algebra_generator(label)
    generator_map = identity.algebra_generator_morphism()

    assert generator_map.domain() is labels
    assert generator_map.codomain() is algebra
    assert generator_map(label) == x
