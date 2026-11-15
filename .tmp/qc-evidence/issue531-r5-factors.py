r"""What the base interners accept as a factor."""
from sage_extensions.categories.sets import set_categories
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family

labels = finite_ordered_set((0, 1))

def attempt(name, thunk):
    try:
        value = thunk()
    except Exception as error:
        print(f"{name}: {type(error).__name__}: {error}")
    else:
        print(f"{name}: {value!r}")

list_factor = lambda label: finite_ordered_set(([label],))
try:
    print("factor hashes:", hash(finite_ordered_set(([0],))))
except Exception as error:
    print("factor hash raises:", type(error).__name__, error)

first = indexed_family(labels, list_factor)
second = indexed_family(labels, list_factor)
print("families equal:", first == second)
attempt("product of an unhashable-factor family", lambda: Sets().product(first))
attempt("second product is the first", lambda: Sets().product(second) is Sets().product(first))
attempt("coproduct of an unhashable-factor family", lambda: Sets().coproduct(first))

plain = lambda label: [label]
third = indexed_family(labels, plain)
print("list-valued families equal:", third == indexed_family(labels, plain))
attempt("product of a list-valued family", lambda: Sets().product(third))
attempt("coproduct of a list-valued family", lambda: Sets().coproduct(third))
