r"""The product category $\mathbf{Set} \times \mathbf{Set}$ and the opposite $\mathbf{Set}^{\mathrm{op}}$.

A morphism of $C \times D$ is a pair of morphisms, composed and compared
componentwise, with identity the pair of identities.  On
$(\{0, 1\}, \{0, 1, 2\})$ the pair $m = (\sigma, \rho)$ of the transposition
and the rotation has $m^2 = (\mathrm{id}, \rho^2) \ne m$ and
$m^3 = (\sigma, \mathrm{id})$, because $\sigma$ has order $2$ and $\rho$
order $3$.  In $C^{\mathrm{op}}$ the identity of $X$ is the identity of $X$
in $C$, and the transposition, an involution, squares to it.  These are
the definitions of the two constructions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _transposition(two):
    return Sets().Mor(two, two)(lambda x: two(1) if x == 0 else two(0))


def _rotation(three):
    return Sets().Mor(three, three)(lambda x: three((x + 1) % 3))


def test_pairs_of_maps_compose_componentwise_in_the_product_category() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    pairs = Cat().product([Sets(), Sets()])
    point = pairs(two, three)
    endomorphisms = pairs.Mor(point, point)
    transposition = _transposition(two)
    rotation = _rotation(three)
    pair = endomorphisms((transposition, rotation))
    identity_pair = endomorphisms(
        (Sets().Mor(two, two).identity(), Sets().Mor(three, three).identity())
    )

    assert pairs.pair(two, three) is point
    assert pair * pair == endomorphisms((transposition * transposition, rotation * rotation))
    assert pair * pair != pair
    assert pair * pair * pair == endomorphisms((transposition, Sets().Mor(three, three).identity()))
    assert endomorphisms.identity() == identity_pair


def test_the_transposition_is_an_involution_in_the_opposite_category() -> None:
    two = Sets.Δ[1]
    opposite = Sets().opposite()
    endomorphisms = opposite.Mor(opposite(two), opposite(two))
    identity = endomorphisms.identity()
    transposition = endomorphisms(_transposition(two))

    assert identity == endomorphisms(Sets().Mor(two, two).identity())
    assert transposition * transposition == identity
    assert transposition != identity
