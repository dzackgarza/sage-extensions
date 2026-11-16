"""#542 round 2: a nontrivial-line specimen of one Picard class."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        print(f"{label}: {f()!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


ring = QQ["x"]
x = ring("x")
scheme = ring.affine_spectrum()
cover = scheme.distinguished_open_cover(x, 1 - x)
overlap_x = scheme.structure_sheaf().restriction_map(scheme, cover.overlap(0, 1))(x)
line = QuasiCoherentSheaves(scheme)(cover, {(0, 1): overlap_x})
structure = scheme.structure_sheaf()
classes = scheme.picard_group().underlying_set()
show("line is isomorphic to O", lambda: line.is_isomorphic(structure))
show("square", lambda: line.tensor_power(2) is line)
first = classes(structure)
second = classes(line)
third = classes(line.tensor_power(2))
show("hash O", lambda: hash(first))
show("hash L", lambda: hash(second))
show("hash L^2", lambda: hash(third))
show("first == second", lambda: first == second)
show("ask(first == second)", lambda: ask(first == second))
show("second == first", lambda: ask(second == first))
show("FiniteOrderedSets (O, L)", lambda: FiniteOrderedSets()((first, second)).cardinality())
show("FiniteOrderedSets (O, L^2)", lambda: FiniteOrderedSets()((first, third)).cardinality())
show("FiniteOrderedSets (L, L^2)", lambda: FiniteOrderedSets()((second, third)).cardinality())
