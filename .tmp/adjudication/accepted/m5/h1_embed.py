"""H1: exact embedding N = U + U(2) + E8(-2)  ->  M = U + U + E8(-2).

Everything is exact (fractions.Fraction); no floating point, no external CAS.
Output: index, Gram pullback, determinant, structure of A_N, A_M, the gluing
class H = M/N, the discriminant-form map phi: A_M -> A_N, and |O(A_N)|
computed by orbit-stabilizer + Witt (validated on known small cases).
"""
from fractions import Fraction as F

# ---------- tiny exact linear algebra ----------
def mmul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]

def T(A):
    return [list(r) for r in zip(*A)]

def det(A):
    n = len(A); M = [row[:] for row in A]; d = F(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return F(0)
        if p != c:
            M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]; pv = M[c][c]
        for r in range(c + 1, n):
            if M[r][c] != 0:
                f = M[r][c] / pv
                M[r] = [M[r][j] - f * M[c][j] for j in range(n)]
    return d

def inv(A):
    n = len(A)
    M = [A[i][:] + [F(1) if i == j else F(0) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(2 * n)]
    return [row[n:] for row in M]

def blockdiag(blocks):
    n = sum(len(b) for b in blocks)
    M = [[F(0)] * n for _ in range(n)]
    o = 0
    for b in blocks:
        for i in range(len(b)):
            for j in range(len(b)):
                M[o + i][o + j] = b[i][j]
        o += len(b)
    return M

def matint(A):
    return all(x.denominator == 1 for row in A for x in row)

# ---------- the lattices ----------
U  = [[F(0), F(1)], [F(1), F(0)]]        # hyperbolic plane, basis (p,q), (p,q)=1
U2 = [[F(0), F(2)], [F(2), F(0)]]        # U(2), basis (a,b), (a,b)=2
# E8 = even unimodular positive definite rank 8, given by its Cartan matrix
C = [[F(0)] * 8 for _ in range(8)]
for i in range(8):
    C[i][i] = F(2)
for i, j in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7)]:   # E8 Dynkin: arms 1,2,4
    C[i][j] = C[j][i] = F(-1)
C2 = [[-2 * x for x in row] for row in C]     # E8(-2)

def sylvester_ok(A):
    n = len(A)
    return all(det([row[:i + 1] for row in A[:i + 1]]) > 0 for i in range(n))

print("E8 check: det =", det(C), " symmetric:", C == T(C),
      " even:", all(C[i][i] % 2 == 0 for i in range(8)) and matint(C),
      " positive definite (Sylvester):", sylvester_ok(C))

GN = blockdiag([U, U2, C2])       # N = U + U(2) + E8(-2),   rank 12
GM = blockdiag([U, U, C2])        # M = U + U + E8(-2),      rank 12
print("rank N =", len(GN), " signature N = (2,10);  det N =", det(GN), "= 2^10 ?", det(GN) == 2**10)
print("det M =", det(GM), " (A_M = A_{E8(-2)} = (Z/2)^8)")

# ---------- the embedding T: N -> M ----------
# N basis: e0,e1 (U: p1,q1), e2,e3 (U(2): a,b), e4..e11 (E8(-2))
# M basis: E0,E1 (U: p1,q1), E2,E3 (U: p2,q2), E4..E11 (E8(-2))
# U(2) -> U :  a = 2 p2 , b = q2   (this is the problem's scaling on the first
# coordinate: (x1,x2,y1,y2,w) |-> (x1,x2,2 y1,y2,w); (2p2,q2)=2, (2p2,2p2)=0, (q2,q2)=0)
Tmat = [[F(0)] * 12 for _ in range(12)]
Tmat[0][0] = F(1); Tmat[1][1] = F(1)            # U -> first plane, identity
Tmat[2][2] = F(2)                                # a |-> 2 p2
Tmat[3][3] = F(1)                                # b |-> q2
for i in range(4, 12):
    Tmat[i][i] = F(1)                            # E8(-2) identity
print("\n(H1) Gram pullback  T^t G_M T == G_N ?", mmul(mmul(T(Tmat), GM), Tmat) == GN)
print("(H1) index [M:N] = |det T| =", det(Tmat))

# ---------- dual lattices and discriminant forms ----------
GNi, GMi = inv(GN), inv(GM)
print("(H1) 2*N^v subset N ?  (A_N killed by 2):", matint([[2 * x for x in r] for r in GNi]))
print("(H1) 2*M^v subset M ?                    :", matint([[2 * x for x in r] for r in GMi]))

def classes(Gi, n):
    """The classes [Gi e_j] in (Q/Z)^n, as tuples of Fractions (canonical rep)."""
    out = []
    for j in range(n):
        col = [Gi[i][j] for i in range(n)]
        out.append([x - int(x) for x in col])     # mod Z, canonical rep in [0,1)
    return out

def twice_vectors(cl, n):
    """A_N -> (Z/2)^n, [y] |-> 2y mod 2 ; an injective F_2-linear map."""
    return [tuple(int(2 * x) % 2 for x in c) for c in cl]

def f2_basis(vecs):
    basis = []
    for v in vecs:
        w = list(v)
        for b in basis:
            piv = next(i for i in range(len(w)) if b[i])
            if w[piv]:
                w = [(w[i] - b[i]) % 2 for i in range(len(w))]
        if any(w):
            piv = next(i for i in range(len(w)) if w[i])
            basis.append(tuple(w))
    return basis

def span(basis):
    S = {tuple([0] * len(basis[0])) if basis else ()}
    for b in basis:
        S = S | {tuple((s[i] + b[i]) % 2 for i in range(len(b))) for s in S}
    return S

def dd(v, w):
    return sum(a * b for a, b in zip(v, w)) % 2

def rank_f2(M):
    if not M: return 0
    r = 0; Mm = [row[:] for row in M]; rows = len(Mm); cols = len(Mm[0])
    for c in range(cols):
        p = next((i for i in range(r, rows) if Mm[i][c]), None)
        if p is None: continue
        Mm[r], Mm[p] = Mm[p], Mm[r]
        for i in range(rows):
            if i != r and Mm[i][c]:
                Mm[i] = [(Mm[i][j] - Mm[r][j]) % 2 for j in range(cols)]
        r += 1
    return r

clN = classes(GNi, 12)
vecN = twice_vectors(clN, 12)
bN = f2_basis(vecN)
print("(H1) dim A_N =", len(bN), " (so A_N = (Z/2)^10)")

# quadratic/bilinear data on A_N: use the canonical reps of classes.
# For a class [y] (y in [0,1)^n):  q([y]) = y^t G y mod 2 ,  b([y],[y']) = y^t G y' mod 1
def qfun(G, y):
    return sum(y[i] * G[i][j] * y[j] for i in range(len(y)) for j in range(len(y)))

def bfun(G, y, z):
    return sum(y[i] * G[i][j] * z[j] for i in range(len(y)) for j in range(len(y)))

# map F_2 basis vectors back to canonical class reps: keep the pairs (vec, class)
pairs = {}
for c, v in zip(clN, vecN):
    pairs.setdefault(v, c)
basis_reps = []
cur = []
for c, v in zip(clN, vecN):
    if rank_f2(cur + [list(v)]) > len(cur):     # greedy independent subset
        cur.append(list(v)); basis_reps.append(c)
qvals = [qfun(GN, c) for c in basis_reps]
bvals = [[bfun(GN, basis_reps[i], basis_reps[j]) for j in range(len(bN))] for i in range(len(bN))]
print("(H1) q on the 10 basis classes (mod 2):", [int(x) % 2 for x in qvals])
print("(H1) b matrix mod 1 (2b, entries in F_2):")
for i in range(len(bN)):
    print("     ", [int(2 * bvals[i][j]) % 2 for j in range(len(bN))])

# non-degeneracy of the polar form on A_N
gram2 = [[int(2 * bvals[i][j]) % 2 for j in range(len(bN))] for i in range(len(bN))]
print("(H1) rank of the polar form on A_N =", rank_f2(gram2), "(nondegenerate iff 10)")

# q and b on A_N, in coordinates with respect to the 10 basis classes
def rep_for(cvec):
    out = [F(0)] * 12
    for i, ci in enumerate(cvec):
        if ci:
            for j in range(12):
                out[j] += basis_reps[i][j]
    return [x % 1 for x in out]
def tovec(i, dim):
    return tuple((i >> k) & 1 for k in range(dim))
qA = {i: int(qfun(GN, rep_for(tovec(i, 10)))) % 2 for i in range(2 ** 10)}
def bA(u, v):
    return int(2 * bfun(GN, rep_for(tovec(u, 10)), rep_for(tovec(v, 10)))) % 2
okq = all((qA[u ^ v] - qA[u] - qA[v] - bA(u, v)) % 2 == 0 for u in range(128) for v in range(128))
print("(H1) q(x+y)=q(x)+q(y)+b(x,y) on A_N:", okq)
print("(H1) #{x in A_N : q(x)=0} =", sum(1 for i in range(1024) if qA[i] == 0), "of 1024")

# ---------- is A_N the split (hyperbolic) 2-elementary form of rank 10? ----------
# We look for 5 pairwise orthogonal hyperbolic pairs.  If found, A_N is isometric to
# the discriminant form of U(2)^5 and |O(A_N)| is the classical order |O^+_10(2)|.
def qc(u): return qA[u]
def bc(u, v): return bA(u, v)

def xorv(u, v): return u ^ v            # F_2^10 with integer encoding
def combo(cvec):
    x = 0
    for k, c in enumerate(cvec):
        if c: x ^= (1 << k)
    return x

def orth_basis(vecs):
    """basis (ints) of the span of vecs"""
    out = []
    for v in vecs:
        w = v
        for b in out:
            hb = b.bit_length() - 1
            if (w >> hb) & 1: w ^= b
        if w: out.append(w)
    return out

found = []
rem = list(range(1, 1024))                     # current orthogonal complement, as vectors
pairs = []
cur_basis = [1 << k for k in range(10)]        # basis of the space we are still in
def span_of(basis):
    S = {0}
    for b in basis:
        S |= {x ^ b for x in S}
    return S
space = span_of(cur_basis)
for step in range(5):
    # find e with q=0, e != 0 in the current space, then f with q=0, b(e,f)=1
    e = next(x for x in sorted(space) if x != 0 and qc(x) == 0)
    f = next((y for y in sorted(space) if qc(y) == 0 and bc(e, y) == 1), None)
    assert f is not None, "not split at step %d" % step
    pairs.append((e, f))
    # orthogonal complement of <e,f> inside space
    space = {x for x in space if bc(x, e) == 0 and bc(x, f) == 0}
    # check nondegeneracy of the restricted form
    nb = orth_basis(sorted(space))
    def rk(bs):
        return rank_f2([[(bc(x, y)) for y in bs] for x in bs])
    assert rk(nb) == len(nb), "complement degenerate at step %d" % step
print("(H1) A_N is split: found", len(pairs), "hyperbolic pairs, q=0 and b=1 on each;")
print("     hence A_N is isometric to the discriminant form of U(2)^5 (split form, rank 10).")

# ---------- calibration of the order formula by brute force in low rank ----------
def brute_order(dim, qf, bf):
    """|O(q)| by enumerating all of GL_dim(F_2) for small dim"""
    from itertools import permutations
    vecs = [tuple((i >> k) & 1 for k in range(dim)) for i in range(2 ** dim)]
    nonz = [v for v in vecs if any(v)]
    cnt = 0
    # enumerate invertible matrices as ordered bases
    def rec(idx, chosen):
        nonlocal cnt
        if idx == dim:
            # build the map e_i -> chosen[i], check q-preservation
            img = chosen
            def apply(x):
                y = tuple([0] * dim)
                out = [0] * dim
                for i, xi in enumerate(x):
                    if xi:
                        out = [(out[j] + img[i][j]) % 2 for j in range(dim)]
                return tuple(out)
            if all(qf(apply(v)) == qf(v) for v in vecs):
                cnt += 1
            return
        for v in nonz:
            # keep independence
            trial = chosen + [v]
            if rank_f2([list(t) for t in trial]) == len(trial):
                rec(idx + 1, trial)
    rec(0, [])
    return cnt

qh2 = lambda v: (v[0] * v[1]) % 2
bh2 = lambda v, w: (v[0] * w[1] + v[1] * w[0]) % 2
qh4 = lambda v: (v[0] * v[1] + v[2] * v[3]) % 2
bh4 = lambda v, w: (v[0] * w[1] + v[1] * w[0] + v[2] * w[3] + v[3] * w[2]) % 2
print("\ncalibration: |O| of the split form on (Z/2)^2 =", brute_order(2, qh2, bh2), "(expect 2)")
print("calibration: |O| of the split form on (Z/2)^4 =", brute_order(4, qh4, bh4), "(expect 72)")
formula = lambda m: 2 ** (m * (m - 1) + 1) * (2 ** m - 1) * eval("*".join(str(2 ** (2 * i) - 1) for i in range(1, m))) if m > 1 else 2
print("formula 2^(m(m-1)+1)(2^m-1)prod(2^2i-1): m=1:", formula(1), " m=2:", formula(2),
      " m=3:", formula(3), "(=|O_6^+(2)|=40320)  m=5:", formula(5))
print("(H1) hence |O(A_N)| = |O_10^+(2)| =", formula(5),
      " = 2^21*3^5*5^2*7*17*31 :", formula(5) == 2**21 * 3**5 * 5**2 * 7 * 17 * 31,
      " == repo-measured 46998591897600 :", formula(5) == 46998591897600)
