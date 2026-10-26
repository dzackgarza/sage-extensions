r"""Base change of an integral form to a field: where the form stays nondegenerate."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_stays_nondegenerate_over_QQ_and_GF2_and_degenerates_over_GF3() -> None:
    r"""``det A2 = 3``, so ``A2 (x) F_p`` is degenerate exactly for ``p = 3``.

    The radical over ``F_3`` is the line spanned by ``e1 - e2``: modulo 3 the
    Gram matrix ``+-[[2, -1], [-1, 2]]`` has all entries equal.
    """
    a2 = Lattices(ZZ)("A2")
    over_rationals = a2.vector_space()
    over_two = a2.base_change(ZZ.Mor(GF(2))(lambda n: GF(2)(n)))
    over_three = a2.base_change(ZZ.Mor(GF(3))(lambda n: GF(3)(n)))

    assert a2.determinant() == 3
    assert over_rationals.dimension() == 2
    assert over_rationals.is_nondegenerate()
    assert over_two.is_nondegenerate()
    assert not over_three.is_nondegenerate()
    assert over_three.radical().dimension() == 1
    assert over_three.radical_quotient().dimension() == 1
    assert over_three.radical_quotient().is_nondegenerate()
