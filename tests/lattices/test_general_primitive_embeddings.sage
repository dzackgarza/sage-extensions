r"""Primitive embeddings of ``A1`` into the non-unimodular lattice ``U + A1``.

``A1`` is negative definite here: its generator has norm ``-2``.
"""

from sage_extensions.all import *


def test_two_primitive_embeddings_of_a1_into_u_plus_a1_have_nonisometric_complements() -> None:
    r"""In ``T = U + A1`` with basis ``e, f, a``, both ``a`` and ``e - f`` are
    primitive of norm ``-2``.  Their complements are ``U`` (determinant ``-1``)
    and ``ZZ(e + f) + ZZa = <2> + <-2>`` (determinant ``-4``), so the two
    embeddings lie in different ``O(T)``-orbits.  Derived by hand: ``w`` is
    orthogonal to ``e - f`` iff its ``e`` and ``f`` coefficients agree.
    """
    source = Lattices(ZZ)("A1")
    target = Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    (root,) = source.module_generators()
    e, f, a = target.module_generators()

    summand = source.Emb(target)({root: a})
    diagonal = source.Emb(target)({root: e - f})

    assert summand.is_primitive()
    assert diagonal.is_primitive()
    assert target.b(e - f, e - f) == source.b(root, root) == -2
    assert summand(root).orthogonal_complement().determinant() == -1
    assert diagonal(root).orthogonal_complement().determinant() == -4
    assert source.Emb(target).primitive_embedding_class_representatives("emb").cardinality() >= 2
