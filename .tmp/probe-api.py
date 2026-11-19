r"""#381: can the torsor's lift be decided from matrices, and is a matrix enough to build it?"""

import time

from sage_extensions.all import Lattices, ZZ
from sage_extensions.categories.lattice_morphisms import _module_matrix
from sage.matrix.constructor import matrix as engine_matrix

START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
labels = tuple(lattice.module_generating_set())
v = lattice.module_generator(labels[0])
line = lattice.primitive_isotropic_subobject(v)
reduction = line.isotropic_reduction()
torsor = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
base = torsor.base_point()
log(f"base type: {type(base).__name__}")
try:
    framed = _module_matrix(base)
    log(f"framed type: {type(framed).__name__}")
    matrix = engine_matrix(framed)
    log(f"matrix: {matrix.nrows()} x {matrix.ncols()} over {matrix.base_ring()}")
    log(f"entries integral: {all(entry.is_integer() for entry in matrix.list())}")
except Exception as error:
    log(f"matrix read failed: {type(error).__name__}: {error}")

rational = base.domain()
log(f"rational lattice: rank {rational.module_rank()}")
try:
    isometry = rational.Isom(rational)._isometry_from_column_matrix(
        engine_matrix(rational.base_ring(), [[1 if i == j else 0 for j in range(rational.module_rank())] for i in range(rational.module_rank())])
    )
    log(f"isometry from an identity matrix: {type(isometry).__name__}")
except Exception as error:
    log(f"isometry construction failed: {type(error).__name__}: {error}")

start = time.perf_counter()
for _ in range(20):
    reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
log(f"20 torsor constructions: {time.perf_counter() - start:.3f}s")
log("done")
