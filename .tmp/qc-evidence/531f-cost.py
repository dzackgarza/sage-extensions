r"""Probe: what the three hashes cost on this tree, repeated."""

import time

from sage_extensions.all import *


def timed(label, work):
    begin = time.time()
    work()
    print(f"  {label}: {1000 * (time.time() - begin):8.3f} ms", flush=True)


lattice = ZZ.free_module(2)
category = ConvexPolytopes(lattice)
many = category(tuple((index, index * index) for index in range(1, 120)))
print("polygon vertices:", many.n_vertices(), flush=True)
for attempt in (1, 2, 3):
    timed(f"hash {attempt} of the 119-gon", lambda: hash(many))

points = FiniteOrderedSets()(tuple(range(2000)))
asked = []

def is_even(point):
    asked.append(point)
    return point % 2 == 0

subset = points.power_set().from_predicate(is_even)
for attempt in (1, 2, 3):
    before = sum(1 for _ in asked)
    timed(f"hash {attempt} of a subset of 2000 points", lambda: hash(subset))
    print(f"    decisions this hash: {sum(1 for _ in asked) - before}", flush=True)

big = Lattices(ZZ)([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
wide = big.reduction_cell(((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
for attempt in (1, 2, 3):
    timed(f"hash {attempt} of the cone with a lineality space", lambda: hash(wide))
