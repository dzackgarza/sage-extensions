r"""The isomorphisms between two sets are counted where the core counts them.

``Sets().Iso(A, B)`` classifies exactly the arrows of ``Sets().Core().Mor(A, B)``
— an arrow of it is, by its own definition, an isomorphism of the base category
between those endpoints — so the two sets of arrows are one set, and its
cardinality is the core's: ``m!`` when ``|A| = |B| = m`` because a bijection is a
chosen ordering of the images, and ``0`` when the cardinalities differ because
no bijection exists.  The category answered neither name before, while the
plain ``Mor`` and ``End`` answered: this pins that the isomorphism class of a
morphism is counted on the same route as the morphisms it sits inside.

Where the core states no count the cardinality is not invented: the infinite
case is a cardinal-exponentiation identity (``|A|^|A|``), not a computation this
layer performs, and it stays refused.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_isomorphisms_between_finite_sets_count_as_the_core_does() -> None:
    two = Set((1, 2))
    three = Set((1, 2, 3))

    assert Sets().Iso(two, three).cardinality() == cardinal(0)
    assert Sets().Iso(three, two).cardinality() == cardinal(0)
    assert Sets().Iso(two, two).cardinality() == cardinal(2)
    assert Sets().Iso(three, three).cardinality() == cardinal(6)


def test_the_iso_category_and_the_core_mor_count_the_same_arrows() -> None:
    three = Set((1, 2, 3))
    four = Set((1, 2, 3, 4))

    assert Sets().Iso(three, four).cardinality() == Sets().Core().Mor(three, four).cardinality()
    assert Sets().Iso(three, three).cardinality() == Sets().Core().Mor(three, three).cardinality()
    assert Sets().Iso(four, four).cardinality() == cardinal(24)


def test_a_set_that_the_core_does_not_count_is_refused() -> None:
    naturals = Sets().Infinite().an_object()

    with pytest.raises(AssertionError):
        Sets().Iso(naturals, naturals).cardinality()
