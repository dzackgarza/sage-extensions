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
comparison they represent.  The answers are therefore properties of the two
orders and not of a second copy of the operation on their own classes.
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


def test_the_order_supplies_its_own_emptiness_after_any_earlier_construction() -> None:
    r"""Both thin orders decide the emptiness of their own hom-sets.

    ``Sets`` owns ``is_empty`` and reads what a construction supplies through
    the protected hook ``_emptiness_decision``, which a level states on its own
    class.  A thin order states it there, so its hom-set is answered by the
    negation of the order's own comparison and not by whatever a class
    resolution reached by an earlier construction selected.  The two orders are
    asked here after each other, each through the order's own ``Mor`` and
    through the cached hom-set, and every answer is the same decision.

    An undecided comparison decides nothing, and no order may answer ``False``
    for a hom-set it has not decided: the set states the proposition
    ``is_empty`` and ``ask`` answers ``Unknown``.
    """
    cardinals = Cardinalities()
    ordinals = Ordinals()

    assert ordinals.Mor(1, 2).is_empty() is False
    assert cardinals.Mor(2, 3).is_empty() is False
    assert cardinal(2).Mor(3).is_empty() is False
    assert cardinals.Mor(2, 3).is_empty() is False
    assert cardinals.Mor(3, 2).is_empty() is True
    assert ordinals.Mor(1, 2).is_empty() is False
    assert ordinals.Mor(2, 1).is_empty() is True

    undecided = cardinals.Mor(2 ** aleph0, aleph(1))
    assert ask(undecided.is_empty()) is Unknown


def test_the_one_cardinal_arrow_composes_as_the_comparison_does() -> None:
    cardinals = Cardinalities()

    two_three = cardinals.Mor(2, 3).unique_morphism()
    three_five = cardinals.Mor(3, 5).unique_morphism()
    four_five = cardinals.Mor(4, 5).unique_morphism()

    assert three_five * two_three == cardinals.Mor(2, 5).unique_morphism()
    assert cardinals.sum_morphism(two_three, four_five) == cardinals.Mor(6, 8).unique_morphism()
    assert cardinals.product_morphism(two_three, four_five) == cardinals.Mor(8, 15).unique_morphism()


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
