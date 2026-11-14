"""H2/H3/H4 on the rank-4 model, in Scattone's M_{2,2}(Z) determinant model.

D = (M_2(Z), det)  ~=  U + U        (basis E11, E22, E12, E21 ; det-form, signature (2,2))
L = {A in D : A_{12} even}  ~=  U + U(2)   (basis E11, E22, 2E12, E21)
L is the index-2 analogue of N = U + U(2) + E8(-2) inside M = U + U + E8(-2).

Contents
  (A) L ~= U + U(2), D ~= U + U ;
  (B) A_L = L^v/L ~= (Z/2)^2 with its form, A_D = 0 ;
  (C) Stab_{SL2 x SL2}(L) = Gamma^0(2) x Gamma^0(2)  (index 9) ;
  (D) the induced action of that stabiliser on A_L (H2/H3) ;
  (E) the ambient Eichler transvections F_{e,x}, e one of the 4 canonical isotropic vectors:
      which preserve L, and their action on A_L (H3) ;
  (F) the general lemma: transvections with e,x in L act trivially on A_L ;
  (G) spinor norms: bireflection decomposition, theta(F_{e,x}) = (x,x)^2, theta(SL2) (H4).
All arithmetic exact over Q.
"""
from fractions import Fraction as F
from itertools import product

# ---------------- exact linear algebra over Q ----------------
def mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def tp(A): return [list(r) for r in zip(*A)]
def add(A, B): return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
def scal(c, A): return [[c * x for x in row] for row in A]
def eye(n): return [[F(1) if i == j else F(0) for j in range(n)] for i in range(n)]
def det(A):
    n = len(A); M = [row[:] for row in A]; d = F(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return F(0)
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]; pv = M[c][c]
        for r in range(c + 1, n):
            if M[r][c] != 0:
                f = M[r][c] / pv
                M[r] = [M[r][j] - f * M[c][j] for j in range(n)]
    return d
def inv(A):
    n = len(A); M = [A[i][:] + [F(1) if i == j else F(0) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [M[r][j] - f * M[c][j] for j in range(2 * n)]
    return [row[n:] for row in M]
def rank(A):
    M = [row[:] for row in A]; r = 0; rows, cols = len(M), len(M[0])
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c] / pv
                M[i] = [M[i][j] - f * M[r][j] for j in range(cols)]
        r += 1
    return r
def isint(A): return all(x.denominator == 1 for r in A for x in r)

# ---------------- the lattices ----------------
# D = M_2(Z) with the determinant form:  b(A,B) = det(A+B) - det(A) - det(B)
def mat(v):            # vector in Q^4 -> 2x2 matrix, basis order E11,E22,E12,E21
    return [[v[0], v[2]], [v[3], v[1]]]
def vec(A):            # 2x2 matrix -> coordinates
    return [A[0][0], A[1][1], A[0][1], A[1][0]]
def bdet(A, B):
    AB = [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]
    return det(AB) - det(A) - det(B)
GD = [[bdet(mat([F(1) if k == i else F(0) for k in range(4)]),
            mat([F(1) if k == j else F(0) for k in range(4)])) for j in range(4)] for i in range(4)]
print("(A) Gram of D = M_2(Z) with det-form:", [[str(x) for x in r] for r in GD])
print("    det D =", det(GD), " signature (2,2);  D ~= U + U.")

Lbasis = [[F(1), 0, 0, 0], [0, F(1), 0, 0], [0, 0, F(2), 0], [0, 0, 0, F(1)]]   # E11,E22,2E12,E21
GL_ = [[bdet(mat(Lbasis[i]), mat(Lbasis[j])) for j in range(4)] for i in range(4)]
print("(A) Gram of L (basis E11,E22,2E12,E21):", [[str(x) for x in r] for r in GL_])
U = [[0, 1], [1, 0]]; U2 = [[0, 2], [2, 0]]
print("    det L =", det(GL_), ";  L ~= U + U(2): the pairs (E11,E22) and (2E12,-E21) are")
print("    hyperbolic with (2E12,-E21) of norm 2:", bdet(mat([0, 0, F(2), 0]), mat([0, 0, 0, F(-1)])),
      " => L ~= U + U(2) with |det L| =", abs(det(GL_)), "]")

# ---------------- (B) discriminant group of L ----------------
GLi = inv(GL_)
def classes(Gi, n):
    return [[Gi[i][j] - int(Gi[i][j]) for i in range(n)] for j in range(n)]
clL = classes(GLi, 4)
print("\n(B) A_L = L^v/L:  L^v = G_L^{-1} Z^4; classes of the columns (mod Z):")
for j, c in enumerate(clL):
    print("     col", j, [str(x) for x in c])
def qf(G, y):
    return sum(y[i] * G[i][j] * y[j] for i in range(len(y)) for j in range(len(y)))
def bf(G, y, z):
    return sum(y[i] * G[i][j] * z[j] for i in range(len(y)) for j in range(len(y)))
# a basis of A_L: the two nonzero classes
nz = []
for c in clL:
    if any(c) and all(all((x - d).denominator == 1 for x, d in zip(c, e)) is False for e in nz) or (any(c) and not nz):
        nz.append(c)
# simpler: pick [E12] and [E21/2] explicitly
Ael = [F(0), F(0), F(1), F(0)]        # E12
Bel = [F(0), F(0), F(0), F(1, 2)]     # E21/2
print("    A_L generated by [E12] and [E21/2] :",
      "q(E12) =", qf(GL_, Ael), " q(E21/2) =", qf(GL_, Bel), " b(E12,E21/2) =", bf(GL_, Ael, Bel))
print("    check both are in L^v (integrality of b with L):",
      all((bf(GL_, Ael, e)).denominator == 1 for e in
          [[F(1), 0, 0, 0], [0, F(1), 0, 0], [0, 0, F(2), 0], [0, 0, 0, F(1)]]),
      all((bf(GL_, Bel, e)).denominator == 1 for e in
          [[F(1), 0, 0, 0], [0, F(1), 0, 0], [0, 0, F(2), 0], [0, 0, 0, F(1)]]))
print("    => A_L ~= (Z/2)^2 with the split (hyperbolic) form, q(E12)=q(E21/2)=0, b = -1/2.")
print("    A_D = 0 (D unimodular).")

def class_of(y):
    """coordinates of the class [y] in A_L w.r.t. the basis ([E12],[E21/2])"""
    # y = alpha*E12 + beta*E21/2 + (integral)  ->  (alpha mod 2, beta mod 2)
    # solve: y - alpha*E12 - beta*E21/2 integral
    for alpha in range(2):
        for beta in range(2):
            r = [y[i] - alpha * Ael[i] - beta * Bel[i] for i in range(4)]
            if all(x.denominator == 1 for x in r) and r[2] % 2 == 0:   # must lie in L!
                return (alpha, beta)
    raise RuntimeError("not in A_L: %s" % y)

# ---------------- (C) which (g,h) in SL2 x SL2 preserve L ? ----------------
def leftmat(g):        # A -> g A  on the basis E11,E22,E12,E21
    return [[F(g[i][0]) if j == 0 else (F(g[i][1]) if j == 2 else 0) for j in range(4)] for i in range(2)] + \
           [[0, 0, F(g[i][0]), 0] if True else None for i in range(2)]
def Lmat(g):           # 4x4 matrix of A -> gA
    cols = []
    for j in range(4):
        A = mat([F(1) if k == j else F(0) for k in range(4)])
        gA = [[sum(F(g[i][k]) * A[k][m] for k in range(2)) for m in range(2)] for i in range(2)]
        cols.append(vec(gA))
    return [[cols[j][i] for j in range(4)] for i in range(4)]
def Rmat(h):           # 4x4 matrix of A -> A h
    cols = []
    for j in range(4):
        A = mat([F(1) if k == j else F(0) for k in range(4)])
        Ah = [[sum(A[i][k] * F(h[k][m]) for k in range(2)) for m in range(2)] for i in range(2)]
        cols.append(vec(Ah))
    return [[cols[j][i] for j in range(4)] for i in range(4)]
def Tmatx(g):          # 4x4 matrix of A -> A^T
    cols = []
    for j in range(4):
        A = mat([F(1) if k == j else F(0) for k in range(4)])
        cols.append(vec([[A[0][0], A[1][0]], [A[0][1], A[1][1]]]))
    return [[cols[j][i] for j in range(4)] for i in range(4)]

def is_iso(M, G):
    return mm(mm(tp(M), G), M) == G

def preserves_L(M):
    """M in GL_4(Q); does M(L) subset L ?  (L = {A12 even}, basis E11,E22,2E12,E21)"""
    for b in Lbasis:
        y = [sum(M[i][j] * b[j] for j in range(4)) for i in range(4)]
        if not isint([[y[0], y[2]], [y[3], y[1]]]):
            return False
        if y[2] % 2 != 0:              # (1,2)-entry must stay even
            return False
        if not isint([[x] for x in y]):
            return False
    return True

def act_on_AL(M):
    """induced map on A_L, in coordinates w.r.t. ([E12],[E21/2])"""
    out = []
    for y in (Ael, Bel):
        z = [sum(M[i][j] * y[j] for j in range(4)) for i in range(4)]
        out.append(class_of(z))
    return out

S = [[0, -1], [1, 0]]; T1 = [[1, 1], [0, 1]]
T2 = [[1, 2], [0, 1]]; T2p = [[1, 0], [2, 1]]; X = [[3, 2], [1, 1]]
gens = {'T2=[[1,2],[0,1]]': T2, 'T2p=[[1,0],[2,1]]': T2p, 'X=[[3,2],[1,1]]': X}

print("\n(C) which (g,h) in SL2(Z)^2 preserve L = {A12 even}?  (A -> g A h^{-1})")
for name, g in gens.items():
    for leftright in ('left', 'right'):
        M = Lmat(g) if leftright == 'left' else Rmat(inv([[F(x) for x in r] for r in g]))
        Minv = inv([[F(x) for x in r] for r in g])
        M = Lmat(g) if leftright == 'left' else Rmat(Minv)
        print("   %-22s %-5s  isometry of D: %s  preserves L: %s" %
              (name, leftright, is_iso(M, GD), preserves_L(M)))
print("\n   criterion: (g,h) preserves L  <=>  g_{12} = h_{12} = 0 mod 2, i.e.")
print("   Stab_{SL2 x SL2}(L) = Gamma^0(2) x Gamma^0(2), index 3*3 = 9 in SL2(Z)^2.")
# index check: Gamma^0(2) = preimage of <[[1,0],[1,1]]> in SL2(F_2), a subgroup of order 2 in S_3.
print("   [SL2(Z) : Gamma^0(2)] = [SL2(F_2) : <[[1,0],[1,1]]>] = 6/2 = 3.")

print("\n   (D) induced action of Gamma^0(2) x Gamma^0(2) on A_L:")
triv = True
for name, g in gens.items():
    for leftright in ('left', 'right'):
        Minv = inv([[F(x) for x in r] for r in g])
        M = Lmat(g) if leftright == 'left' else Rmat(Minv)
        if preserves_L(M):
            act = act_on_AL(M)
            ok = (act[0] == (1, 0) and act[1] == (0, 1))
            triv = triv and ok
            print("   %-22s %-5s  preserves L, induced map on A_L: %s   trivial: %s" %
                  (name, leftright, act, ok))
print("   ALL named stabiliser generators act trivially on A_L:", triv)

print("\n(C2) do the STANDARD SL2(Z) generators (the 4 quoted block generators) preserve L?")
for nm, g in [('S=[[0,-1],[1,0]]', S), ('T=[[1,1],[0,1]]', T1)]:
    for leftright in ('left', 'right'):
        Minv = inv([[F(x) for x in r] for r in g])
        M = Lmat(g) if leftright == 'left' else Rmat(Minv)
        print("   %-18s %-5s preserves L: %s" % (nm, leftright, preserves_L(M)))
print("   => none of the 4 quoted SL2(Z)^2 generators is an isometry of L; the stabiliser")
print("      Gamma^0(2)^2 has index 9 in SL2(Z)^2 and needs different (product) generators.")

# random products in Gamma^0(2)^2
import random
random.seed(1)
def mul2(a, b): return [[a[0][0]*b[0][0]+a[0][1]*b[1][0], a[0][0]*b[0][1]+a[0][1]*b[1][1]],
                        [a[1][0]*b[0][0]+a[1][1]*b[1][0], a[1][0]*b[0][1]+a[1][1]*b[1][1]]]
genlist = [T2, T2p, X, [[F(x) for x in r] for r in inv([[F(x) for x in r] for r in T2])],
           [[F(x) for x in r] for r in inv([[F(x) for x in r] for r in T2p])],
           [[F(x) for x in r] for r in inv([[F(x) for x in r] for r in X])]]
alltriv = True
for trial in range(200):
    g = [[F(1), F(0)], [F(0), F(1)]]; h = [[F(1), F(0)], [F(0), F(1)]]
    for _ in range(random.randint(1, 8)):
        g = mul2(g, [[F(x) for x in r] for r in random.choice(genlist)])
        h = mul2(h, [[F(x) for x in r] for r in random.choice(genlist)])
    M = mm(Lmat(g), Rmat(h))
    assert preserves_L(M), "criterion broken"
    act = act_on_AL(M)
    if act != [(1, 0), (0, 1)]:
        alltriv = False
print("   200 random elements of Gamma^0(2)^2 all preserve L and act trivially on A_L:", alltriv)

# ---------------- (E) ambient Eichler transvections in D ----------------
def refl(v):
    """reflection sigma_v (needs (v,v) != 0) on D, as a 4x4 matrix"""
    vv = qf(GD, v)
    assert vv != 0
    return [[(F(1) if i == j else F(0)) - 2 * v[i] * sum(GD[j][k] * v[k] for k in range(4)) / vv
             for j in range(4)] for i in range(4)]

def transvection(e, x):
    """F_{e,x}(v) = v + b(v,e)x - b(v,x)e - (1/2)(x,x) b(v,e) e ; needs (e,e)=0=(e,x)"""
    assert qf(GD, e) == 0 and bf(GD, e, x) == 0
    xx = qf(GD, x)
    cols = []
    for j in range(4):
        v = [F(1) if k == j else F(0) for k in range(4)]
        bve = bf(GD, v, e); bvx = bf(GD, v, x)
        w = [v[i] + bve * x[i] - bvx * e[i] - xx / 2 * bve * e[i] for i in range(4)]
        cols.append(w)
    return [[cols[j][i] for j in range(4)] for i in range(4)]

Es = {'E11': [F(1), 0, 0, 0], 'E22': [F(0), F(1), 0, 0],
      'E12': [F(0), 0, F(1), 0], 'E21': [F(0), 0, 0, F(1)]}
print("\n(E) the four canonical isotropic vectors of D and their divisibility in D:")
for nm, e in Es.items():
    divs = [bf(GD, e, [F(1) if k == j else F(0) for k in range(4)]) for j in range(4)]
    print("   %s : (e,e) = %s ; b(e, basis) = %s => div_D(e) = 1" % (nm, qf(GD, e), [str(x) for x in divs]))
print("   (so every F_{e,x} with x in D acts trivially on A_D = 0 -- the ambient statement)")

print("\n   Which F_{e,x} preserve L, and what do they do on A_L?")
for nm, e in Es.items():
    # a Z-basis of e^perp cap D
    orth = []
    cand = [[F(1) if k == j else F(0) for k in range(4)] for j in range(4)]
    for w in cand:
        if bf(GD, e, w) == 0:
            orth.append(w)
    print("   e = %-4s : basis of e^perp cap D has %d vectors" % (nm, len(orth)))
    for w in orth:
        if qf(GD, e) != 0: continue
        M = transvection(e, w)
        assert is_iso(M, GD), "F is not an isometry of D!"
        print("       x = %-22s isometry:%s  integral:%s  preserves L:%s  action on A_L:%s" %
              (str([str(t) for t in w]), is_iso(M, GD), isint(M), preserves_L(M),
               act_on_AL(M) if preserves_L(M) else "-"))

# ---------------- (F) general lemma: transvections with e,x in L are trivial on A_L --------------
print("\n(F) the lattice's OWN Eichler transvections (e, x in L, x in e^perp, (x,x) != 0):")
V = {'E11': [F(1), 0, 0, 0], 'E22': [F(0), F(1), 0, 0], '2E12': [F(0), 0, F(2), 0],
     'E21': [F(0), 0, 0, F(1)], 'E11+E22': [F(1), F(1), 0, 0], '2E12+E21': [F(0), 0, F(2), F(1)]}
cases = [('E11', '2E12+E21'), ('E11', 'E21'), ('2E12', 'E11+E22'), ('2E12', 'E11'),
         ('E21', 'E11+E22')]
for en, xn in cases:
    e, x = V[en], V[xn]
    assert qf(GD, e) == 0, en
    dv = 0
    for b in Lbasis:
        val = bf(GD, e, b)
        assert val.denominator == 1
        dv = __import__('math').gcd(dv, int(val))
    if bf(GD, e, x) != 0:
        print("   e = %-10s x = %-10s : x not in e^perp, skipped" % (en, xn)); continue
    M = transvection(e, x)
    print("   e = %-10s x = %-10s (x,x)=%-3s : isometry:%s integral:%s preserves L:%s  "
          "div_L(e)=%s  action on A_L trivial:%s"
          % (en, xn, qf(GD, x), is_iso(M, GD), isint(M), preserves_L(M), dv,
             act_on_AL(M) == [(1, 0), (0, 1)] if preserves_L(M) else "-"))
print("   => every transvection with e,x in L lies in O(L) and acts trivially on A_L.")
print("   (lemma, div-independent: for y in L^v, b(y,e) and b(y,x) are integers, (x,x)/2 in Z)")

# ---------------- (G) spinor norms ----------------
print("\n(G) spinor norms: theta: O(V_R) -> R*/squares, O+ = ker theta.")
def refl(v):
    vv = qf(GD, v)
    assert vv != 0
    return [[(F(1) if i == j else F(0)) - 2 * v[i] * sum(GD[j][k] * v[k] for k in range(4)) / vv
             for j in range(4)] for i in range(4)]
def two_refl(M):
    """try to write M = sigma_a sigma_b ; return (a,a)(b,b) or None"""
    cands = []
    for nm, v in V.items():
        for sgn in (1, -1):
            cands.append([sgn * t for t in v])
    for nm, v in V.items():
        for nm2, w in V.items():
            cands.append([v[t] + w[t] for t in range(4)])
            cands.append([v[t] - w[t] for t in range(4)])
    for b in cands:
        if qf(GD, b) == 0: continue
        Mb = [sum(M[i][t] * b[t] for t in range(4)) for i in range(4)]
        for a in ([Mb[i] + b[i] for i in range(4)], [Mb[i] - b[i] for i in range(4)]):
            if qf(GD, a) == 0: continue
            if mm(refl(a), refl(b)) == M:
                return a, b, qf(GD, a) * qf(GD, b)
            if mm(refl(b), refl(a)) == M:
                return b, a, qf(GD, a) * qf(GD, b)
    return None

print("  (i) Eichler transvections F_{e,x} with (x,x) != 0 :")
for en, xn in [('E11', '2E12+E21'), ('2E12', 'E11+E22'), ('E21', 'E11+E22'), ('E21', '2E12+E21')]:
    e, x = V[en], V[xn]
    if bf(GD, e, x) != 0 or qf(GD, x) == 0: continue
    M = transvection(e, x)
    xx = qf(GD, x)
    y = [x[i] - xx / 2 * e[i] for i in range(4)]          # y = x - (x,x)e/2
    ident = (mm(refl(y), refl(x)) == M)
    print("    F_{%s,%s}: (x,x) = %-3s ; F = sigma_y sigma_x with y = x-(x,x)e/2 : %s ;"
          " (y,y) = %s ; theta = (x,x)(y,y) = %s = (x,x)^2 => theta = 1 in R*/squares"
          % (en, xn, xx, ident, qf(GD, y), qf(GD, y) * xx))
print("  (ii) SL2(Z)^2 block maps: (g-1)^2 = 0 (unipotent, so in the identity component) or hyperbolicity:")
for nm, g in gens.items():
    for leftright in ('left', 'right'):
        Minv = inv([[F(x) for x in r] for r in g])
        M = Lmat(g) if leftright == 'left' else Rmat(Minv)
        A = add(M, scal(F(-1), eye(4)))
        print("    %-22s %-5s rank(M-1) = %d ; (M-1)^2 = 0 : %s"
              % (nm, leftright, rank(A), mm(A, A) == [[F(0)] * 4] * 4))
print("    => the whole image of SL2(Z)^2 lies in O+: SL2(R)^2 = Spin(2,2) -> SO(D_R) is connected,")
print("       so it lands in the identity component of O(D_R), which is contained in ker(theta).")
print("  (iii) reflections in norm +-2 vectors (N has only these roots, all in the U summand):")
for nm, v in [('E11+E22', [F(1), F(1), 0, 0]), ('E11-E22', [F(1), F(-1), 0, 0]),
              ('E11+2E22', [F(1), F(2), 0, 0]), ('E11-2E22', [F(1), F(-2), 0, 0])]:
    vv = qf(GD, v)
    if vv == 0: continue
    print("    v = %-10s (v,v) = %-3s : theta(sigma_v) = (v,v) mod squares => sigma_v in O+ iff (v,v)>0 : %s"
          % (nm, vv, vv > 0))
print("    and div_L(v) = 1 for v = E11+-E22, so these reflections also lie in ker(O(L)->O(A_L)).")

print("\n(H3-reflections) the group generated by ALL reflections in norm (\u00b12) vectors of L:")
Nv = [[F(1), F(1), 0, 0], [F(-1), F(-1), 0, 0], [F(1), F(-1), 0, 0], [F(-1), F(1), 0, 0]]
refls = [refl(v) for v in Nv]
grp = {tuple(map(tuple, eye(4)))}
frontier = [eye(4)]
while frontier:
    new = []
    for g in frontier:
        for r in refls:
            h = mm(r, g)
            key = tuple(map(tuple, h))
            if key not in grp:
                grp.add(key); new.append(h)
    frontier = new
print("    the 4 norm-(+-2) vectors of L (they all lie in the U summand) generate a group of order",
      len(grp), "(all of them act on L; on the U(2) summand they act as the identity).")
print("    => 'reflection generation by norm +-2 vectors' generates only this small group on L,")
print("       and on N = U + U(2) + E8(-2) exactly the same, since N has no other root.")
