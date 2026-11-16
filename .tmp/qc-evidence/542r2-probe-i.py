"""#542 round 2: two invertible sheaves on a plane cubic with one Picard class."""
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
inclusion = cubic.inclusion()
pulled_structure = inclusion.module_pullback(plane.structure_sheaf())
structure = cubic.structure_sheaf()
show("types", lambda: (type(pulled_structure).__name__, type(structure).__name__))
show("distinct objects", lambda: pulled_structure is structure)
show("isomorphic", lambda: pulled_structure.is_isomorphic(structure))
classes = cubic.picard_group().underlying_set()
show("class set type", lambda: type(classes).__name__)
first = classes(structure)
second = classes(pulled_structure)
show("reps distinct", lambda: first.representative() is second.representative())
show("hash first", lambda: hash(first))
show("hash second", lambda: hash(second))
show("ask(first == second)", lambda: ask(first == second))
show("FiniteOrderedSets", lambda: FiniteOrderedSets()((first, second)).cardinality())
