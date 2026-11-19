r"""#381: does the isometry constructor accept a matrix over Sage's QQ for an owned rational lattice?"""

import time

from sage.rings.rational_field import QQ as SageQQ
from sage.matrix.constructor import matrix as engine_matrix

from sage_extensions.all import Lattices, ZZ

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
rational = base.domain()
rank = int(rational.module_rank())
log(f"rational lattice rank {rank}, base ring {rational.base_ring()}")

identity = engine_matrix(SageQQ, rank, rank, lambda i, j: 1 if i == j else 0)
start = time.perf_counter()
try:
    isometry = rational.Isom(rational)._isometry_from_column_matrix(identity)
    log(f"isometry from a QQ identity: {type(isometry).__name__}  [{time.perf_counter() - start:.3f}s]")
    generators = tuple(rational.module_generators())
    log(f"  it fixes the generators: {all(isometry(generator) == generator for generator in generators)}")
except Exception as error:
    log(f"failed: {type(error).__name__}: {error}")

# and the owned fields, for comparison
start = time.perf_counter()
try:
    owned = rational.base_ring()(SageQQ(1)) if hasattr(rational.base_ring(), "__call__") else None
    log(f"owned(1) = {owned}")
except Exception as error:
    log(f"owned ring call failed: {type(error).__name__}")
log("done")
