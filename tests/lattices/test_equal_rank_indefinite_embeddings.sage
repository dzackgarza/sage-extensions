from sage_extensions.all import *


def test_equal_rank_indefinite_embedding_reuses_exact_isometry_witness() -> None:
    source = Lattices(ZZ)([[0, 2], [2, 0]])
    target = Lattices(ZZ)([[0, 2], [2, 4]])

    assert source.module_rank() == target.module_rank() == 2
    assert not target.is_definite()
    assert not target.is_unimodular()

    embeddings = source.Emb(target)
    assert embeddings.is_empty() is False
    embedding = embeddings.an_element()

    assert embedding.domain() is source
    assert embedding.codomain() is target
    assert embedding.cokernel().is_zero()
    for left in source.module_generators():
        for right in source.module_generators():
            assert target.b(embedding(left), embedding(right)) == source.b(left, right)


def test_equal_rank_indefinite_nonisometry_is_an_empty_embedding_mor() -> None:
    source = Lattices(ZZ)([[0, 2], [2, 0]])
    target = Lattices(ZZ)([[0, 3], [3, 0]])

    assert source.module_rank() == target.module_rank() == 2
    assert source.discriminant() != target.discriminant()
    assert source.Emb(target).is_empty() is True
