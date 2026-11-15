r"""Round 5's four statements at the repaired tree, printed rather than asserted."""
from sage.all import QQ, vector

from sage_extensions.categories.sets import set_categories
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.logic import AtomicProposition


class UnhashablePoint(tuple):
    __hash__ = None


factor = Sets.Δ[1]


def reset():
    set_categories._FINITE_PRODUCTS = set_categories.defaultdict(list)
    set_categories._FINITE_COPRODUCTS = set_categories.defaultdict(list)


def pair(factor):
    unhashable = indexed_family(finite_ordered_set((UnhashablePoint((1, 2)),)), lambda label: factor)
    hashed = indexed_family(finite_ordered_set(((1, 2),)), lambda label: factor)
    assert unhashable == hashed
    return unhashable, hashed


for order in ("unhashable first", "hashable first"):
    for name in ("product", "coproduct"):
        reset()
        unhashable, hashed = pair(factor)
        first, second = (unhashable, hashed) if order == "unhashable first" else (hashed, unhashable)
        build = Sets().product if name == "product" else Sets().coproduct
        print(f"{name}, {order}: one object ->", build(first) is build(second))

# A factor that refuses a hash: the family still interns.
reset()
list_factor = lambda label: finite_ordered_set(([label],))
left = indexed_family(finite_ordered_set((0, 1)), list_factor)
right = indexed_family(finite_ordered_set((0, 1)), list_factor)
print("unhashable-factor product interns ->", Sets().product(left) is Sets().product(right))

# The repair's second item, with mutable QQ vectors as the index points.
reset()
v, w = vector(QQ, [1, 2]), vector(QQ, [3, 4])
S = finite_ordered_set((v, w))
T = S.filtered(lambda point: True)
family = indexed_family(T, lambda point: factor)
product = Sets().product(family)
again = indexed_family(S.filtered(lambda point: True), lambda point: factor)
print("filtered mutable-vector product built:", product, "| factor(v) is factor ->",
      product.factor(v) is factor, "| two equal families one product ->",
      Sets().product(again) is product)

# Undecided family equality inside one bucket.
class SymbolicPoint:
    def __eq__(self, other):
        return AtomicProposition("equal_symbolic_points", self, other)


reset()
labels = finite_ordered_set((0, 1))
first_factor = finite_ordered_set((SymbolicPoint(),))
second_factor = finite_ordered_set((SymbolicPoint(),))
first = indexed_family(labels, lambda label: first_factor if label == 0 else factor)
second = indexed_family(labels, lambda label: second_factor if label == 0 else factor)
try:
    bool(first == second)
except TypeError as error:
    print("family comparison is a proposition:", type(error).__name__)
first_product = Sets().product(first)
second_product = Sets().product(second)
print("undecided equality builds both and keeps both ->",
      second_product is not first_product,
      first_product.factor(0) is first_factor,
      second_product.factor(0) is second_factor)
