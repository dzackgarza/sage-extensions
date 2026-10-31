r"""The module product assembles and projects its elements.

A product is given by its projections and its universal property, not by a
basis; its factors may be an enumerated family or one repeated factor. The
assembly and projection operations read the factors from the product's diagram
either way, and they keep the parent identity of the product they were asked
for.
"""

from sage_extensions.all import *

from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.indexed_families import IndexedFamily


def test_a_constant_family_product_assembles_its_elements_and_projects_them() -> None:
    ring = QQ
    factor = ring.regular_module()
    labels = NN
    construction = Modules(ring)._categorical_product_construction(
        IndexedFamily(labels, factor)
    )
    product = construction.object()
    unit = factor(ring.one())

    element = Modules(ring).product_element(
        construction, IndexedFamily(labels, lambda _index: unit)
    )

    assert element.parent() is product
    assert Modules(ring).product_component(construction, element, NN(0)) == unit
    assert Modules(ring).product_component(construction, element, NN(5)) == unit


def test_a_product_rejects_components_indexed_by_another_set() -> None:
    ring = QQ
    factor = ring.regular_module()
    construction = Modules(ring)._categorical_product_construction(
        IndexedFamily(NN, factor)
    )
    for wrong_labels in (Sets.Δ[2], ZZ):
        try:
            Modules(ring).product_element(
                construction,
                IndexedFamily(wrong_labels, lambda _index: factor(ring.one())),
            )
        except ValueError:
            continue
        raise AssertionError(
            f"a product over {NN} accepted components indexed by {wrong_labels}"
        )
