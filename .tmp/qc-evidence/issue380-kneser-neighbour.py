"""#380: find the Kneser 2-neighbour vector w of E8(-1)^2 whose neighbour
K' = K_w + Z(w/2) is in the class of D16+(-1), then check the u-construction.

Sources (SPLAG 3rd ed., .tmp/conway-sloane-splag-3rd-ed.pdf, read as text):
  - Preface to the Third Edition, Notes on Chapter 17, section "Neighbours",
    printed p. lv: for u in L with 1/2 u not in L and u.u in 4Z, the neighbour
    L'' = L_u + Z(u/2) is unimodular; L'' is even iff u.u in 8Z.
  - Ch. 26 sec. 1, printed p. 525: (u^perp cap Lambda)/u is an integral
    unimodular Euclidean lattice for isotropic u in a unimodular Lorentzian
    lattice.
  - Ch. 17 sec. 1, printed pp. 421-422: neighbours are index-2 intersections;
    orbits of primitive norm-0 vectors correspond to the even unimodular
    lattices of the complement.

Search family: w = v + v, the diagonal copy of one norm-(-4) divisibility-one
vector v of one E8(-1) summand, so w.w = -8 in 8Z and 1/2 w is not in K.
"""
import math
import sys
import time

from sage.all import matrix as sage_matrix, vector as sage_vector
from sage.all import QuadraticForm, QQ as SageQQ
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
E8sq = C("E8") + C("E8")
D16 = C(_d16_plus_gram()).twist(-1)
stamp("lattices built")

GK = _engine_component_matrix(E8sq.gram_tensor()).change_ring(SageZZ)
G2 = _engine_component_matrix(D16.gram_tensor()).change_ring(SageZZ)
G8 = GK.matrix_from_rows_and_columns(range(8), range(8))
assert GK.matrix_from_rows_and_columns(range(8), range(8, 16)) == 0
assert GK.matrix_from_rows_and_columns(range(8, 16), range(8, 16)) == G8
stamp("E8(-1)^2 gram is block-diagonal with two equal E8(-1) blocks")

# The norm-4 shell of E8, positive form -G8, enumerated once.
Q8 = QuadraticForm(SageZZ, -G8)
shells = Q8.short_vector_list_up_to_length(4)
sizes = [len(entry) for entry in shells]
stamp(f"E8(-1) shell sizes up to 4: {sizes}")
root_index = sizes.index(240)
if sizes[root_index + 1] == 2160:
    norm4_index = root_index + 1
elif sizes[root_index + 2] == 2160:
    norm4_index = root_index + 2
else:
    raise SystemExit(f"cannot find the norm-4 shell in {sizes}")
stamp(f"roots at index {root_index}, norm-(-4) shell at index {norm4_index}")
shell4 = [sage_vector(SageZZ, list(v)) for v in shells[norm4_index]]
stamp(f"norm-(-4) vectors of one E8(-1) summand: {len(shell4)}")

order_e8sq = QuadraticForm(SageZZ, -GK).number_of_automorphisms()
order_d16 = QuadraticForm(SageZZ, -G2).number_of_automorphisms()
stamp(f"|O(E8(-1)^2)| = {order_e8sq}")
stamp(f"|O(D16+(-1))| = {order_d16}")


def divisibility(pairing):
    return math.gcd(*[int(entry) for entry in pairing])


def neighbour_gram(c):
    r"""Gram matrix and basis of K' = K_w + Z(w/2) for w with coordinates c.

    K_w = {x in K : x . w even} = Z(2v) + ker(a) for a = GK c the pairing
    vector of w and a . v = 1.  With c = s B on that basis and r = s mod 2,
    K' has B-coordinates Z^16 + Z(s/2) = (1/2)(2Z^16 + Z r): half the echelon
    basis of the row span of the 2e_i and r.
    """
    a = GK * c
    assert divisibility(a) == 1, f"divisibility of w is {divisibility(a)}, not 1"
    v = sage_matrix(SageZZ, [list(a)]).solve_right(sage_vector(SageZZ, [1]))
    kernel = sage_matrix(SageZZ, [list(a)]).right_kernel().basis()
    B = sage_matrix(SageZZ, [list(SageZZ(2) * v)] + [list(k) for k in kernel])
    assert B.rank() == 16 and abs(int(B.det())) == 2, f"K_w basis is degenerate: rank {B.rank()}, det {B.det()}"
    s = B.solve_left(c)
    assert s * B == c and all(coefficient in SageZZ for coefficient in s)
    r = sage_vector(SageZZ, [int(coefficient) % 2 for coefficient in s])
    assert r != 0, "w lies in 2K_w: no neighbour"
    doubled = sage_matrix(
        SageZZ,
        [list(SageZZ(2) * sage_vector(SageZZ, [SageZZ(1) if i == j else SageZZ(0) for j in range(16)])) for i in range(16)]
        + [list(r)],
    )
    echelon = doubled.echelon_form()
    basis = [echelon.row(index) for index in range(echelon.nrows()) if echelon.row(index) != 0]
    assert len(basis) == 16, f"echelon basis has {len(basis)} rows"
    half = sage_matrix(SageQQ, [[SageQQ(coefficient) / 2 for coefficient in row] for row in basis])
    prime = half * B.change_ring(SageQQ)
    gram = prime * GK.change_ring(SageQQ) * prime.transpose()
    return gram.change_ring(SageQQ), prime


def classify(gram):
    entries = gram.list()
    assert all(entry in SageZZ for entry in entries), f"neighbour gram is not integral: {entries}"
    order = QuadraticForm(SageZZ, -gram.change_ring(SageZZ)).number_of_automorphisms()
    if order == order_e8sq:
        return "E8(-1)^2", order
    if order == order_d16:
        return "D16+(-1)", order
    return "other", order


found = None
for index, v in enumerate(shell4[:32]):
    c = sage_vector(SageZZ, list(v) + list(v))
    square = int(c * GK * c)
    assert square == -8, f"diagonal square is {square}"
    assert any(int(entry) % 2 for entry in c), "half of w lies in K"
    gram, prime = neighbour_gram(c)
    determinant = int(gram.det())
    label, order = classify(gram)
    stamp(
        f"candidate {index}: square {square}, divisibility {divisibility(GK * c)}, "
        f"neighbour det {determinant}, class {label} (|O| = {order})"
    )
    if label == "D16+(-1)":
        found = (index, v, c, gram)
        stamp("GOOD: this diagonal has neighbour in the class of D16+(-1)")
        break

if found is None:
    stamp("no diagonal candidate in the first 32 produced a D16+(-1) neighbour")
    sys.exit(1)

index, v, c, gram = found
stamp(f"chosen v (one E8(-1) summand): {list(v)}")
stamp(f"chosen w = v + v (E8(-1)^2 coordinates): {list(c)}")
stamp(f"K' gram:\n{gram}")

# The u-construction in L1 = U + E8(-1)^2: u = 2f + w + 2e with c = -(w.w)/4 = 2.
L1 = C("U") + E8sq
G1 = _engine_component_matrix(L1.gram_tensor()).change_ring(SageZZ)
assert G1.matrix_from_rows_and_columns(range(2), range(2)) == sage_matrix(SageZZ, [[0, 1], [1, 0]])
assert G1.matrix_from_rows_and_columns(range(2), range(2, 18)) == 0
stamp("L1 = U + E8(-1)^2 gram has the hyperbolic plane first")

u = sage_vector(SageZZ, [2, 2] + list(c))
p = G1 * u
assert int(p * u) == 0, f"u is not isotropic: {int(p * u)}"
assert divisibility(p) == 1, f"u has divisibility {divisibility(p)}"
stamp("u = 2f + w + 2e is isotropic of divisibility one")

system = sage_matrix(SageZZ, [list(p)])
D, U, V = system.smith_form()
z0 = V.column(0)
if p * z0 == -1:
    z0 = -z0
assert p * z0 == 1 and all(coefficient in SageZZ for coefficient in z0)
square_z0 = int(z0 * G1 * z0)
assert square_z0 % 2 == 0
z = z0 - SageZZ(square_z0 // 2) * u
assert int(z * G1 * u) == 1 and int(z * G1 * z) == 0, "z is not an isotropic partner"
stamp(f"z = z0 - (z0^2/2)u with z0^2 = {square_z0}: u.z = 1, z^2 = 0")

conditions = sage_matrix(SageZZ, [list(p), list(z * G1)])
kernel = conditions.right_kernel().basis()
M1 = sage_matrix(SageZZ, [list(k) for k in kernel])
assert M1.nrows() == 16 and M1.rank() == 16, f"M1 basis is {M1.nrows()} rows of rank {M1.rank()}"
gram_M1 = M1 * G1 * M1.transpose()
label_m, order_m = classify(gram_M1.change_ring(SageQQ))
stamp(f"(u^perp cap z^perp) class: {label_m} (|O| = {order_m})")
stamp(f"M1 gram:\n{gram_M1}")
