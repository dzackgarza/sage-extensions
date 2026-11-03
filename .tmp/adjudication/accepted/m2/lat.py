"""Exact integer-lattice helpers (Fractions, no floats). Rank <= 8, small data only.

Conventions: a lattice L is an integer symmetric Gram matrix G (basis e_1..e_n).
Vector v = integer coordinate column.  q(v) = v^T G v,  b(v,w) = v^T G w.
L^v = {x in Q^n : Gx in Z^n} ;  A_L = L^v/L  <->  class of y in Z^n/GZ^n via x = G^{-1}y,
q_A(y) = y^T G^{-1} y  in  Q/2Z.
An isometry M in O(L) (M^T G M = G) acts on A_L by y |-> (G M G^{-1}) y.
"""
from fractions import Fraction
from itertools import product


def T(A):
    return [list(r) for r in zip(*A)]


def mul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]


def mv(A, v):
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def idm(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def inv_frac(A):
    n = len(A)
    M = [[Fraction(A[i][j]) for j in range(n)] + [Fraction(1 if i == j else 0) for j in range(n)]
         for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(2 * n)]
    return [row[n:] for row in M]


def det_frac(A):
    n = len(A)
    M = [[Fraction(x) for x in row] for row in A]
    d = Fraction(1)
    for c in range(n):
        p = None
        for r in range(c, n):
            if M[r][c] != 0:
                p = r
                break
        if p is None:
            return Fraction(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d *= M[c][c]
        pv = M[c][c]
        for r in range(c + 1, n):
            if M[r][c] != 0:
                f = M[r][c] / pv
                M[r] = [M[r][j] - f * M[c][j] for j in range(n)]
    return d


class Lat:
    def __init__(self, G, name=""):
        self.G = [[int(x) for x in row] for row in G]
        self.n = len(G)
        self.name = name
        self.Gi = inv_frac(self.G)
        self.det = det_frac(self.G)

    def q(self, v):
        return sum(v[i] * self.G[i][j] * v[j] for i in range(self.n) for j in range(self.n))

    def b(self, v, w):
        return sum(v[i] * self.G[i][j] * w[j] for i in range(self.n) for j in range(self.n))

    def even(self):
        return all(self.q([1 if k == i else 0 for k in range(self.n)]) % 2 == 0 for i in range(self.n))

    def is_iso(self, M):
        G = self.G
        return mul(mul(T(M), G), M) == G

    # ---- discriminant group A_L = Z^n / G Z^n ----
    def classes(self):
        """all classes of Z^n / col(G) as tuples (y mod col G), brute force over a box."""
        # bounding box: use Smith-like bound via |det| ; enumerate y with 0<=y_i<m_i where m_i from HNF
        cols = [[self.G[r][j] for r in range(self.n)] for j in range(self.n)]
        # integer column reduction to get a box: use diagonal of the HNF of G
        H = hnf(self.G)
        box = [abs(H[i][i]) for i in range(self.n)]
        seen = {}
        for y in product(*[range(b) for b in box]):
            y = tuple(y)
            rep = self.canon(y)
            if rep not in seen:
                seen[rep] = y
        return seen  # rep -> a representative y

    def canon(self, y):
        """canonical rep of y mod col(G): reduce x = G^{-1} y mod Z^n."""
        y = [Fraction(v) for v in y]
        x = mv(self.Gi, y)
        x = [xi - Fraction(xi.numerator // xi.denominator) for xi in x]  # mod 1
        # x = G^{-1} y'  => y' = G x
        yp = mv(self.G, x)
        out = []
        for v in yp:
            assert v.denominator == 1
            out.append(int(v))
        return tuple(out)

    def qA(self, y):
        """quadratic form on A_L at class of y, in Q/2Z, returned as Fraction mod 2."""
        y = [Fraction(v) for v in y]
        s = sum(y[i] * self.Gi[i][j] * y[j] for i in range(self.n) for j in range(self.n))
        return s % 2

    def action_on_A(self, M):
        """matrix of the induced action on Z^n/GZ^n : y -> G M G^{-1} y (must be integral)."""
        A = mul(mul(self.G, M), self.Gi)
        out = []
        for row in A:
            r = []
            for v in row:
                assert v.denominator == 1, ("non-integral discriminant action", v)
                r.append(int(v))
            out.append(r)
        return out

    def trivial_on_A(self, M):
        A = self.action_on_A(M)
        I = idm(self.n)
        D = [[A[i][j] - I[i][j] for j in range(self.n)] for i in range(self.n)]
        # columns of D must lie in col(G)
        for j in range(self.n):
            c = [Fraction(D[i][j]) for i in range(self.n)]
            x = mv(self.Gi, c)
            if any(v.denominator != 1 for v in x):
                return False
        return True


def hnf(A):
    """column-style HNF of integer matrix A (row reduction over columns is enough for a box)."""
    n = len(A)
    M = [[int(A[i][j]) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = None
        for r in range(c, n):
            if M[r][c] != 0:
                p = r
                break
        if p is None:
            continue
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            while M[r][c] != 0:
                f = M[r][c] // M[c][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(n)]
                if M[r][c] != 0:
                    M[c], M[r] = M[r], M[c]
        for r in range(c):
            M[c][r] = M[c][r] % M[c][c] if M[c][c] else M[c][r]
    return M


def transvection(L, e, x):
    """Eichler transvection tau_{e,x}(v) = v - (v,e)x + (v,x)e - ((x,x)/2)(v,e)e
    (defined for e isotropic, x in e-perp, L even). Returns integer matrix."""
    n = L.n
    Ge = mv(L.G, e)
    Gx = mv(L.G, x)
    T4 = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            T4[i][j] = -x[i] * Ge[j] + e[i] * Gx[j] - Fraction(L.q(x), 2) * e[i] * Ge[j]
    M = [[idm(n)[i][j] + T4[i][j] for j in range(n)] for i in range(n)]
    out = []
    for row in M:
        r = []
        for v in row:
            if v.denominator != 1:
                return None  # not integral
            r.append(int(v))
        out.append(r)
    return out


def reflection(L, v):
    """tau_v(w) = w - 2(w,v)/(v,v) v  (returns None if not integral)."""
    qv = L.q(v)
    if qv == 0:
        return None
    n = L.n
    Gv = mv(L.G, v)
    M = [[(1 if i == j else 0) - Fraction(2 * v[i] * Gv[j], qv) for j in range(n)] for i in range(n)]
    out = []
    for row in M:
        r = []
        for x in row:
            if x.denominator != 1:
                return None
            r.append(int(x))
        out.append(r)
    return out


U = [[0, 1], [1, 0]]
U2 = [[0, 2], [2, 0]]
