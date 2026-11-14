#!/usr/bin/env python3
"""m7: the containment gap, repaired.  Model Lambda = M = U + U + <-4> + <-4>  (rank 6),
N = U + U(2) + <-4> + <-4> with U(2) = <2e2, f2>.  The quoted generator
E_{e2, e2+l1}  (e2 one of the four canonical isotropic vectors, x = e2+l1 in e2^perp cap M)
is an isometry of M and of N, acts TRIVIALLY on A_M = A_L, and acts NON-trivially on
A_N:  it moves [f2/2] to [f2/2] + [e2] + [l1/2].  Hence the descended group is NOT
contained in ker(O(N)->O(A_N)).   Run: python3 witness_H2.py
"""
from fractions import Fraction as F
import math, itertools
def mat(r): return [[F(x) for x in row] for row in r]
def T(A): return [list(x) for x in zip(*A)]
def mm(A,B):
    n,m,k=len(A),len(B[0]),len(B)
    return [[sum(A[i][t]*B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]
def mv(A,v): return [sum(A[i][j]*v[j] for j in range(len(v))) for i in range(len(A))]
def eye(n): return [[F(int(i==j)) for j in range(n)] for i in range(n)]
def inv(A):
    n=len(A); M=[A[i][:]+[F(int(i==j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p=next(r for r in range(c,n) if M[r][c]!=0)
        M[c],M[p]=M[p],M[c]; pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for r in range(n):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[a-f*b for a,b in zip(M[r],M[c])]
    return [row[n:] for row in M]
def det(A):
    A=[r[:] for r in A]; n=len(A); d=F(1); s=1
    for i in range(n):
        if A[i][i]==0:
            p=next((r for r in range(i+1,n) if A[r][i]!=0),None)
            if p is None: return F(0)
            A[i],A[p]=A[p],A[i]; s=-s
        d*=A[i][i]
        for r in range(i+1,n):
            f=A[r][i]/A[i][i]; A[r]=[a-f*b for a,b in zip(A[r],A[i])]
    return s*d
def show(v): return "("+",".join(str(x) for x in v)+")"
G=mat([[0,1,0,0,0,0],[1,0,0,0,0,0],[0,0,0,1,0,0],[0,0,1,0,0,0],[0,0,0,0,-4,0],[0,0,0,0,0,-4]])
b=lambda i: [F(int(k==i)) for k in range(6)]
e1,f1,e2,f2,l1,l2 = b(0),b(1),b(2),b(3),b(4),b(5)
twoe2=[F(0),F(0),F(2),F(0),F(0),F(0)]
def ip(x,y): return sum(x[i]*G[i][j]*y[j] for i in range(6) for j in range(6))
Mgens=[e1,f1,e2,f2,l1,l2]; Ngens=[e1,f1,twoe2,f2,l1,l2]
def in_N(v):
    # N = <e1,f1,2e2,f2,l1,l2> : coordinates a e1 + b f1 + c e2 + d f2 + x l1 + y l2 with c even
    return v[2].denominator==1 and v[2]%2==0 and all(v[i].denominator==1 for i in range(6))
def integral_on(gens,v):
    return all(sum(ip(v,g)*0 for _ in [0])==0 for g in gens) and all(ip(v,g).denominator==1 for g in gens)
def E(e,x):
    def col(j):
        v=[F(int(i==j)) for i in range(6)]
        ve=ip(v,e); vx=ip(v,x); xx=ip(x,x)
        return [v[i]+ve*x[i]-vx*e[i]-xx*ve/2*e[i] for i in range(6)]
    return T([col(j) for j in range(6)])
def isom(A): return mm(mm(T(A),G),A)==G
def in_M(v): return all(c.denominator==1 for c in v)
print("e = e2 =",show(e2)," isotropic:",ip(e2,e2)==0)
x=[e2[i]+l1[i] for i in range(6)]
print("x = e2 + l1 =",show(x)," x perp e:",ip(x,e2)==0," (x,x) =",ip(x,x))
A=E(e2,x)
print("E is an isometry of the Q-space:",isom(A))
print("E(M) subset M            :",all(in_M(mv(A,g)) for g in Mgens))
print("E(N) subset N            :",all(in_N(mv(A,g)) for g in Ngens))
print("  images of the N-generators:",[show(mv(A,g)) for g in Ngens])
print("E(x') - x' in M for x' in the dual basis of M (trivial on A_M):")
# M^v = M + L^v ; test l1/4, l2/4 (generators of A_L) and the M-generators
for y in Mgens+[[F(0),F(0),F(0),F(0),F(1,4),F(0)],[F(0),F(0),F(0),F(0),F(0),F(1,4)],
                [F(0),F(0),F(1,2),F(0),F(0),F(0)]]:
    d=[mv(A,y)[i]-y[i] for i in range(6)]
    print("   y=%-28s displacement=%-24s in M: %s  (in N: %s)"%(show(y),show(d),in_M(d),in_N(d)))
y=[F(0),F(0),F(0),F(1,2),F(0),F(0)]     # f2/2 in N^v
d=[mv(A,y)[i]-y[i] for i in range(6)]
print("WITNESS: E(f2/2) - f2/2 =",show(d),"   in N?",in_N(d),"  -> NON-trivial on A_N")
print("         = e2 + l1/2 (mod N), and e2 not in N")
print("Quadratic check: q(E(f2/2)) = (.,.) mod 2 =",ip(mv(A,y),mv(A,y))%2," q(f2/2) =",ip(y,y)%2)
