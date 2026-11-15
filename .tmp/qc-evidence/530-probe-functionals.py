"""Constructing functionals of an infinite free module in the Mor model."""

from sage_extensions.all import *
from sage_extensions.all import NN

from sage_extensions.categories.sets.indexed_families import IndexedFamily


def show(label, thunk):
    try:
        value = thunk()
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"  {label}: {type(exc).__name__}: {exc}")
        return None
    print(f"  {label}: {value!r}")
    return value


module = QQ.free_module(NN)
ring = QQ
factor = ring.regular_module()
dual = show("Mor(M, QQ.reg)", lambda: Modules(ring).Mor(module, factor))
labels = show("M.module_generating_set()", lambda: module.module_generating_set())
print("  labels cardinality:", labels.cardinality())

zero_functional = show("Mor(...)(lambda label: 0)", lambda: Modules(ring).Mor(module, factor)(lambda label: factor(ring.zero())))
delta_0 = show(
    "Mor(...)(IndexedFamily(labels, 1 at 0))",
    lambda: Modules(ring).Mor(module, factor)(
        IndexedFamily(labels, lambda label: factor(ring.one() if label == NN(0) else ring.zero()))
    ),
)
constant = show("Mor(...)(IndexedFamily(labels, all ones))", lambda: Modules(ring).Mor(module, factor)(IndexedFamily(labels, lambda label: factor(ring.one()))))
if delta_0 is not None:
    e0 = module.module_generator(NN(0))
    e1 = module.module_generator(NN(1))
    show("delta_0(e0)", lambda: delta_0(e0))
    show("delta_0(e1)", lambda: delta_0(e1))
if constant is not None:
    show("constant(e0)", lambda: constant(module.module_generator(NN(0))))
    show("constant(2*e0 + 3*e7)", lambda: constant(2 * module.module_generator(NN(0)) + 3 * module.module_generator(NN(7))))

# the correlation of the standard diagonal form, with functionals as images
def diagonal(i, j):
    return ring.one() if i == j else ring.zero()

formed = show("equip_bilinear_form", lambda: module.equip_bilinear_form(ring, diagonal))
if formed is not None:
    show("formed.dual_module()", lambda: formed.dual_module())
    show("correlation_morphism()", lambda: formed.correlation_morphism())
