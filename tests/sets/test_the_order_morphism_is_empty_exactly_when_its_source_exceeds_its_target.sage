r"""In $\mathbf{Card}$ and $\mathbf{Ord}$ the hom-set $\kappa \to \lambda$ is empty exactly when $\kappa > \lambda$.

Both categories are thin: there is one arrow $\kappa \to \lambda$ exactly
when $\kappa \le \lambda$.  So the hom-set holds one arrow or none, and
its emptiness, its cardinality and its unique arrow are one
mathematical fact read three ways: $3 \nleq 2$, so
$\operatorname{Mor}(3, 2)$ is empty, has cardinality $0$ and contains no
arrow to return, while $\operatorname{Mor}(2, 3)$ holds the one arrow
$2 \le 3$ and $\operatorname{Mor}(3, 3)$ its identity.

The emptiness and the cardinality of a set are read through the
protected hooks a realization supplies on its own class
(``set_categories.Sets.ParentMethods._emptiness_decision`` and
``_cardinality_decision``), and the two orders supply theirs from the
comparison they represent.  So the answers are properties of the two
orders and of nothing else: the last test builds the hom-sets before
and after the constructions the rest of the set tests make, and asks
for the same decisions again on freshly built hom-sets.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_a_cardinal_order_morphism_exists_exactly_below_its_target() -> None:
    cardinals = Cardinalities()

    below = cardinals.Mor(2, 3)
    equal = cardinals.Mor(3, 3)
    above = cardinals.Mor(3, 2)

    assert below.is_empty() is False
    assert equal.is_empty() is False
    assert above.is_empty() is True
    assert below.cardinality() == cardinal(1)
    assert equal.cardinality() == cardinal(1)
    assert above.cardinality() == cardinal(0)
    assert equal.identity() == equal.unique_morphism()
    with pytest.raises(ValueError):
        above.unique_morphism()


def test_the_one_cardinal_arrow_composes_as_the_comparison_does() -> None:
    cardinals = Cardinalities()

    two_three = cardinals.Mor(2, 3).unique_morphism()
    four_five = cardinals.Mor(4, 5).unique_morphism()

    assert four_five * two_three == cardinals.Mor(2, 5).unique_morphism()
    assert cardinals.sum_morphism(two_three, four_five) == cardinals.Mor(6, 8).unique_morphism()


def test_an_ordinal_order_morphism_exists_exactly_below_its_target() -> None:
    ordinals = Ordinals()

    below = ordinals.Mor(1, 2)
    equal = ordinals.Mor(2, 2)
    above = ordinals.Mor(2, 1)

    assert below.is_empty() is False
    assert equal.is_empty() is False
    assert above.is_empty() is True
    assert below.cardinality() == cardinal(1)
    assert above.cardinality() == cardinal(0)
    assert equal.identity() == equal.unique_morphism()
    with pytest.raises(ValueError):
        above.unique_morphism()


def test_the_two_orders_decide_the_same_before_and_after_the_other_set_constructions() -> None:
    r"""The decisions are the orders', not the session's history.

    The hom-sets are asked first, then the constructions the sibling set
    tests make are performed, and then the same questions are asked of
    freshly built hom-sets and through the second route
    ``cardinal(4).Mor(5)``.
    """
    cardinals = Cardinalities()
    ordinals = Ordinals()
    decisions = (False, True, False, True)

    first = (
        cardinals.Mor(2, 3).is_empty(),
        cardinals.Mor(3, 2).is_empty(),
        ordinals.Mor(1, 2).is_empty(),
        ordinals.Mor(2, 1).is_empty(),
    )

    ordinal_three = Sets.Δ[2]
    ordered = finite_ordered_set(("a", "b"))
    naturals = NN
    rationals = QQ
    integers = ZZ
    continuum = cardinal(2) ** aleph0
    first_infinite = omega(0)

    later = (
        cardinals.Mor(4, 5).is_empty(),
        cardinals.Mor(5, 4).is_empty(),
        ordinals.Mor(3, 4).is_empty(),
        ordinals.Mor(4, 3).is_empty(),
    )

    assert first == decisions
    assert later == decisions
    assert cardinal(4).Mor(5).is_empty() is False
    assert cardinal(5).Mor(4).is_empty() is True
    assert ordinals(3).Mor(first_infinite).is_empty() is False
    assert ordinals(first_infinite).Mor(3).is_empty() is True
    assert ordinal_three.cardinality() == cardinal(3)
    assert ordered.cardinality() == cardinal(2)
    assert naturals.cardinality() == aleph0
    assert rationals.cardinality() == aleph0
    assert integers.cardinality() == aleph0
    assert continuum.cardinality() == continuum
