r"""A functor category retains its endpoints and builds diagrams from object families."""

from sage_extensions.all import *  # noqa: F401,F403


def test_discrete_functor_category_retains_endpoints_and_factor_family() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    product_diagram = Sets().product_construction((two, three)).diagram()
    index = product_diagram.domain()
    factors = product_diagram.diagram_objects()
    diagrams = Cat().Mor(index, Sets())
    rebuilt = diagrams.discrete_diagram(factors)

    assert diagrams.domain_category() is index
    assert diagrams.codomain_category() is Sets()
    assert rebuilt.diagram_objects() is factors
    assert rebuilt(index(0)) is two
    assert rebuilt(index(1)) is three
