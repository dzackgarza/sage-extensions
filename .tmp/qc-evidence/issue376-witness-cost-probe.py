"""#376: what the port's OrbitCoverModel actually builds for the target model, and what the easy group costs."""
import sys
import time

from sage_extensions.all import *

START = time.time()


def stamp(message):
    print(f"[{time.time() - START:8.1f}s] {message}")
    sys.stdout.flush()


def _d16_plus_gram():
    def entry(i, j):
        if i == j:
            return 4 if i in (0, 15) else 2
        if {i, j} == {0, 1}:
            return -2
        if {i, j} == {0, 15}:
            return 1
        if 1 <= i <= 14 and 1 <= j <= 14 and abs(i - j) == 1:
            return -1
        return 0

    return [[entry(i, j) for j in range(16)] for i in range(16)]


C = Lattices(ZZ)
target = C(_d16_plus_gram()).twist(-1).two_u_eichler_model().lattice()
stamp(f"target lattice {target.signature_pair()}")

from sage_extensions.tensors.tensor import _engine_component_matrix
from sage_indefinite_port.indefinite.eichler import OrbitCoverModel

begin = time.time()
cover = OrbitCoverModel(target)
stamp(f"OrbitCoverModel(target) in {time.time() - begin:.2f} s")
stamp(f"attributes: {sorted(vars(cover))}")
model = cover.model
lattice = model.lattice()
stamp(f"model lattice signature {lattice.signature_pair()}, same object as target: {lattice is target}")
stamp(f"model lattice gram tensor: {type(lattice.gram_tensor()).__name__}")

basis = model.hyperbolic_basis() + tuple(
    model.complement_inclusion()(point) for point in model.orthogonal_complement().module_generators()
)
stamp(f"model basis: {len(basis)} vectors")

begin = time.time()
_engine_component_matrix(lattice.gram_tensor())
stamp(f"_engine_component_matrix(model gram) in {time.time() - begin:.2f} s")

begin = time.time()
for second in range(5):
    int(lattice.b(basis[0], basis[second]))
stamp(f"5 b() on the model basis in {time.time() - begin:.2f} s")

begin = time.time()
generators = OrbitCoverModel.source_easy_generators(model)
stamp(f"source_easy_generators(model): {len(generators)} generators in {time.time() - begin:.1f} s")

begin = time.time()
covering = tuple(cover.covering_vectors(0, 1))
stamp(f"covering_vectors(0, 1): {len(covering)} vectors in {time.time() - begin:.1f} s")
stamp("done")
