"""Which modules carry a chosen resolution for their linear dual."""

from sage_extensions.all import *


def show(label, thunk):
    try:
        value = thunk()
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"  {label}: {type(exc).__name__}: {exc}")
        return None
    print(f"  {label}: {value!r}")
    return value


for name, module in (
    ("ZZ**2", ZZ**2),
    ("Zmod(8)", Zmod(8)),
    ("QQ(i)", QuadraticField(-1)),
    ("ZZ['x']", ZZ["x"]),
    ("QQ['x']", QQ["x"]),
):
    print(f"--- {name}: base ring {module.base_ring()}")
    print("  has_selected_module_resolution:", module.has_selected_module_resolution())
    labels = show("module_generating_set()", lambda m=module: m.module_generating_set())
    if labels is not None:
        show("its cardinality", lambda l=labels: l.cardinality())
    dual = show("dual_module()", lambda m=module: m.dual_module())
    if dual is not None:
        print("  dual has_selected_module_resolution:", dual.has_selected_module_resolution())
        show("dual.module_generating_set()", lambda d=dual: d.module_generating_set())
