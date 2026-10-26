r"""Vector spaces expose their represented basis and dimension.

The standard plane over ``QQ`` has two selected basis labels and dimension two;
its linear identity fixes both basis vectors.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_rational_plane_has_two_basis_labels_and_dimension_two() -> None:
    space = QQ.free_module(2)
    labels = space.basis_generator_labels()

    assert space in VectorSpaces(QQ)
    assert space in Modules(QQ)
    assert space.dimension() == 2
    assert labels.cardinality() == cardinal(2)
    assert isinstance(space.module_generator(labels[0]), space.ElementType)


def test_vector_space_morphisms_have_identity() -> None:
    space = QQ.free_module(2)
    identity = space.Mor(space).identity()

    assert identity(space.module_generator(0)) == space.module_generator(0)
    assert identity * identity == identity
