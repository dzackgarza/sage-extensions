r"""Published root counts and group orders computed in a session."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sterk_published_norm_breakdown_survives_the_catalogue_split() -> None:
    r"""Counts of $(-4)$- and $(-2)$-roots in Sterk's five diagrams.

    Source: Sterk, *Compactifications of the period space of Enriques
    surfaces* I, Math. Z. 207 (1991).
    """
    expected = {
        "Sterk_1": {-4: 12, -2: 0},
        "Sterk_2": {-4: 9, -2: 1},
        "Sterk_3": {-4: 10, -2: 2},
        "Sterk_4": {-4: 9, -2: 2},
        "Sterk_5": {-4: 10, -2: 4},
    }
    assert {
        name: {norm: sum(root.q() == norm for root in roots) for norm in (-4, -2)}
        for name, roots in Sterk.sterk_roots().items()
    } == expected


def test_literature_group_orders_survive_the_known_mathematics_split() -> None:
    r"""$|W(E_8)| = 696729600$ and $|O(A_4)| = 2\,|W(A_4)| = 240$.

    Source: Bourbaki, *Lie Groups and Lie Algebras* IV–VI, Plates I and VII.
    """
    assert Groups.Weyl(["E", 8]).order() == 696729600
    assert Lattices.A4.Aut().order() == 240
