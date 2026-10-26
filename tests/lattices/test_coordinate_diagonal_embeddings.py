from sage_extensions.all import *


def coordinate_rows(morphism):
    domain = morphism.domain()
    codomain = morphism.codomain()
    source_labels = tuple(domain.module_generating_set())
    target_labels = tuple(codomain.module_generating_set())
    return tuple(
        tuple(
            int(
                codomain.framing_morphism().lift(
                    morphism(domain.module_generator(source_label))
                )(target_label)
            )
            for source_label in source_labels
        )
        for target_label in target_labels
    )


def test_coordinate_diagonal_embeddings_are_typed_similarities():
    category = Lattices(ZZ)
    line = category([[1]])
    plane = category([[1, 0], [0, 1]])

    embeddings = category.coordinate_diagonal_embeddings((line, plane))

    found = [
        (int(scale), parts, coordinate_rows(embedding))
        for source, target, scale, embedding, parts in embeddings
        if source is line and target is plane
    ]
    assert found == [
        (1, ((0,),), ((1,), (0,))),
        (2, ((0, 1),), ((1,), (1,))),
    ]
    assert all(
        embedding.domain().gram_tensor() == scale * source.gram_tensor()
        and embedding.codomain() is target
        for source, target, scale, embedding, _parts in embeddings
    )
