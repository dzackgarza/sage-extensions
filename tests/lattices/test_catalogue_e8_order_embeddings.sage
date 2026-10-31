r"""Named embeddings match the named E8 bases, not their positions.

Some catalogue lattices name their E8 blocks in Sage's integral-lattice basis
order and others in the owned Cartan order.  The permutation between them is a
basis change of the same form, so an embedding between the two must follow it;
keeping positions would send adjacent named roots to non-adjacent ones and the
image would not preserve the pairing.
"""

from sage_extensions.all import *

from sage_extensions.catalogue import _SAGE_E8_BASIS_ORDER, _SAGE_E8_POSITION


def test_the_e8_order_change_is_a_permutation_and_its_own_inverse() -> None:
    assert sorted(_SAGE_E8_BASIS_ORDER) == list(range(8))
    assert sorted(_SAGE_E8_POSITION) == list(range(8))
    for owned in range(8):
        assert _SAGE_E8_BASIS_ORDER[_SAGE_E8_POSITION[owned]] == owned


def test_the_tdp_to_lk3_embedding_preserves_the_e8_adjacency() -> None:
    tdp = NamedLattices.TdP
    lk3 = NamedLattices.LK3
    embedding = Embeddings.TdP_into_LK3
    labels = tuple(tdp.module_generating_set())
    roots = [label for label in labels if str(label).startswith("a")]
    assert len(roots) == 8
    first = tdp.module_generator(roots[0])
    second = tdp.module_generator(roots[1])
    assert first.b(second) == embedding(first).b(embedding(second))
    assert embedding.is_injective()
    assert embedding.is_primitive()


def test_the_e8_two_into_tdp_embedding_preserves_the_e8_adjacency() -> None:
    source = NamedLattices.E8_2
    embedding = Embeddings.E8_2_into_TdP
    labels = tuple(source.module_generating_set())
    first = source.module_generator(labels[0])
    second = source.module_generator(labels[1])
    assert first.b(second) == embedding(first).b(embedding(second))
    assert embedding.is_injective()
    assert embedding.is_primitive()
