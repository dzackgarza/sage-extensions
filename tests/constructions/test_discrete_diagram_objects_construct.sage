r"""A discrete product diagram retains the indexed family of its factors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_binary_product_diagram_exposes_its_factor_family() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    diagram = Sets().product_construction((two, three)).diagram()
    factors = diagram.diagram_objects()
    labels = tuple(factors.index_set())

    assert factors.cardinality() == cardinal(2)
    assert factors[labels[0]] is two
    assert factors[labels[1]] is three
