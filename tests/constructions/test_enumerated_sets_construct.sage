r"""A finite ordinal is an enumerated set ranked by its own order."""

from sage_extensions.all import *  # noqa: F401,F403


def test_finite_ordinal_is_enumerated() -> None:
    ordinal_two = EnumeratedSets().an_object()

    assert ordinal_two in EnumeratedSets()
    assert ordinal_two.cardinality() == cardinal(2)
    assert ordinal_two.ranking_map()(ordinal_two[1]) == NN(1)
