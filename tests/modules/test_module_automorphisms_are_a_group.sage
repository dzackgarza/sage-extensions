r"""$\operatorname{Aut}_{\mathbb Z}(\mathbb Z^2) = \operatorname{End}(\mathbb Z^2)^\times = \mathrm{GL}_2(\mathbb Z)$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_aut_z2_contains_the_swap_but_not_the_doubling() -> None:
    r"""The swap has determinant $-1$, a unit; doubling has determinant $4$, so it is injective with
    cokernel $(\mathbb Z/2)^2$ and not invertible.

    Source: Lang, Algebra, XIII.4 (an integer matrix is invertible over Z iff its determinant is ±1).
    """
    M = ZZ**2
    a, b = M.module_generator(0), M.module_generator(1)
    swap = M.End()({0: b, 1: a})
    doubling = M.End()({0: 2 * a, 1: 2 * b})
    automorphisms = M.Aut()

    assert automorphisms == M.End().unit_group()
    assert swap in automorphisms
    assert swap * swap == M.End().one()
    assert doubling not in automorphisms
    assert doubling.is_injective()
    assert not doubling.is_surjective()
    assert doubling.cokernel().cardinality() == 4
