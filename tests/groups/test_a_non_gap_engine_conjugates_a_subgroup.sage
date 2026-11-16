r"""A conjugation computed by an engine that has no GAP model of its elements.

$A = \mathbb{Z}/2 \oplus \mathbb{Z}/4$ is realized by its invariants: its
elements are positions in that direct sum, not GAP permutations or words.  The
engine conjugates a subgroup's own generators in its own product, which is the
operation the group has; conjugating by an element of an abelian group carries
every subgroup to itself, so the answer is the subgroup on one generator of
order two.

Reading the conjugating element through a GAP model instead refuses the
operation before the engine's own conjugation is reached.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_non_gap_engine_conjugates_a_subgroup() -> None:
    r"""$A$ is abelian, so $g H g^{-1} = H$ for its subgroup of order two."""
    group = Groups.Abelian([2, 4])
    short, long = tuple(group.group_generators())
    subgroup = group.subgroup((short,))

    conjugate = group.conjugate_subgroup(long, subgroup)

    assert conjugate.order() == 2
    assert short in conjugate
    assert long not in conjugate
