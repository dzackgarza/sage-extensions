"""#531: the cost of the canonical form, and the degenerate lineality."""
import time

from sage_extensions.all import *

z2 = Lattices(ZZ)([[1, 0], [0, 1]])
z3 = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

def first_and_cached(label, cones):
    start = time.perf_counter()
    for cone in cones:
        hash(cone)
    first = (time.perf_counter() - start) / len(cones) * 1000
    start = time.perf_counter()
    for cone in cones:
        hash(cone)
    again = (time.perf_counter() - start) / len(cones) * 1000
    print(f"{label}: {len(cones)} cones, first hash {first:.3f} ms, cached {again:.4f} ms")

first_and_cached("pointed cones of Z^2", [z2.reduction_cell(((1, k), (0, 1))) for k in range(1, 41)])
first_and_cached("cones with a lineality, Z^2", [z2.reduction_cell(((0, 1),)) for _ in range(1)] * 40)
first_and_cached("cones with a lineality, Z^3",
                 [z3.reduction_cell(((1, 0, k), (0, 1, 0))) for k in range(1, 41)])
first_and_cached("pointed cones of Z^3", [z3.reduction_cell(((1, 0, k), (0, 1, 0), (0, 0, 1))) for k in range(1, 41)])

# the degenerate case: a whole space as a cone, lineality of full rank
line = Lattices(ZZ)([[1]])
whole = line.reduction_cell(())
print("the whole line as a cone:", whole.dimension(), "pointed", whole.is_pointed())
print("  form", whole._canonical_form_modulo_lineality(), "hash", hash(whole))
print("  equal to itself cut out again:", whole == line.reduction_cell(()),
      "hash equal:", hash(whole) == hash(line.reduction_cell(())))
