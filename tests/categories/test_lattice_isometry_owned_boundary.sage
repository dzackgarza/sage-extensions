r"""Orthogonal groups of small integral lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_orthogonal_group_of_A2_is_dihedral_of_order_12() -> None:
    r"""``O(A2) = W(A2) x {+-1}``, dihedral of order 12 with centre ``{+-1}``.

    Conway--Sloane, *SPLAG*, ch. 4, sec. 6.4: ``|W(A2)| = 6`` and
    ``-1`` is not in ``W(A2)``.
    """
    a2 = Lattices(ZZ)("A2")
    orthogonal_group = a2.O()
    e1, e2 = a2.basis()
    minus_one = a2.Mor(a2)({e1: -e1, e2: -e2})

    assert orthogonal_group.cardinality() == 12
    assert not orthogonal_group.is_abelian()
    assert orthogonal_group.center().cardinality() == 2
    assert minus_one in orthogonal_group


def test_orthogonal_group_of_the_hyperbolic_plane_is_the_klein_four_group() -> None:
    r"""``O(U) = {1, -1, s, -s}`` for the swap ``s`` of the isotropic basis.

    An isometry permutes the two primitive isotropic lines ``Ze`` and ``Zf``
    and preserves ``b(e, f) = 1``, which leaves exactly these four.
    """
    u = Lattices(ZZ)("U")
    orthogonal_group = u.O()
    e, f = u.basis()
    swap = u.Mor(u)({e: f, f: e})
    minus_swap = u.Mor(u)({e: -f, f: -e})
    scaling = u.Mor(u)({e: 2 * e, f: f})

    assert orthogonal_group.cardinality() == 4
    assert orthogonal_group.is_abelian()
    assert swap in orthogonal_group
    assert minus_swap in orthogonal_group
    assert scaling not in orthogonal_group
    assert all(g * g == orthogonal_group.one() for g in orthogonal_group)
