r"""Item 1: both construction orders, each against a cleared interner."""
from sage_extensions.categories.sets import set_categories
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family


class UnhashablePoint(tuple):
    __hash__ = None


factor = Sets.Δ[1]


def pair():
    keyless_labels = finite_ordered_set((UnhashablePoint((1, 2)),))
    keyed_labels = finite_ordered_set(((1, 2),))
    keyless = indexed_family(keyless_labels, lambda label: factor)
    keyed = indexed_family(keyed_labels, lambda label: factor)
    assert keyless == keyed, "the two families are not equal"
    return keyless, keyed


def reset():
    set_categories._FINITE_PRODUCTS = ({}, {})
    set_categories._FINITE_COPRODUCTS = ({}, {})


for order in ("keyless first", "keyed first"):
    for operation in ("product", "coproduct"):
        reset()
        keyless, keyed = pair()
        first, second = (keyless, keyed) if order == "keyless first" else (keyed, keyless)
        build = Sets().product if operation == "product" else Sets().coproduct
        one = build(first)
        two = build(second)
        print(f"{operation}, {order}: one object ->", one is two)
