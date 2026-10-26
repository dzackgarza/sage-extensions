from sage_extensions.all import *


def test_chosen_target_embedding_filters_a_nontrivial_genus() -> None:
    r"""A literal target is selected even when its genus has several classes.

    The indefinite forms ``[1,15,-1]`` and ``[3,13,-5]`` have fundamental
    discriminant ``229``.  That discriminant has one genus and class number
    greater than one, so their Gram matrices represent distinct classes in a
    non-singleton genus.  The first contains the primitive square-two vector
    ``e_0``.  The chosen-target embedding must therefore be constructed in
    that literal lattice rather than refused merely because its genus has more
    than one class.
    """
    source = Lattices(ZZ)([[2]])
    target = Lattices(ZZ)([[2, 15], [15, -2]])
    other_class = Lattices(ZZ)([[6, 13], [13, -10]])

    assert target.Isom(other_class).is_empty() is True

    embedding = source.Emb(target).an_element()

    assert embedding.domain() is source
    assert embedding.codomain() is target
    assert embedding.is_primitive()
    generator = source.basis_vector(0)
    assert embedding(generator).q() == generator.q()


