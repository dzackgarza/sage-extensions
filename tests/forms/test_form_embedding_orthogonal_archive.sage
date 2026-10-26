r"""Orthogonal complements of primitive embeddings into the hyperbolic plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_orthogonal_complement_of_the_diagonal_in_U_is_minus_two() -> None:
    r"""``<2> -> U``, ``v |-> e + f``, has complement ``Z(e - f) = <-2>``; together they have index 2.

    ``b(e + f, e - f) = 0`` and ``(e - f)^2 = -2``; ``det(<2> + <-2>) = -4``
    against ``det U = -1``.
    """
    u = Lattices(ZZ)("U")
    line = Lattices(ZZ)([[2]])
    e, f = u.basis()
    (v,) = line.basis()
    embedding = line.Mor(u)({v: e + f})

    complement = embedding.orthogonal_complement()
    (w,) = complement.basis()

    assert embedding.is_primitive()
    assert complement.module_rank() == 1
    assert complement.inclusion()(w) in (e - f, f - e)
    assert complement.is_isometric_to(Lattices(ZZ)([[-2]]))
    assert u.sublattice_from((e + f, e - f)).inclusion().index() == 2
