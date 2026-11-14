r"""The ``U + E8(2)`` adapted gluing, the archived map and Sterk 5's fourteen roots.

The archived catalogue (`archives/preamble/catalogue.sage` at ``24dc7a61``)
states this arrow as an adapted basis, not a block inclusion:

    e~ = e + e' + f' - a1,   f~ = f + e' + f' - a1,
    a1~ = e' - f',           a3~ = f' + a3,   a_i~ = a_i otherwise.

Its Gram is exactly ``U + E8(2)`` inside ``T_En``, and it is what makes Sterk 5's
fourteen roots in the standalone ``U + E8(2)`` the same configuration as their
``T_En`` presentation.  The check is on the retained map: the images of the ten
source basis vectors, every one of their hundred pairings, the fourteen
transported roots with all of their pairings, and injectivity and primitivity.
"""

from sage_extensions.all import *

from sage_extensions.sterk import Sterk


def _embedding_and_bases():
    source = NamedLattices.U_E8_2
    target = NamedLattices.TEn
    embedding = Embeddings.U_E8_2_into_TEn
    assert embedding.domain() is source
    assert embedding.codomain() is target
    return source, target, embedding


def test_the_adapted_images_are_the_archived_expressions() -> None:
    source, target, embedding = _embedding_and_bases()
    ten = tuple(target.module_generators())
    e, ep, fp, a1 = ten[0], ten[2], ten[3], ten[4]
    a3 = ten[6]
    expected = (
        e + ep + fp - a1,
        ten[1] + ep + fp - a1,
        ep - fp,
        ten[5],
        fp + a3,
        *ten[7:12],
    )
    assert tuple(
        embedding(source.module_generator(label))
        for label in source.module_generating_set()
    ) == expected


def test_every_pairing_of_the_source_basis_is_the_pairing_of_its_image() -> None:
    source, _target, embedding = _embedding_and_bases()
    for left in source.module_generators():
        for right in source.module_generators():
            assert left.b(right) == embedding(left).b(embedding(right))
    assert embedding.is_injective()
    assert embedding.is_primitive()


def test_sterk_five_fourteen_roots_transport_with_their_pairings() -> None:
    source, _target, embedding = _embedding_and_bases()
    lattice, roots = Sterk.sterk5_in_U_E8_2()
    assert lattice is source
    images = tuple(embedding(root) for root in roots)
    assert len(images) == 14
    for root, image in zip(roots, images):
        assert root.is_root()
        assert image.is_root()
        assert image.q() == root.q()
    for left_root, left_image in zip(roots, images):
        for right_root, right_image in zip(roots, images):
            assert left_root.b(right_root) == left_image.b(right_image)
