r"""Orthogonal decomposition of definite lattices into indecomposable summands."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_plus_a1_decomposes_orthogonally_but_a2_is_indecomposable() -> None:
    r"""A definite lattice is uniquely an orthogonal sum of indecomposables.

    $A_1 \oplus A_1$ has two summands, each isometric to $A_1$; the root
    lattice $A_2$ is indecomposable, although it contains $A_1$.  Source:
    Kneser, *Quadratische Formen*, Satz 27.2 (Eichler).
    """
    a1 = Lattices(ZZ)("A1")
    a2 = Lattices(ZZ)("A2")
    summands = (a1 + a1).orthogonal_decomposition()

    assert summands.cardinality() == 2
    assert all(summand.is_isometric_to(a1) for summand in summands)
    assert a2.orthogonal_decomposition().cardinality() == 1
    assert not a2.is_isometric_to(a1 + a1)
