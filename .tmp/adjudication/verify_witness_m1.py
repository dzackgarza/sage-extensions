# Judge-side independent reproduction of m1's witness t(a1-style "a2", r0).
# M = <a1,b1,a2,b2> + E8(-2); N = <a1,b1,2a2,b2> + E8(-2).
# t(e,x)(y) = y + (y,e)x - ((y,x) + q(x)(y,e))e, with q(x) = (x,x)/2.
from fractions import Fraction as F

C8 = [
 [2,-1,0,0,0,0,0,0],
 [-1,2,-1,0,0,0,0,0],
 [0,-1,2,-1,0,0,0,-1],
 [0,0,-1,2,-1,0,0,0],
 [0,0,0,-1,2,-1,0,0],
 [0,0,0,0,-1,2,-1,0],
 [0,0,0,0,0,-1,2,0],
 [0,0,-1,0,0,0,0,2],
]
Gblocks = [[[0,1],[1,0]], [[0,1],[1,0]], [[-2*c for c in row] for row in C8]]
# coordinates on M: (a1,b1,a2,b2, r1..r8)
n = 12
G = [[F(0)]*n for _ in range(n)]
off = 0
for B in Gblocks:
    for i in range(len(B)):
        for j in range(len(B)):
            G[off+i][off+j] = F(B[i][j])
    off += len(B)

def dot(x, y): return sum(x[i]*G[i][j]*y[j] for i in range(n) for j in range(n))
def q(x): return dot(x,x)/F(2)

def e_i(k):  # 0..11
    return [F(1 if i==k else 0) for i in range(n)]

def t(e, x, y):
    qx = q(x)
    return [y[i] + dot(y,e)*x[i] - (dot(y,x) + qx*dot(y,e))*e[i] for i in range(n)]

m_basis = [e_i(k) for k in range(n)]
n_basis = [e_i(0), e_i(1), [F(2) if k==2 else F(0) for k in range(n)], e_i(3)] + [e_i(k) for k in range(4,12)]

def in_N(v):
    # v in Z-span of n_basis
    import sympy as sp
    B = sp.Matrix.hstack(*[sp.Matrix(n,1,b) for b in n_basis])
    sol = B.solve(sp.Matrix(n,1,v))
    return all(x.is_integer for x in sol)

a2 = e_i(2)
r0 = e_i(4)  # first E8 Cartan basis vector, (r0,r0) = -4
checks = []
checks.append(("e isotropic", dot(a2,a2) == 0))
checks.append(("(e,r0) = 0", dot(a2,r0) == 0))
checks.append(("(r0,r0) = -4", dot(r0,r0) == -4))

# isometry: preserve (t(v), t(w)) = (v,w) on all basis pairs
ok = True
for i in range(n):
    for j in range(n):
        ti = t(a2, r0, m_basis[i]); tj = t(a2, r0, m_basis[j])
        if dot(ti,tj) != dot(m_basis[i],m_basis[j]): ok = False
checks.append(("isometry on M", ok))

# preserves N
checks.append(("t(N) subset N: a1", in_N(t(a2,r0,n_basis[0]))))
checks.append(("t(N) subset N: b1", in_N(t(a2,r0,n_basis[1]))))
checks.append(("t(N) subset N: 2a2", in_N(t(a2,r0,n_basis[2]))))
checks.append(("t(N) subset N: b2", in_N(t(a2,r0,n_basis[3]))))
all_e8 = all(in_N(t(a2,r0,n_basis[k])) for k in range(4,12))
checks.append(("t(N) subset N: E8 block", all_e8))
# inverse t(a2,-r0) also preserves
inv_ok = all(in_N(t(a2,[-x for x in r0],n_basis[k])) for k in range(12))
checks.append(("t(a2,-r0) preserves N", inv_ok))

# trivial on D(M): for all w in M^v = span(...): M unimodular on planes, E8(-2) dual = (1/2)(-2C8^-1)
# M^v basis: a1,b1,a2,b2 plus r_i/2 (since (r_i/2, r_j) = -C8[i][j] in Z)
mv_basis = [e_i(k) for k in range(4)] + [[F(1,2) if k==j else F(0) for k in range(n)] for j in range(4,12)]
def in_M(v):
    # v has integer coordinates in the standard M basis
    return all(x.denominator == 1 for x in v)

triv = True
for w in mv_basis:
    diff = [t(a2,r0,w)[i]-w[i] for i in range(n)]
    if not in_M(diff):  # the discriminant-triviality claim on M: difference must lie in M itself
        triv = False
checks.append(("t trivial on D(M): displacement in M", triv))

# moves D(N): w = b2/2 in N^v, difference not in N
w = [F(1,2) if k==3 else F(0) for k in range(n)]
in_nv = all((dot(w, nb) in range(-10,10)) and (dot(w,nb).denominator == 1) for nb in n_basis)
diff = [t(a2,r0,w)[i]-w[i] for i in range(n)]
checks.append(("b2/2 in N^v", in_nv))
checks.append(("t(b2/2)-b2/2 = a2 + r0/2 as a vector"
               , diff == [F(0),F(0),F(1),F(0),F(1,2)]+[F(0)]*7))
checks.append(("difference has odd a2 coefficient -> not in N", not in_N(diff)))

for name, v in checks:
    print(f"{'OK ' if v else 'FAIL'} {name}")
print("ALL", "OK" if all(v for _,v in checks) else "FAIL")
