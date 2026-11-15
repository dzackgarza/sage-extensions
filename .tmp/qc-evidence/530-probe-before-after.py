"""The behaviour the two tests state, read on whichever library is first on the path."""

import collections.abc

from sage_extensions.all import *
import sage_extensions


print("package:", sage_extensions.__file__)

ring = ZZ["x"]
print("ring.__iter__:", ring.__iter__)
print("isinstance(ring, collections.abc.Iterable):", isinstance(ring, collections.abc.Iterable))
for label, thunk in (("iter", lambda: iter(ring)), ("tuple", lambda: tuple(ring))):
    try:
        thunk()
        print(f"{label}: returned")
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"{label}: {type(exc).__name__}")

module = QQ**NN
dual = module.dual_module()
print("dual:", dual)
print("dual is Mor(M, QQ.reg):", dual is module.module_category().Mor(module, QQ.regular_module()))
try:
    constant = dual(lambda label: QQ.regular_module()(QQ.one()))
    total = module.module_generator(NN(0)) + module.module_generator(NN(1))
    print("constant functional at e0+e1:", module.dual_evaluation(constant, total))
except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
    print(f"constant functional: {type(exc).__name__}: {exc}")

two_x = ZZ["x"](2 * ZZ["x"].algebra_generator("x") + 2)
try:
    print("(2x+2).order_ideal():", two_x.order_ideal())
except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
    print(f"(2x+2).order_ideal(): {type(exc).__name__}: {exc}")
