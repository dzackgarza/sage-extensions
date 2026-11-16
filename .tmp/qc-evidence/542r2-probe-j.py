"""#542 round 2: a Picard class of a sheaf and of its tensor square."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        v = f()
        print(f"{label}: {v!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


plane = ProjectiveSpaces(QQ)(2)
x, y, z = plane.homogeneous_coordinate_generators()
cubic = plane.hypersurface(x**3 + y**3 + z**3)
structure = cubic.structure_sheaf()
show("has tensor_power", lambda: hasattr(type(structure), "tensor_power"))
squared = structure.tensor_power(2)
show("squared is structure", lambda: squared is structure)
show("squared type", lambda: type(squared).__name__)
show("isomorphic squared", lambda: squared.is_isomorphic(structure))
classes = cubic.picard_group().underlying_set()
first = classes(structure)
second = classes(squared)
show("reps distinct", lambda: first.representative() is second.representative())
show("hash first", lambda: hash(first))
show("hash second", lambda: hash(second))
show("ask(first==second)", lambda: ask(first == second))
show("FiniteOrderedSets", lambda: FiniteOrderedSets()((first, second)).cardinality())
