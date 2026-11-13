"""#380 route test: isometry_to on the test's exact pair through the public API."""
import time

from sage.all import QuadraticForm
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.all import *
from sage_extensions.tensors.tensor import _engine_component_matrix

START = time.time()


def stamp(message):
    print(f"[{time.time() - START:8.1f}s] {message}", flush=True)


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
e8_squared = C("E8") + C("E8")
d16_plus = C(_d16_plus_gram()).twist(-1)
source = e8_squared.two_u_eichler_model().lattice()
target = d16_plus.two_u_eichler_model().lattice()
stamp("the test's pair built")

stamp(f"source.is_isometric_to(target): {source.is_isometric_to(target)}")
witness = source.isometry_to(target)
stamp(f"isometry_to returned: {witness}")
assert witness.domain() is source
assert witness.codomain() is target
stamp("the witness has the test's domain and codomain")

# The acceptance equation: M^T G M = G' with M the column matrix of the
# inverse (columns = the images of the target's generators in source coords).
G = _engine_component_matrix(source.gram_tensor()).change_ring(SageZZ)
Gp = _engine_component_matrix(target.gram_tensor()).change_ring(SageZZ)
rows = []
for generator in target.module_generators():
    image = witness.inverse()(generator)
    rows.append([int(image.to_vector()(label)) for label in source.module_generating_set()])
M = _engine_component_matrix and None
import sage.matrix.constructor as _mc

R = _mc.matrix(SageZZ, rows)
stamp(f"the inverse's row matrix R: {R.nrows()}x{R.ncols()}, det {R.det()}")
left = R * G * R.transpose()
stamp(f"R G R^T == G': {left == Gp}")
M = R.transpose()
stamp(f"(M^T G M == G') with M = R^T: {M.transpose() * G * M == Gp}")
assert M.transpose() * G * M == Gp, "the acceptance equation fails"
stamp("ACCEPTANCE: M^T G M = G' verified exactly through the public API")
