"""order_ideal where the scalar ring does not commute."""

from sage_extensions.all import *


def show(label, thunk):
    try:
        value = thunk()
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"  {label}: {type(exc).__name__}: {exc}")
        return None
    print(f"  {label}: {value!r}")
    return value


matrices = QQ.matrix_space(2)
print("M_2(QQ) in CommutativeRings:", matrices in OwnedRings().Commutative())
regular = show("M_2(QQ).regular_module()", lambda: matrices.regular_module())
if regular is not None:
    print("  base ring:", regular.base_ring())
    element = show("regular module an_element()", lambda: regular.an_element())
    if element is not None:
        show("dual_module()", lambda: regular.dual_module())
        show("order_ideal()", lambda: element.order_ideal())

free = show("M_2(QQ).free_module(1)", lambda: matrices.free_module(1))
if free is not None:
    print("  base ring:", free.base_ring())
    element = free.an_element()
    show("dual_module()", lambda: free.dual_module())
    show("order_ideal()", lambda: element.order_ideal())

# the ring's own element, placed as a QQ-module
ring_element = matrices.matrix_unit(0, 1)
print("ring element parent:", ring_element.parent(), "base ring:", ring_element.parent().base_ring())
show("ring element order_ideal()", lambda: ring_element.order_ideal())
