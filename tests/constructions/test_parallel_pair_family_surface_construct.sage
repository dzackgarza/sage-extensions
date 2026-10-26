r"""Parallel-pair and parallel-family shapes expose their arrows and owners."""

from sage_extensions.all import *  # noqa: F401,F403


def test_equalizer_parallel_pair_arrows_retain_names_and_shape() -> None:
    source = Sets.Δ[2]
    target = Sets.Δ[1]
    left = Sets().Mor(source, target)(lambda point: target(int(point) % 2))
    right = Sets().Mor(source, target)(lambda _point: target(0))
    shape = Sets().equalizer_construction(left, right).diagram().domain()
    arrows = shape.Mor(shape.source(), shape.target())

    assert arrows.parallel_pair_category() is shape
    assert shape.left().name() == "left"
    assert shape.right().name() == "right"
    assert not shape.left().is_identity()
    assert shape.identity(shape.source()).is_identity()


def test_wide_equalizer_parallel_family_arrows_retain_labels_and_shape() -> None:
    source = Sets.Δ[2]
    target = Sets.Δ[1]
    first = Sets().Mor(source, target)(lambda point: target(int(point) % 2))
    second = Sets().Mor(source, target)(lambda _point: target(0))
    construction = Sets().equalizer_of_family_construction((first, second))
    diagram = construction.diagram()
    shape = diagram.domain()
    arrows = shape.Mor(shape.source(), shape.target())
    labels = tuple(shape.index_set())

    assert arrows.parallel_family_category() is shape
    assert diagram.morphisms().cardinality() == cardinal(2)
    assert diagram.reference() in (first, second)
    assert shape.arrow(labels[0]).label() == labels[0]
    assert not shape.arrow(labels[0]).is_identity()
    assert shape.identity(shape.source()).is_identity()
