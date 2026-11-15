"""The evaluation-image route, built the way the image owner wants it."""

from sage_extensions.all import *


def show(label, thunk):
    try:
        value = thunk()
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"  {label}: {type(exc).__name__}: {exc}")
        return None
    print(f"  {label}: {value!r}")
    return value


def attempt(name, module, vector):
    print(f"--- {name}: base ring {module.base_ring()}")
    ring = module.base_ring()
    regular = ring.regular_module()
    to_ring = ring.regular_module_isomorphism()
    dual = show("dual_module()", lambda: module.dual_module())
    labels = show("dual.module_generating_set()", lambda: dual.module_generating_set())
    if labels is None:
        return
    values = show(
        "generator images {l: f_l(v)}",
        lambda: {
            label: to_ring(dual.module_generator(label)(vector))
            for label in labels
        },
    )
    if values is None:
        return
    evaluation = show(
        "Mor(dual, R.reg)(images)",
        lambda: Modules(ring).Mor(dual, regular)(values),
    )
    if evaluation is None:
        return
    print("  evaluation.domain() is dual:", evaluation.domain() is dual)
    print("  evaluation.codomain() is regular:", evaluation.codomain() is regular)
    show("evaluation.image()", lambda: evaluation.image())
    show("old route dual_evaluation_image_generators", lambda: module.dual_evaluation_image_generators(vector))


attempt("ZZ**2 at (-6,9)", ZZ**2, (ZZ**2).linear_combination({0: ZZ(-6), 1: ZZ(9)}))
attempt("ZZ**2 at 0", ZZ**2, (ZZ**2).zero())
attempt("ZZ['x'] at 2x+2", ZZ["x"], ZZ["x"](2 * ZZ["x"].algebra_generator("x") + 2))
attempt("Zmod(8) at 3", Zmod(8), Zmod(8)(3))
