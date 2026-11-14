"""#380: assemble the isometry 2U + E8(-1)^2 -> 2U + D16+(-1) and check
M^T G M = G' exactly, where M = the inverse of the column matrix of the
images of the source generators.

Construction (SPLAG 3rd ed., read as text):
  - Preface to the Third Edition, Notes on Chapter 17, section "Neighbours",
    printed p. lv: the 2-neighbour K' = K_w + Z(w/2) of K = E8(-1)^2 along a
    vector w with 1/2 w not in K and w.w in 8Z.
  - Ch. 26 sec. 1, printed p. 525: (u^perp cap Lambda)/u is an integral
    unimodular Euclidean lattice for isotropic u of divisibility one.
  - Ch. 17 sec. 1, printed pp. 421-422: neighbours are index-2 intersections;
    orbits of primitive norm-0 vectors correspond to the even unimodular
    lattices of the complement.

The chosen neighbour vector is the diagonal w = v + v of the first
norm-(-4), divisibility-one vector v = [3, 6, 9, 8, 6, 4, 2, 4] of one
E8(-1) summand (probe .tmp/kneser.log): its neighbour is in the class of
D16+(-1).
"""
import math
import sys
import time

from sage.all import matrix as sage_matrix, vector as sage_vector
from sage.all import QuadraticForm, QQ as SageQQ, ZZ as SageZZ_unused
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ

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
        if 1 <= i <= 14 and 1 <= j <= 14 and 1 <= i <= 14 and 1 <= j <= 14 and abs(i - j) == 1:
            return -1
        return 0

    return [[entry(i, j) for j in range(16)] for i in range(16)]


C = Lattices(ZZ)
E8sq = C("E8") + C("E8")
D16 = C(_d16_plus_gram()).twist(-1)
source = E8sq.two_u_eichler_model().lattice()
target = D16.two_u_eichler_model().lattice()
stamp("source and target built")

G = _engine_component_matrix(source.gram_tensor()).change_ring(SageZZ)
Gp = _engine_component_matrix(target.gram_tensor()).change_ring(SageZZ)
stamp(f"source gram {G.nrows()}x{G.ncols()}, target gram {Gp.nrows()}x{Gp.ncols()}")
assert G.matrix_from_rows_and_columns(range(4), range(4)) == sage_matrix(
    SageZZ, [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
)
assert G.matrix_from_rows_and_columns(range(4), range(4, 20)) == 0
stamp("source gram has the two hyperbolic planes first, then the complement")

# The chosen neighbour vector w (probe .tmp/kneser.log, candidate 0).
c = sage_vector(SageZZ, [3, 6, 9, 8, 6, 4, 2, 4, 3, 6, 9, 8, 6, 4, 2, 4])
u = sage_vector(SageZZ, [2, 2, 0, 0] + list(c))
p = G * u
assert int(p * u) == 0, f"u is not isotropic: {int(p * u)}"
div_u = math.gcd(*[int(entry) for entry in p])
assert div_u == 1, f"u has divisibility {div_u}"
stamp("u = 2f + w + 2e is isotropic of divisibility one in the source")

# z with u.z = 1, isotropic, by the Smith form of the pairing row.
system = sage_matrix(SageZZ, [list(p)])
D, U, V = system.smith_form()
z0 = V.column(0)
if p * z0 == -1:
    z0 = -z0
assert p * z0 == 1 and all(coefficient in SageZZ for coefficient in z0)
square_z0 = int(z0 * G * z0)
assert square_z0 % 2 == 0
z = z0 - SageZZ(square_z0 // 2) * u
assert int(z * G * u) == 1 and int(z * G * z) == 0, "z is not an isotropic partner"
stamp(f"z = z0 - (z0^2/2)u with z0^2 = {square_z0}: u.z = 1, z^2 = 0")

# M1 = the 16 vectors of u^perp cap z^perp.
conditions = sage_matrix(
    SageZZ,
    [list(p), list(z * G), [0, 0, 1, 0] + [0] * 16, [0, 0, 0, 1] + [0] * 16],
)
kernel = conditions.right_kernel().basis()
M1 = sage_matrix(SageZZ, [list(k) for k in kernel])
assert M1.nrows() == 16 and M1.rank() == 16, f"M1 basis is {M1.nrows()} rows of rank {M1.rank()}"
gram_M1 = M1 * G * M1.transpose()
stamp("M1 = u^perp cap z^perp computed (16 vectors)")

# The target complement K2: rows 4..19 of the target gram.
GK2 = Gp.matrix_from_rows_and_columns(range(4, 20), range(4, 20))
stamp(f"target complement gram (16x16 block) extracted")

# The definite isometry M1 -> K2 through the library's own route.
M1_lat = C([list(row) for row in gram_M1])
K2_lat = C([list(row) for row in GK2])
stamp("definite lattices built; asking Isom(M1, K2) for the witness")
witness = M1_lat.Isom(K2_lat).an_element()
columns = []
for generator in M1_lat.module_generators():
    image = witness(generator)
    columns.append([int(image.to_vector()(label)) for label in K2_lat.module_generating_set()])
T16 = sage_matrix(SageZZ, columns)
stamp(f"definite isometry matrix T16 (16x16) extracted: det {T16.det()}")
assert T16 * GK2 * T16.transpose() == gram_M1, "the definite isometry fails its form equation"
stamp("T16^T G_M1 T16 == G_K2 verified exactly")

# The new basis of the source: u, z, the 16 M1 vectors, e_b, f_b.
new_basis_columns = [list(u), list(z)] + [list(row) for row in M1.rows()]
new_basis_columns += [[0, 0, 1, 0] + [0] * 16, [0, 0, 0, 1] + [0] * 16]
P = sage_matrix(SageZZ, [list(column) for column in zip(*new_basis_columns)])
stamp(f"change-of-basis matrix P: {P.nrows()}x{P.ncols()}, det {P.det()}")
assert abs(int(P.det())) == 1, "the new basis is not unimodular"
stamp("P is unimodular: (u, z, M1, e_b, f_b) is a basis of the source")

# The images: u -> e_a', z -> f_a', M1 -> T16 columns, e_b -> e_b', f_b -> f_b'.
image_columns = [[1, 0, 0, 0] + [0] * 16, [0, 1, 0, 0] + [0] * 16]
image_columns += [[0, 0, 0, 0] + list(T16.row(i)) for i in range(16)]
image_columns += [[0, 0, 1, 0] + [0] * 16, [0, 0, 0, 1] + [0] * 16]
Q = sage_matrix(SageZZ, [list(column) for column in zip(*image_columns)])
T_full = Q * P.inverse()
stamp(f"assembled T_full (20x20): det {T_full.det()}")
left = T_full.transpose() * Gp * T_full
stamp(f"T_full^T G' T_full == G: {left == G}")
assert left == G, "the assembled isometry fails its form equation"

M = T_full.inverse()
left_M = M.transpose() * G * M
stamp(f"M^T G M == G': {left_M == Gp}")
assert left_M == Gp, "the acceptance equation fails"
stamp("ACCEPTance: M^T G M = G' verified exactly")
stamp(f"M (20x20, the inverse column matrix):\n{M}")
