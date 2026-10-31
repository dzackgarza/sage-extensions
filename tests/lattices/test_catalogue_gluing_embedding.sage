r"""The ``U + E8(2)`` gluing into ``U + U(2) + E8(2)``, checked on every pairing.

The retained map is pinned exactly, not up to isometry: source positions
``0, 1`` are the hyperbolic plane and go to the target's ``e, f``, and source
positions ``2 .. 9`` are the ``E8(2)`` block in the owned Cartan order and go to
the target's ``a1 .. a8`` through the order change.  Every pairing of the
source basis is then compared with the pairing of its images, and the inclusion
is checked for injectivity and primitivity.
"""

from sage_extensions.all import *

from sage_extensions.catalogue import _SAGE_E8_POSITION


def test_the_gluing_embedding_is_pinned_on_the_declared_ordered_bases() -> None:
    source = NamedLattices.U_E8_2
    target = NamedLattices.TEn
    embedding = Embeddings.U_E8_2_into_TEn

    assert embedding.domain() is source
    assert embedding.codomain() is target
    # The target's declared ordered basis.
    assert tuple(map(str, target.module_generating_set())) == (
        "e", "f", "ep", "fp", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
    )
    target_labels = tuple(target.module_generating_set())
    source_labels = tuple(source.module_generating_set())
    assert len(source_labels) == 10

    expected = (
        target.module_generator(target_labels[0]),
        target.module_generator(target_labels[1]),
        *(
            target.module_generator(target_labels[4 + _SAGE_E8_POSITION[index]])
            for index in range(8)
        ),
    )
    # The image of each source basis vector is exactly the stated generator of
    # the target's declared basis: the map is pinned, not merely isometric.
    assert tuple(
        embedding(source.module_generator(label)) for label in source_labels
    ) == expected

    # Every pairing of the source basis is the pairing of its images.  For the
    # E8 block this is `a_i . a_j = a_{pos(i)} . a_{pos(j)}`, which holds only
    # because both sides are read in their own declared order.
    for left in source.module_generators():
        for right in source.module_generators():
            assert left.b(right) == embedding(left).b(embedding(right))

    assert embedding.is_injective()
    assert embedding.is_primitive()
