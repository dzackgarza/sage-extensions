"""The rewritten dual and order ideal, per module."""

from sage_extensions.all import *


def show(label, thunk):
    try:
        value = thunk()
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"  {label}: {type(exc).__name__}: {exc}")
        return None
    print(f"  {label}: {value!r}")
    return value


def attempt(name, element):
    module = element.parent()
    print(f"--- {name}: parent {module}, base ring {module.base_ring()}")
    dual = show("dual_module()", lambda: module.dual_module())
    if dual is not None:
        print("  dual category:", dual.category())
    ideal = show("order_ideal()", lambda: element.order_ideal())
    if ideal is not None:
        print("  in CommutativeIdeals(base ring):", ideal in CommutativeIdeals(module.base_ring()))


attempt("ZZ**2 at (-6,9)", (ZZ**2).linear_combination({0: ZZ(-6), 1: ZZ(9)}))
attempt("ZZ**2 at 0", (ZZ**2).zero())
attempt("QQ(i) at 1+i", QuadraticField(-1)(1 + QuadraticField(-1).primitive_element()))
attempt("ZZ['x'] at 2x+2", ZZ["x"](2 * ZZ["x"].algebra_generator("x") + 2))
attempt("QQ['x'] at x+1", QQ["x"](QQ["x"].algebra_generator("x") + 1))
attempt("Zmod(8) at 3", Zmod(8)(3))
attempt("M_2(QQ) at e12", QQ.matrix_space(2).matrix_unit(0, 1))
