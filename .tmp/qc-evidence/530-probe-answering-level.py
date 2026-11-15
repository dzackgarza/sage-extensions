"""Which level answers order_ideal, per module."""

from sage_extensions.all import *


def which(element):
    bound = element.order_ideal
    function = bound.__func__
    print(f"  answering method: {function.__qualname__}  module {function.__module__}")


for name, element in (
    ("ZZ**2 at (-6,9)", (ZZ**2).linear_combination({0: ZZ(-6), 1: ZZ(9)})),
    ("QQ(i) at 1+i", QuadraticField(-1)(1 + QuadraticField(-1).primitive_element())),
    ("ZZ['x'] at 2x+2", ZZ["x"](2 * ZZ["x"].algebra_generator("x") + 2)),
    ("QQ['x'] at x+1", QQ["x"](QQ["x"].algebra_generator("x") + 1)),
    ("M_2(QQ) element", QQ.matrix_space(2).matrix_unit(0, 1)),
    ("module over M_2(QQ)", QQ.matrix_space(2).regular_module().an_element()),
    ("Zmod(8) at 3", Zmod(8)(3)),
):
    print(f"--- {name}")
    which(element)
