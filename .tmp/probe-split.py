r"""#381: does the cusp-5 line at T_Co split off a hyperbolic plane, generators or not?

`_hyperbolic_completion` scans the lattice's chosen generators for an isotropic f
with b(v,f) != 0 whose plane <v,f> is a direct summand.  This scans a box of
coefficients instead, and reports every isotropic f with b(v,f) = +-div(v) whose
plane is a summand.
"""

import itertools
import time

import numpy as np

from sage_extensions.all import NamedLattices, Sterk, ZZ
from sage.matrix.constructor import matrix as engine_matrix
from sage.rings.integer_ring import ZZ as SageZZ

START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
enriques = NamedLattices.TEn
cusp = Sterk.selected_isotropic_vectors()["Sterk_5"]
coordinates = cusp.to_vector()
enriques_labels = tuple(enriques.module_generating_set())
given = {label: int(coordinates(label)) for label in enriques_labels}
coefficients = {"h": ZZ(given["e"])} if given["e"] else {}
for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
    if given[label]:
        coefficients[label] = ZZ(given[label])
vector = lattice.linear_combination(coefficients)
log(f"v of divisibility {vector.div()}, q = {vector.q()}")

gram = engine_matrix(SageZZ, [[int(lattice.b(lattice.module_generator(left), lattice.module_generator(right))) for right in labels] for left in labels])
G = np.array(gram, dtype=np.int64)
values = vector.to_vector()
v = np.array([int(values(label)) for label in labels], dtype=np.int64)
log(f"v coordinates {tuple(int(entry) for entry in v)}")
log(f"gram determinant {int(gram.determinant())}, v G v = {int(v @ G @ v)}, div v = {int(np.gcd.reduce(G @ v))}")

box = np.array(list(itertools.product((-1, 0, 1), repeat=len(labels))), dtype=np.int64)
log(f"box of {len(box)} coefficient vectors")
squares = np.einsum("ij,jk,ik->i", box, G, box)
pairings = box @ (G @ v)
mask = (squares == 0) & (np.abs(pairings) == int(vector.div())) & (np.abs(box).sum(axis=1) > 0)
candidates = box[mask]
log(f"isotropic f with |b(v,f)| = {int(vector.div())}: {len(candidates)}")

summands = []
for candidate in candidates:
    rows = [list(int(entry) for entry in v), list(int(entry) for entry in candidate)]
    two = engine_matrix(SageZZ, rows)
    smith = two.smith_form()[0]
    diagonal = [int(smith[index, index]) for index in range(2)]
    if diagonal == [1, 1]:
        summands.append(tuple(int(entry) for entry in candidate))
log(f"of those, planes <v,f> that are direct summands: {len(summands)}")
for entry in summands[:5]:
    log(f"  f = {entry}")
log("done")
