"""Which class answers the torsion decision, and with what, on the two objects."""

from sage_extensions.all import *

for label, thunk in (
    ("Z[x]/(x^2)", lambda: ZZ["x"].quotient_by_relations([ZZ["x"].algebra_generator("x") ** 2])),
    ("Zmod(4)['x']", lambda: Zmod(4)["x"]),
    ("Z['x']", lambda: ZZ["x"]),
    ("Q(i)", lambda: QuadraticField(-1)),
):
    obj = thunk()
    print(f"### {label}: {obj}")
    owner = None
    for klass in type(obj).__mro__:
        if "_torsion_freeness_decision" in vars(klass):
            owner = klass
            break
    print("  answers from:", owner.__module__ + "." + owner.__qualname__)
    print("  answer:", obj.is_torsion_free())
