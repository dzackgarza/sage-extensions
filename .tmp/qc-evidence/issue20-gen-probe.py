"""Issue #20: the .gen defect that stops the number-field-order specimen.

`QuadraticField(2, "a").maximal_order()` cannot be indexed by `field.gen()`:
`'Owned_OwnedAlgebraParent_with_category' object has no attribute 'gen'`.  This
reads what the parent does offer, so the repair is stated against a real datum.
"""
from sage_extensions.all import *  # noqa: F401,F403

field = QuadraticField(2, "a")
order = field.maximal_order()
print("order:", order, flush=True)
print("order parent type:", type(order).__name__ if False else "read below", flush=True)
print("order in OwnedRings():", order in OwnedRings(), flush=True)
print("field:", field, flush=True)
try:
    print("field.gen():", field.gen(), flush=True)
except Exception as error:
    print("field.gen() RAISED", type(error).__name__, error, flush=True)
try:
    print("order.gen():", order.gen(), flush=True)
except Exception as error:
    print("order.gen() RAISED", type(error).__name__, error, flush=True)
for name in ("is_framed_algebra", "algebra_generating_set", "algebra_generator", "gens", "one", "zero", "base_ring"):
    try:
        value = getattr(order, name)
        print(f"order.{name}:", value() if callable(value) else value, flush=True)
    except Exception as error:
        print(f"order.{name} RAISED", type(error).__name__, error, flush=True)
labels = order.algebra_generating_set()
for label in labels:
    print("  generator", label, "->", order.algebra_generator(label), flush=True)
print("categories of order:", order.category(), flush=True)
print("DONE", flush=True)
