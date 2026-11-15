r"""Round 5's two red states at the base HEAD, printed rather than asserted."""
from collections.abc import Hashable

from sage.all import QQ, vector

from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family


class UnhashablePoint(tuple):
    __hash__ = None


factor = Sets.Δ[1]
keyless_labels = finite_ordered_set((UnhashablePoint((1, 2)),))
keyed_labels = finite_ordered_set(((1, 2),))
keyless = indexed_family(keyless_labels, lambda label: factor)
keyed = indexed_family(keyed_labels, lambda label: factor)
print("equal families:", keyless == keyed)


def one_product(first, second, order):
    product = Sets().product(first)
    again = Sets().product(second)
    print(f"{order}: product(first) is product(second) ->", product is again)


one_product(keyless, keyed, "keyless first")
one_product(keyed, keyless, "keyed first")

v, w = vector(QQ, [1, 2]), vector(QQ, [3, 4])
print("mutable vector isinstance Hashable:", isinstance(v, Hashable))
try:
    hash(v)
except Exception as error:
    print("hash(mutable vector) raises:", type(error).__name__, error)
S = finite_ordered_set((v, w))
T = S.filtered(lambda point: True)
print("T points:", tuple(T), "points_have_a_hash:", T.points_have_a_hash())
family = indexed_family(T, lambda point: factor)
try:
    product = Sets().product(family)
except Exception as error:
    print("product over the filtered mutable-vector index raises:", type(error).__name__, error)
else:
    print("product over the filtered mutable-vector index built:", product)
