r"""The natural numbers and the finite ordinals $\Delta[n] = \{0, \dots, n\}$.

$7 \bmod 3 = 1$, $7 - 2 = 5$, $3 + 4 = 7$ and $3\cdot4=12$ in $\mathbb{N}$.
As a semiring, $\mathbb N$ is initial: every unital semiring receives its
unique morphism from $\mathbb N$.  In particular mixed arithmetic with
$\mathbb Z$ follows the canonical inclusion rather than pulling integers back
into $\mathbb N$.
$\mathbb{N}$ is enumerated as $0, 1, 2, \dots$ and ranked by the identity,
since $\mathbb{N}$ is the ordinal $\omega$ counting itself.  $\Delta[n]$ has
$n + 1$ points, so $\Delta[3]$ has $4$ and $\Delta[-1]$ is empty;
$\Delta[\aleph_0] = \mathbb{N}$.  A finite ordinal is ranked by the
identity, its $k$-th point is $k$, and it has no point at a position past
its last.  These are the definitions of the von Neumann ordinals.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_arithmetic_of_natural_numbers() -> None:
    assert NN(7) % 3 == 1
    assert NN(7) - 2 == 5
    assert 3 + NN(4) == 7
    assert NN(3) * NN(4) == NN(12)
    assert 10 - NN(4) == 6


def test_natural_numbers_are_the_initial_owned_semiring() -> None:
    semirings = OwnedSemirings()

    assert NN in semirings
    assert semirings.initial_object() is NN
    assert NN.category().is_subcategory(NN.category()._meet_(ZZ.category()))

    for target in (ZZ, QQ):
        canonical = semirings.initial_morphism(target)
        assert canonical.domain() is NN
        assert canonical.codomain() is target
        assert canonical(NN(0)) == target.zero()
        assert canonical(NN(5)) == target(5)


def test_mixed_natural_and_integer_arithmetic_uses_the_initial_map() -> None:
    canonical = ZZ.coerce_map_from(NN)

    assert canonical(NN(3)) == ZZ(3)
    assert (NN(2) + ZZ(3)).parent() is ZZ
    assert NN(2) + ZZ(3) == ZZ(5)
    assert (NN(2) * ZZ(3)).parent() is ZZ
    assert NN(2) * ZZ(3) == ZZ(6)
    assert NN(2) - ZZ(3) == ZZ(-1)


def test_the_natural_numbers_are_listed_and_ranked_in_order() -> None:
    listing = iter(NN)

    assert [next(listing) for _step in range(3)] == [0, 1, 2]
    assert NN.ranking_map()(NN(5)) == 5


def test_the_standard_simplices_have_one_more_point_than_their_dimension() -> None:
    assert Sets.Δ[cardinal(3)].cardinality() == cardinal(4)
    assert Sets.Δ[-1].cardinality() == cardinal(0)
    assert Sets.Δ[aleph0] is NN


def test_a_finite_ordinal_is_ranked_by_the_identity() -> None:
    five = Sets.Δ[4]
    ranking = five.ranking_map()

    assert five[2] == 2
    assert ranking(five(3)) == 3
    assert ranking.inverse()(3) == five(3)
    with pytest.raises(IndexError):
        five[7]
