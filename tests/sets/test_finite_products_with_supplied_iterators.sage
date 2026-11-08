r"""Finite products enumerate supplied factor iterators without a new ranking."""

from sage_extensions.all import *


def test_s3_times_a_singleton_has_every_group_element_once() -> None:
    group = Groups.S(3)
    singleton = Sets.Δ[0]
    product = Sets().product((group, singleton))
    points = tuple(product)
    first, second = product.projection(0), product.projection(1)

    assert product.cardinality() == cardinal(6)
    assert sum(1 for _ in points) == ZZ(6)
    assert all(sum(1 for point in points if first(point) == element) == ZZ(1) for element in group)
    assert all(second(point) == singleton(0) for point in points)
    assert product not in EnumeratedSets()


def test_a_ranked_infinite_product_keeps_its_selected_enumeration() -> None:
    product = Sets().product((NN, NN))
    ranking = product.ranking_map()
    points = iter(product)

    assert all(ranking(next(points)) == NN(position) for position in range(8))


def test_the_empty_product_has_its_unique_empty_section() -> None:
    product = Sets().product(())
    points = tuple(product)

    assert product.cardinality() == cardinal(1)
    assert sum(1 for _ in points) == ZZ(1)
    assert points[0] == product(())
