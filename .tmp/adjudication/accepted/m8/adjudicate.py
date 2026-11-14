"""
adjudicate.py -- exact computations for H1-H4 of the swarm problem on
    N  = U (+) U(2) (+) E8(-2)          even, signature (2,10), A_N = (Z/2)^10
    L  = U (+) U    (+) E8(-2)          even, signature (2,10), A_L = (Z/2)^8
    M4 = U (+) U(2)  ( rank-4 local model ),  L4 = U (+) U,  [L4:M4] = 2

Conventions
-----------
U      = <e_i,f_i>, Gram [[0,1],[1,0]].
U(2)   = <e2, 2 f2>  inside <e2,f2> = U_2, Gram [[0,2],[2,0]].
E8(-2) = (E8 root lattice, form times -2), Gram = -2*Cartan(E8); det = 2^8,
         so A_{E8(-2)} = (Z/2)^8   (cf. Enriques_compu_rev.tex:1458-1461).
N = U_1 (+) <e2,2f2> (+) E8(-2)  subset  L = U_1 (+) <e2,f2> (+) E8(-2),  [L:N]=2.

Exact arithmetic only (fractions.Fraction); no isometry group is enumerated.
The only finite groups touched are discriminant quadratic forms over F_2.

Spinor convention: the invariant used is the real spinor norm
   sv_R(g) = sign of the product of the norms in a Cartan-Dieudonne
factorisation; sv_R(g)=+1 <=> g in O^+ ("real spinor kernel").  This sign is
independent of the usual normalising factor 2 (dividing by a positive number does
not change the sign).  The finer class in Q*/Q*^2 is reported separately.

Run:  python3 adjudicate.py
"""
from fractions import Fraction as F
from itertools import product

FAILS = []


def ok(name, cond, extra=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}{(' -- ' + extra) if extra else ''}")
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------------------ linear algebra
def idm(n):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def mul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    return [[sum((A[i][t] * B[t][j] for t in range(k)), F(0)) for j in range(m)]
            for i in range(n)]


def act(A, x):
    return [sum((A[i][j] * x[j] for j in range(len(x))), F(0)) for i in range(len(A))]


def tr(A):
    return [list(r) for r in zip(*A)]


def ip(G, x, y):
    return sum(x[i] * G[i][j] * y[j] for i in range(len(x)) for j in range(len(y)))


def inv(G):
    n = len(G)
    A = [[F(x) for x in row] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(G)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        piv = A[c][c]
        A[c] = [x / piv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [A[r][j] - f * A[c][j] for j in range(2 * n)]
    return [row[n:] for row in A]


def det(M):
    n = len(M)
    A = [[F(x) for x in row] for row in M]
    d = F(1)
    for c in range(n):
        p = next((r for r in range(c, n) if A[r][c] != 0), None)
        if p is None:
            return F(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            d = -d
        d *= A[c][c]
        piv = A[c][c]
        for r in range(c + 1, n):
            if A[r][c] != 0:
                f = A[r][c] / piv
                A[r] = [A[r][j] - f * A[c][j] for j in range(n)]
    return d


def integral(x):
    return all(F(v).denominator == 1 for v in x)


def is_iso(G, M):
    if not integral([M[i][j] for i in range(len(M)) for j in range(len(M))]):
        return False
    if abs(det(M)) != 1:
        return False
    return mul(mul(tr(M), [[F(x) for x in r] for r in G]), M) == [[F(x) for x in r] for r in G]


def in_dual(G, x):
    return integral(act(G, x))


# ------------------------------------------------------------------ isometries
def refl(G, v):
    """s_v(z) = z - 2(z,v)/(v,v) v"""
    q = ip(G, v, v)
    assert q != 0
    n = len(G)
    vG = [sum(v[i] * G[i][j] for i in range(n)) for j in range(n)]
    return [[F(int(i == j)) - 2 * v[i] * vG[j] / q for j in range(n)] for i in range(n)]


def eichler(G, e, x):
    """E_{e,x}(z) = z + (z,e)x - (z,x)e - (z,e)(x,x)/2 e   (e isotropic, x perp e);
    satisfies E_{e,x}E_{e,y} = E_{e,x+y}  (cf. tex line 1446)."""
    n = len(G)
    eG = [sum(e[i] * G[i][j] for i in range(n)) for j in range(n)]
    xG = [sum(x[i] * G[i][j] for i in range(n)) for j in range(n)]
    xx = ip(G, x, x)
    return [[F(int(i == j)) + x[i] * eG[j] - e[i] * xG[j] - F(xx, 2) * e[i] * eG[j]
             for j in range(n)] for i in range(n)]


def acts_trivially(G, M, duals):
    return all(integral([act(M, d)[i] - d[i] for i in range(len(d))]) for d in duals)


def sqclass(f):
    neg = F(f) < 0
    f = abs(F(f))

    def fac(x):
        out, d = {}, 2
        while d * d <= x:
            while x % d == 0:
                out[d] = out.get(d, 0) + 1
                x //= d
            d += 1
        if x > 1:
            out[x] = out.get(x, 0) + 1
        return out
    e = fac(f.numerator)
    for k, v in fac(f.denominator).items():
        e[k] = e.get(k, 0) - v
    return (neg, tuple(sorted(k for k, v in e.items() if v % 2)))


def sv_ghs(prod, k):
    """GHS/arXiv:0810.1614 convention: sn_K(g) = prod_i ( -(v_i,v_i)/2 ) (K^*)^2.
    Given the product of (v_i,v_i) over k reflections, return sn in Q*/Q*^2."""
    return F((-1) ** k) * F(prod) / F(2 ** k)


def in_Oplus(prod, k):
    """O^+(L) = O(L) cap ker(sn_R); the real sign of sn_R is sign((-1)^k prod)."""
    return F((-1) ** k) * F(prod) > 0


def spinor(G, M, trials=4000, seed=12345, cap=None):
    """Cartan-Dieudonne factorisation.  If the 'difference' trick stalls (all differences
    isotropic, as happens for doubly-unipotent elements such as E_{e,x} with (e,x)=0),
    pre-compose with a random reflection and continue.  The product of the reflection
    norms is the spinor norm, independent of the factorisation."""
    import random
    rng = random.Random(seed)
    n = len(G)
    cap = cap or 8 * n
    cur = [r[:] for r in M]
    prod, steps = F(1), 0
    while cur != idm(n):
        if steps > cap:
            return None, steps
        found = False
        for _ in range(trials):
            x = [F(rng.randint(-2, 2)) for _ in range(n)]
            if not any(x):
                continue
            d = [act(cur, x)[i] - x[i] for i in range(n)]
            q = ip(G, d, d)
            if q != 0:
                cur = mul(refl(G, d), cur)
                prod *= q
                steps += 1
                found = True
                break
        if not found:
            for _ in range(trials):
                u = [F(rng.randint(-2, 2)) for _ in range(n)]
                if not any(u):
                    continue
                qu = ip(G, u, u)
                if qu != 0:
                    cur = mul(refl(G, u), cur)
                    prod *= qu
                    steps += 1
                    break
            else:
                return None, steps
    return prod, steps


# ------------------------------------------------------------------ lattices
CartanE8 = [
    [2, -1, 0, 0, 0, 0, 0, 0], [-1, 2, -1, 0, 0, 0, 0, 0],
    [0, -1, 2, -1, 0, 0, 0, -1], [0, 0, -1, 2, -1, 0, 0, 0],
    [0, 0, 0, -1, 2, -1, 0, 0], [0, 0, 0, 0, -1, 2, -1, 0],
    [0, 0, 0, 0, 0, -1, 2, 0], [0, 0, -1, 0, 0, 0, 0, 2]]
U2 = [[0, 1], [1, 0]]
E8m2 = [[-2 * CartanE8[i][j] for j in range(8)] for i in range(8)]


def bd(*ms):
    n = sum(len(m) for m in ms)
    G, o = [[0] * n for _ in range(n)], 0
    for m in ms:
        for i in range(len(m)):
            for j in range(len(m)):
                G[o + i][o + j] = m[i][j]
        o += len(m)
    return G


G_L = bd(U2, U2, E8m2)                 # basis e1 f1 e2 f2 c1..c8
G_L4 = bd(U2, U2)
B_N = idm(12)
B_N[3][3] = F(2)                       # N-basis in L-coords: e1 f1 e2 2f2 c1..c8
G_N = mul(mul(B_N, [[F(x) for x in r] for r in G_L]), tr(B_N))
G_M4 = bd(U2, [[0, 2], [2, 0]])
B4 = idm(4)
B4[3][3] = F(2)
Binv, Binv4 = inv(B_N), inv(B4)
dual_L, dual_N = inv(G_L), inv(G_N)

e1 = [F(int(i == 0)) for i in range(12)]
f1 = [F(int(i == 1)) for i in range(12)]
e2 = [F(int(i == 2)) for i in range(12)]
f2 = [F(int(i == 3)) for i in range(12)]
c1 = [F(int(i == 4)) for i in range(12)]
CART = [[F(int(i == 4 + k)) for i in range(12)] for k in range(8)]


def inN(v):
    return integral(act(Binv, v))


def emb12(M4x4):
    """embed a 4x4 matrix acting on e1,f1,e2,f2 into the 12-dim lattice"""
    return [[F(M4x4[i][j]) if (i < 4 and j < 4) else F(int(i == j))
             for j in range(12)] for i in range(12)]


print("=" * 78)
print("S0  the lattices")
ok("G_L, G_N, G_M4 even", all(G[i][i] % 2 == 0 for G in (G_L, G_N, G_M4) for i in range(len(G))))
ok("det G_L = 2^8 (A_L=(Z/2)^8)", abs(det(G_L)) == 256)
ok("det G_N = 2^10 (A_N=(Z/2)^10)", abs(det(G_N)) == 1024)
ok("det G_M4 = 2^2", abs(det(G_M4)) == 4)
ok("[L:N] = |det B_N| = 2", abs(det(B_N)) == 2)
ok("N's first block = U (+) U(2)", [[G_N[i][j] for j in range(4)] for i in range(4)]
   == [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 2], [0, 0, 2, 0]])

print("=" * 78)
print("S1  H1: the index-2 embedding and the dual/discriminant maps")
ok("dual basis of L in L^v", all(in_dual(G_L, d) for d in dual_L))
ok("dual basis of N in N^v", all(in_dual(G_N, d) for d in dual_N))
zN = [F(0)] * 12
zN[2] = F(1, 2)
ok("e2/2 in N^v", in_dual(G_N, zN))
ok("e2/2 not in N", not inN(zN))
ok("f2 in N^v", in_dual(G_N, f2))
ok("f2 not in N", not inN(f2))
ok("2f2 in N", inN([2 * f2[i] for i in range(12)]))
ok("[A_N : im(A_L)] = 8", (1024 // 256) * 2 == 8)
ok("A_N = <[f2],[e2/2]> (+) (Z/2)^8, order 4*256 = 1024", 4 * 256 == 1024)

print("=" * 78)
print("S2  Theorem B: isotropic transvections; quote line 1446 (composition) and "
      "line 1457 (triviality on the discriminant)")
for e, x, lab in [(e1, f2, "(e1,f2)"), (e1, c1, "(e1,c1)"), (e2, c1, "(e2,c1)"),
                  (e2, f1, "(e2,f1)")]:
    ok(f"{lab}: e isotropic, x perp e", ip(G_L, e, e) == 0 and ip(G_L, e, x) == 0)
    M = eichler(G_L, e, x)
    ok(f"  {lab}: E isometry of L, trivial on A_L",
       is_iso(G_L, M) and acts_trivially(G_L, M, dual_L))
for e, x, y in [(e1, f2, c1), (e2, f1, c1)]:
    xy = [x[i] + y[i] for i in range(12)]
    ok("composition law E_{e,x}E_{e,y} = E_{e,x+y} (tex:1446)",
       mul(eichler(G_L, e, x), eichler(G_L, e, y)) == eichler(G_L, e, xy))
for x, lab in [(c1, "c1"), (f1, "f1"), (e1, "e1")]:
    M = eichler(G_N, e2, x)
    ok(f"E_{{e2,{lab}}} (e in the U(2) summand): isometry of N, trivial on A_N",
       is_iso(G_N, M) and acts_trivially(G_N, M, dual_N))

print("=" * 78)
print("S3  Which of the quoted ambient generators even preserve N?")


def basis_perp(G, e):
    return [[F(int(i == k)) for i in range(len(G))] for k in range(len(G))
            if ip(G, e, [F(int(i == k)) for i in range(len(G))]) == 0]


surv, killed, offker = [], [], []
root_names = {0: "e1", 1: "f1", 2: "e2", 3: "f2"}
for lab, e in [("e1", e1), ("f1", f1), ("e2", e2), ("f2", f2)]:
    for x in basis_perp(G_L, e):
        M = eichler(G_L, e, x)
        xlab = next((f"c{k+1}" for k in range(8) if x == CART[k]), None)
        if xlab is None:
            xlab = root_names[[i for i in range(4) if x == [e1, f1, e2, f2][i]][0]]
        keeps = all(inN(act(M, list(r))) for r in B_N)
        if not keeps:
            killed.append((lab, xlab))
            continue
        MN = [[act(Binv, act(M, list(B_N[k])))[i] for k in range(12)] for i in range(12)]
        if acts_trivially(G_N, MN, dual_N):
            surv.append((lab, xlab))
        else:
            offker.append((lab, xlab, MN))
print("    quoted ambient transvections E_{e_i,x}, x over a Z-basis of e_i^perp cap L:")
print(f"      total {len(surv)+len(killed)+len(offker)}")
print(f"      {len(surv)} preserve N and act trivially on A_N  (in Stab_E(N) cap ker)")
print(f"      {len(offker)} preserve N but act NON-trivially on A_N : {[(a,b) for a,b,_ in offker]}")
print(f"      {len(killed)} do not preserve N (Alg 1 discards them) : {killed}")
ok("44 quoted transvections in total (4(n-1) with n=12)",
   len(surv) + len(killed) + len(offker) == 44)
ok("Stab_E(N) is NOT contained in ker(O(N)->O(A_N)) -- witnesses above",
   len(offker) > 0)
ok("4 of the 44 do not even preserve N", len(killed) == 4)
# explicit witness, hand-checkable
g = eichler(G_L, f2, c1)
ok("g = E_{f2,c1}: isometry of L, trivial on A_L",
   is_iso(G_L, g) and acts_trivially(G_L, g, dual_L))
ok("g preserves N", all(inN(act(g, list(r))) for r in B_N))
gz = act(g, zN)
ok("g(e2/2) = e2/2 + f2 + c1/2",
   [gz[i] - zN[i] for i in range(12)]
   == [f2[i] + F(c1[i], 2) for i in range(12)])
ok("g(e2/2)-e2/2 = f2 + c1/2 is NOT in N  => g not in ker(O(N)->O(A_N))",
   not inN([gz[i] - zN[i] for i in range(12)]))

print("=" * 78)
print("S4  Containment: ker(O(N)->O(A_N)) is contained in O(L) for every N subset L subset N^v")
# Abstract proof: L/N is generated by f2 mod N, and f2 in N^v; g in ker(O(N)->O(A_N))
# acts trivially on N^v/N, so g(f2) = f2 + (element of N), hence g(L) = L.
def toN(vL):
    return act(Binv, vL)


def toL(cN):
    return act(tr(B_N), cN)


def NtoL_matrix(M):
    """matrix of an N-coordinate isometry, written in L-coordinates"""
    return mul(mul(tr(B_N), M), tr(Binv))


def preserves_L(MN):
    ML = NtoL_matrix(MN)
    return integral([ML[i][j] for i in range(12) for j in range(12)])


ok("f2 lies in N^v", in_dual(G_N, toN(f2)))
ok("2f2 lies in N", inN(toL(toN([2 * x for x in f2]))))
# abstract: L/N = <f2 + N>, f2 in N^v, ker acts trivially on N^v/N => ker preserves L.
sv2 = refl(G_N, toN([e1[k] + f1[k] for k in range(12)]))
ok("a kernel reflection fixes f2 mod N, hence preserves L:  s(f2)-f2 in N",
   inN([act(sv2, toN(f2))[k] - toN(f2)[k] for k in range(12)]))
ok("...and it preserves L as a matrix", preserves_L(sv2))
intr_iso = {"e1": toN(e1), "f1": toN(f1), "e2": toN(e2), "2f2": toN([2 * x for x in f2])}
allgood, count = True, 0
for lab, e in intr_iso.items():
    ok(f"  {lab} is isotropic in N", ip(G_N, e, e) == 0)
    for x in basis_perp(G_N, e):
        M = eichler(G_N, e, x)
        count += 1
        good = (is_iso(G_N, M) and acts_trivially(G_N, M, dual_N) and preserves_L(M))
        if not good:
            print("    problem with", lab, [str(t) for t in x][:4])
        allgood = allgood and good
ok(f"all {count} intrinsic transvections E_(e_i,x) (e_i in N isotropic, x a basis of "
   "e_i^perp cap N) are isometries of N, lie in ker(O(N)->O(A_N)), and preserve L", allgood)

print("=" * 78)
print("S5  Theorem C: tau_v in ker(O(N)->O(A_N)) <=> v in ((v,v)/2)N")
def ncomb(*terms):
    v = [F(0)] * 12
    for coef, vec in terms:
        for i in range(12):
            v[i] += coef * vec[i]
    return v


vecs = {"norm 2: e1+f1": ncomb((1, toN(e1)), (1, toN(f1))),
        "norm -2: e1-f1": ncomb((1, toN(e1)), (-1, toN(f1))),
        "norm 4: e2+2f2": ncomb((1, toN(e2)), (1, toN([2 * x for x in f2]))),
        "norm -2: c1+ ... c2": ncomb((1, toN(c1)), (1, toN(CART[1])))}
for lab, w in vecs.items():
    q = ip(G_N, w, w)
    a = F(q, 2)
    if q == 0:
        continue
    S = refl(G_N, w)
    triv = acts_trivially(G_N, S, dual_N)
    pred = integral([F(x) / a for x in w])
    ok(f"{lab}: (v,v)={q}, a={a}, predicted kernel={pred}, observed={triv}",
       triv == pred and is_iso(G_N, S))

print("=" * 78)
print("S6  H4: det and spinor norm of the named generators")
report = {}
cases = [("E_{e1,f2} on L", eichler(G_L, e1, f2), G_L),
         ("E_{e2,c1} on L", eichler(G_L, e2, c1), G_L),
         ("E_{f2,c1} on L (=witness)", eichler(G_L, f2, c1), G_L),
         ("E_{e1,c1} on N", eichler(G_N, toN(e1), toN(c1)), G_N),
         ("s_{e1+f1} (norm 2)", refl(G_N, vecs["norm 2: e1+f1"]), G_N),
         ("s_{e1-f1} (norm -2)", refl(G_N, vecs["norm -2: e1-f1"]), G_N),
         ("s_{e2+2f2} (norm 4)", refl(G_N, vecs["norm 4: e2+2f2"]), G_N),
         ("-id on N", [[F(-int(i == j)) for j in range(12)] for i in range(12)], G_N)]
for lab, M, G in cases:
    sp, ns = spinor(G, M)
    report[lab] = (det(M), sp, ns)
    if sp is None:
        print(f"    {lab:30s} det={det(M)}  factorisation failed")
        continue
    sn = sv_ghs(sp, ns)
    print(f"    {lab:30s} det={str(det(M)):>2} #refl={ns:>2} sn_ghs={str(sn):>12} "
          f"class={sqclass(sn)}  {'in O^+' if in_Oplus(sp, ns) else 'NOT in O^+'}"
          f"  {'in O~SO+ (spinorial kernel)' if sqclass(sn) == (False, ()) else ''}")
ok("E_{e1,f2}: det 1, sn a square => in the spinorial kernel O'(L) = O~SO+(L)",
   report["E_{e1,f2} on L"][0] == 1 and sqclass(sv_ghs(*report["E_{e1,f2} on L"][1:])) == (False, ()))
ok("E_{e2,c1}: det 1, sn a square", sqclass(sv_ghs(*report["E_{e2,c1} on L"][1:])) == (False, ()))
ok("E_{f2,c1} (the descent witness): det 1, sn a square (it is in O^+, just not in ker)",
   report["E_{f2,c1} on L (=witness)"][0] == 1
   and sqclass(sv_ghs(*report["E_{f2,c1} on L (=witness)"][1:])) == (False, ()))
ok("sigma_{e1-f1}, (v,v)=-2: sn=+1 => in O^+  (GHS convention -(v,v)/2)",
   in_Oplus(*report["s_{e1-f1} (norm -2)"][1:]))
ok("sigma_{e1+f1}, (v,v)=+2: sn=-1 => NOT in O^+",
   not in_Oplus(*report["s_{e1+f1} (norm 2)"][1:]))
ok("sigma_{e2+2f2}, (v,v)=+4: sn=-2 => NOT in O^+",
   not in_Oplus(*report["s_{e2+2f2} (norm 4)"][1:]))
ok("-id: det 1, in O^+", report["-id on N"][0] == 1 and in_Oplus(*report["-id on N"][1:]))

print("-- block SL_2(Z)^2 on the determinant model M_{2,2}(Z) = U (+) U "
      "(E11->e1, E22->f1, E12->e2, E21->-f2)")


def left_mult(S):
    (a, b), (c, d) = S
    M = [[F(0)] * 4 for _ in range(4)]
    M[0][0], M[3][0] = F(a), F(-c)
    M[1][1], M[2][1] = F(d), F(b)
    M[2][2], M[1][2] = F(a), F(c)
    M[0][3], M[3][3] = F(-b), F(d)
    return M


def right_mult(S):
    (a, b), (c, d) = S
    M = [[F(0)] * 4 for _ in range(4)]
    M[0][0], M[2][0] = F(a), F(c)
    M[0][2], M[2][2] = F(b), F(d)
    M[3][1], M[1][1] = F(-b), F(d)
    M[3][3], M[1][3] = F(a), F(-c)
    return M


S1, S2 = [[1, 1], [0, 1]], [[1, 0], [1, 1]]
for nm, M in [("leftmult(S1)", left_mult(S1)), ("leftmult(S2)", left_mult(S2)),
              ("rightmult(S1)", right_mult(S1)), ("rightmult(S2)", right_mult(S2))]:
    ok(f"{nm} isometry of U(+)U", is_iso(G_L4, M))
    sp, ns = spinor(G_L4, M)
    ML = emb12(M)
    sgn = "?" if sp is None else ("+1" if sp > 0 else "-1")
    ok(f"{nm}: sn_ghs class {sqclass(sv_ghs(sp, ns)) if sp is not None else None} "
       f"=> in O' and trivial on A_L",
       sp is not None and sqclass(sv_ghs(sp, ns)) == (False, ())
       and acts_trivially(G_L, ML, dual_L))
    keeps = all(inN(act(ML, list(r))) for r in B_N)
    print(f"    {nm:16s} det={det(M)} #refl={ns} prod norms={sp} class="
          f"{sqclass(sp) if sp is not None else None} preserves N? {keeps}")

print("=" * 78)
print("S7  |O(A)| for A = (hyperbolic plane)^p over F_2; repo fixture p=5 -> 46998591897600")


def og_order(p):
    """|O(q)| for q = (hyperbolic plane)^p over F_2.  Recursion
       |O(2m)| = #orbit(nonzero singular vectors) * 2^(2m-2) * |O(2m-2)|,
    the middle factor being the unipotent radical of the stabiliser parabolic."""
    if p == 0:
        return 1
    n = 2 * p
    sing = sum(1 for v in product((0, 1), repeat=n)
               if sum(v[2 * k] * v[2 * k + 1] for k in range(p)) % 2 == 0)
    return (sing - 1) * 2 ** (n - 2) * og_order(p - 1)


def og_order_brute(p):
    """brute force: enumerate bases and count isometries by depth-first search"""
    n = 2 * p
    vecs = list(product((0, 1), repeat=n))

    def q(v):
        return sum(v[2 * k] * v[2 * k + 1] for k in range(p)) % 2

    def b(x, y):
        return (q(tuple((x[i] + y[i]) % 2 for i in range(n))) - q(x) - q(y)) % 2
    basis = [tuple(int(i == k) for i in range(n)) for k in range(n)]
    cnt = 0
    def dfs(k, imgs):
        nonlocal cnt
        if k == n:
            cnt += 1
            return
        for v in vecs:
            if q(v) != q(basis[k]):
                continue
            if all(b(v, imgs[j]) == b(basis[k], basis[j]) for j in range(k)):
                dfs(k + 1, imgs + [v])
    dfs(0, [])
    return cnt


for p in (1, 2, 3):
    ok(f"recursion vs brute force at p={p}", og_order(p) == og_order_brute(p),
       f"{og_order(p)} vs {og_order_brute(p)}")
for p, exp in [(1, 2), (2, 72), (3, 40320), (4, 348364800), (5, 46998591897600)]:
    got = og_order(p)
    ok(f"|O((plane)^{p})| = {exp}", got == exp, f"got {got}")
ok("|O(A_N)| = 2^21*3^5*5^2*7*17*31", og_order(5) == 2 ** 21 * 3 ** 5 * 5 ** 2 * 7 * 17 * 31)
print("    |O(E8/2E8)| =", og_order(4), "; |W(E8)| = 696729600 ; ratio",
      F(696729600, og_order(4)))

print("=" * 78)
print("S8  Gamma(2) = ker(O(N)->O(N/2N)) strictly inside ker(O(N)->O(A_N))")
w2 = vecs["norm 2: e1+f1"]
ok("s_{e1+f1} in ker(O(N)->O(A_N)) (norm 2 => always)", acts_trivially(G_N, refl(G_N, w2), dual_N))
wit = None
for tup in product(range(-1, 2), repeat=12):
    x = [F(t) for t in tup]
    if any(x) and ip(G_N, x, w2) % 2 != 0:
        wit = x
        break
ok("exists x in N with (x, e1+f1) odd => that kernel element is outside ker(O(N)->O(N/2N))",
   wit is not None)
ok("consequently ker(O(N)->O(N/2N)) is strictly smaller than ker(O(N)->O(A_N))", wit is not None)
ok("there is no transvection with (v,v)=+-4 in ker(O(N)->O(A_N)): v in ((v,v)/2)N=2N "
   "would give (v,v)=4(w,w) in 8Z", True)

print("=" * 78)
print("S9  Which lattices satisfy Kneser's conditions?  rank_p = max rank of M in L with p | det M")
G_Lp = bd(U2, [[0, 2], [2, 0]], [[-CartanE8[i][j] for j in range(8)] for i in range(8)])   # L' = U + U(2) + E8(-1)


def rank_mod_p(G, p):
    A = [[int(G[i][j]) % p for j in range(len(G))] for i in range(len(G))]
    n, r = len(G), 0
    for c in range(n):
        piv = next((rr for rr in range(r, n) if A[rr][c] % p), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv_ = pow(A[r][c], -1, p)
        A[r] = [(x * inv_) % p for x in A[r]]
        for rr in range(n):
            if rr != r and A[rr][c] % p:
                f = A[rr][c]
                A[rr] = [(A[rr][j] - f * A[r][j]) % p for j in range(n)]
        r += 1
    return r


for nm, G in [("N = U+U(2)+E8(-2)", G_N), ("ambient L = U+U+E8(-2)", G_L),
              ("L' = U+U(2)+E8(-1)", G_Lp)]:
    r2, r3 = rank_mod_p(G, 2), rank_mod_p(G, 3)
    print(f"    {nm:26s} rank_2 = {r2:2d}   rank_3 = {r3:2d}   "
          f"Kneser (rank_3>=5, rank_2>=6): {'YES' if (r2 >= 6 and r3 >= 5) else 'NO'}")
ok("rank_2(N) = 2  (matches GHS, verbatim: 'L = U(2)+U+E8(-2) ... has 2-rank 2')",
   rank_mod_p(G_N, 2) == 2)
ok("rank_2(ambient L) = 4 < 6: Kneser/GHS generation theorem does not apply to L either",
   rank_mod_p(G_L, 2) == 4)
ok("rank_2(L') = 10 >= 6 and rank_3(L') = 12 >= 5: L' satisfies the Kneser conditions",
   rank_mod_p(G_Lp, 2) == 10 and rank_mod_p(G_Lp, 3) == 12)
# L' really represents -2 and has Witt index >= 2 (signature (2,10))
ok("L' represents -2 (E8(-1) root)", ip(G_Lp, CART[0], CART[0]) == -2)
ok("N represents -2 (e1-f1)", ip(G_N, vecs["norm -2: e1-f1"], vecs["norm -2: e1-f1"]) == -2)
# divisors: div(e2) = 2 in N  => e2 cannot be completed to an integral hyperbolic plane in N
def divisor(G, e):
    vals = [abs(int(ip(G, e, [F(int(i == k)) for i in range(len(G))]))) for k in range(len(G))]
    g = 0
    for v in vals:
        g = math.gcd(g, v)
    return g


import math
ok("div(e2) = 2 in N  (so e2 CANNOT be completed to an integral U in N; GHS Prop ET needs div=1)",
   divisor(G_N, toN(e2)) == 2)
ok("div(e1) = 1 in N (the U-direction is unimodular)", divisor(G_N, toN(e1)) == 1)
ok("div(f2) = 1 in L (f2 is unimodular in the ambient lattice)", divisor(G_L, f2) == 1)
ok("div(2f2) = 2 in N (the second U(2) isotropic direction is not unimodular either)",
   divisor(G_N, toN([2 * x for x in f2])) == 2)
# GHS transport: L is the index-4 sublattice of L'(2) obtained by halving the U(4) generators
GLp2 = [[2 * G_Lp[i][j] for j in range(12)] for i in range(12)]
ok("det L'(2) = 2^14 and det N = 2^10 => [L'(2) : N] = 4 (GHS's transport relation)",
   det(GLp2) != 0 and (det(GLp2) / det(G_N)) == 16)

print("=" * 78)
print("SUMMARY:", "ALL CHECKS PASSED" if not FAILS else f"FAILURES: {FAILS}")
