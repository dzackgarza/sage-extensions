r"""The character table of $S_3$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_character_table_of_s3() -> None:
    r"""On the classes of $1$, a transposition and a $3$-cycle, the irreducible characters of $S_3$ take the values $(1, 1, 1)$, $(1, -1, 1)$ and $(2, 0, -1)$.

    Source: Fulton–Harris, *Representation Theory*, §2.3.
    """
    group = Groups.S(3)
    transposition = next(g for g in group if g.order() == 2)
    three_cycle = next(g for g in group if g.order() == 3)
    table = sorted(
        (character(group.one()), character(transposition), character(three_cycle))
        for character in group.irreducible_characters()
    )

    assert table == [(1, -1, 1), (1, 1, 1), (2, 0, -1)]
