#!/usr/bin/env python3
"""The ambient Eichler/Scattone generators on M = U+U+E8(-2) tested against
the index-2 sublattice N = U+U(2)+E8(-2) (Enriques coinvariant with a free U).

Generators, exactly as named in Enriques_compu_rev.tex:1437-1451:
  (i) the four block maps X -> A X B, A,B in {S,T} in SL_2(Z), acting on
      U+U identified with (M_{2,2}(Z), det)   [Example 3.7.2]
  (ii) the Eichler transvections E_{e,x} for e one of the 4 canonical
      isotropic vectors e1,f1,e2,f2 of the two hyperbolic planes and x in a
      Z-basis of e^perp cap M  [the 4(n-1) = 44 transvections, n = 12].
All computations are exact integer/rational matrix algebra on 12x12 matrices.
"""
from fractions import Fraction as F
from itertools import product
import sys

def inv(G):
    n=len(G); A=[[F(G[i][j]) for j in range(n)]+[F(1 if i==j else 0) for j in range(n)] for i in range(n)]
    for c in range(n):
        p=next(r for r in range(c,n) if A[r][c]!=0); A[c],A[p]=A[p],A[c]
        pv=A[c][c]; A[c]=[x/pv for x in A[c]]
        for r in range(n):
            if r!=c and A[r][c]!=0:
                f=A[r][c]; A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return [row[n:] for row in A]

def mul(A,B):
    n=len(A); m=len(B[0]); k=len(B)
    return [[sum(F(A[i][t])*F(B[t][j]) for t in range(k)) for j in range(m)] for i in range(n)]
def T(A): return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
def mv(A,v): return [sum(F(A[i][j])*F(v[j]) for j in range(len(v))) for i in range(len(A))]
def isint(x): return F(x).denominator==1
def ident(n): return [[F(1 if i==j else 0) for j in range(n)] for i in range(n)]

def bdiag(*Ms):
    n=sum(len(M) for M in Ms); G=[[F(0)]*n for _ in range(n)]; o=0
    for M in Ms:
        for i in range(len(M)):
            for j in range(len(M)): G[o+i][o+j]=F(M[i][j])
        o+=len(M)
    return G
def U():  return [[0,1],[1,0]]
def U2(): return [[0,2],[2,0]]
def E8():
    n=8; G=[[0]*n for _ in range(n)]
    for i in range(7): G[i][i]=2
    for i in range(6): G[i][i+1]=G[i+1][i]=-1
    G[7][7]=2; G[2][7]=G[7][2]=-1
    return G
def sc(k,M): return [[k*M[i][j] for j in range(len(M))] for i in range(len(M))]

GM=bdiag(U(),U(),sc(-2,E8()))          # M = U + U + E8(-2), basis e1,f1,e2,f2,E8*8
n=len(GM)
GMi=inv(GM)

def gram(v,w): return sum(F(v[i])*F(GM[i][j])*F(w[j]) for i in range(n) for j in range(n))
def q(v): return gram(v,v)/2

def is_iso(g):
    return mul(mul(T(g),GM),g)==[[F(x) for x in row] for row in GM]

def acts_trivially_on_disc(g,G,Gi,sub=None):
    """sub: matrix whose columns are a Z-basis of the lattice L in ambient coords."""
    k=len(G)
    Sinv=inv(sub) if sub is not None else None
    for j in range(k):
        x=[Gi[i][j] for i in range(k)]           # dual generator, L-coordinates
        if sub is not None:
            xa=mv(sub,x)                          # to ambient coordinates
            na=mv(g,xa)
            d=mv(Sinv,[na[i]-xa[i] for i in range(k)])
            if any(not isint(a) for a in d): return False
        else:
            nx=mv(g,x)
            if any(not isint(a-b) for a,b in zip(nx,x)): return False
    return True

# ---------- sublattices N ----------
def N_basis(kind):
    """columns: basis of the index-2 sublattice U + U(2) + E8(-2) inside M."""
    B=[[F(0)]*n for _ in range(n)]
    B[0][0]=F(1); B[1][1]=F(1)                 # e1, f1
    if kind=='e2_2f2':
        B[2][2]=F(1); B[3][3]=F(2)
    elif kind=='2e2_f2':
        B[2][3]=F(1); B[3][2]=F(2)
    for i in range(4,n): B[i][i]=F(1)
    return B

def preserves(g,B):
    """g(B) subset B, and returns the matrix of g on B."""
    gB=mul(g,B)
    X=mul(inv(B),gB)
    if all(isint(x) for row in X for x in row):
        if abs(round(matdet(X)))==1:
            return True,X
    return False,None

def matdet(M):
    A=[[F(x) for x in row] for row in M]; nn=len(A); d=F(1)
    for c in range(nn):
        p=next((r for r in range(c,nn) if A[r][c]!=0),None)
        if p is None: return F(0)
        if p!=c: A[c],A[p]=A[p],A[c]; d=-d
        d*=A[c][c]; pv=A[c][c]
        for r in range(c+1,nn):
            f=A[r][c]/pv
            if f: A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return d

# ---------- (i) the four block maps X -> A X B on M_{2,2}(Z) ----------
S=[[0,-1],[1,0]]; Tt=[[1,1],[0,1]]
# psi: abstract (e1,f1,e2,f2) coordinates -> (E11,E12,E21,E22) coordinates
psi=[[F(0)]*4 for _ in range(4)]
# e1 -> E11, f1 -> E22, e2 -> E12, f2 -> -E21
psi[0][0]=F(1)   # E11 <- e1
psi[3][1]=F(1)   # E22 <- f1
psi[1][2]=F(1)   # E12 <- e2
psi[2][3]=F(-1)  # -E21 <- f2
psii=inv(psi)

def matbasis(i,j):        # E_ij in M_{2,2}
    M=[[0,0],[0,0]]; M[i][j]=1; return M

def blockmap(A,B):
    """matrix of X -> A X B on (E11,E12,E21,E22) coordinates."""
    cols=[]
    for (i,j) in [(0,0),(0,1),(1,0),(1,1)]:
        X=matbasis(i,j)
        Y=mul(mul(A,X),B)     # 2x2 with integer entries
        cols.append([F(Y[0][0]),F(Y[0][1]),F(Y[1][0]),F(Y[1][1])])
    M4=[[cols[j][i] for j in range(4)] for i in range(4)]
    G4=mul(mul(psii,M4),psi)          # action in abstract coordinates
    G=ident(n)
    for i in range(4):
        for j in range(4): G[i][j]=G4[i][j]
    return G

# ---------- (ii) Eichler transvections ----------
def transvection(e,x,variant):
    """Return the 12x12 matrix of the map on M (as a function of v)."""
    cols=[]
    for j in range(n):
        v=[F(1 if i==j else 0) for i in range(n)]
        ve=gram(v,e); vx=gram(v,x); qx=q(x)
        if variant==1:
            w=[v[i]+ve*x[i]-(vx+ve*qx)*e[i] for i in range(n)]
        elif variant==2:
            w=[v[i]+ve*x[i]-vx*e[i] for i in range(n)]
        else:
            w=[v[i]+ve*x[i]-vx*e[i]-qx*ve*e[i] for i in range(n)]
        cols.append(w)
    return [[cols[j][i] for j in range(n)] for i in range(n)]

def vec(idx):
    v=[F(0)]*n; v[idx]=F(1); return v

def basis_e_perp(idx):
    """a Z-basis of e^perp cap M for e = vec(idx), idx in {0,1,2,3}."""
    partner={0:1,1:0,2:3,3:2}[idx]
    return [vec(i) for i in range(n) if i!=partner]

def main():
    L=print
    L('M = U+U+E8(-2), rank %d, det %s' % (n,matdet(GM)))
    L('')
    L('=== A. choices of the Eichler transvection formula (e = e1, x = e2, so (x,e)=0) ===')
    e=vec(0); x=vec(2)
    L('    q(x) = %s ; (x,e) = %s' % (q(x), gram(x,e)))
    for var in (1,2,3):
        g=transvection(e,x,var)
        L('    variant %d : isometry %s ; fixes e %s ; acts trivially on A_M %s'
          % (var,is_iso(g), mv(g,e)==e, acts_trivially_on_disc(g,GM,GMi)))
    L('')
    for kind in ('e2_2f2','2e2_f2'):
        B=N_basis(kind); GN=mul(mul(T(B),GM),B); GNi=inv(GN)
        L('=== B. sublattice choice %s : det = %s (index 2), Gram = %s' % (kind,matdet(GN),'ok' if matdet(GN)==-4*(256) else '?'))
        rows=[]
        gens=[]
        for A,Bb in [(S,ident(2)),(Tt,ident(2)),(ident(2),S),(ident(2),Tt)]:
            A=[[int(v) for v in row] for row in A]; Bb=[[int(v) for v in row] for row in Bb]
            gens.append(('block(A=%s,B=%s)'%(A,Bb),blockmap(A,Bb)))
        names=['e1','f1','e2','f2']
        cnt=0
        for idx in range(4):
            for j,xv in enumerate(basis_e_perp(idx)):
                g=transvection(vec(idx),xv,1)
                if not is_iso(g):
                    L('    !! transvection e=%s x=%d is not an isometry' % (names[idx],j))
                gens.append(('T(e=%s,x=%d)'%(names[idx],j),g)); cnt+=1
        L('    total named generators: %d (= 4 block + 4*(n-1) = 4 + %d)' % (len(gens),4*(n-1)))
        keep=0; keep_trivial=0
        for nm,g in gens:
            ok,X=preserves(g,B)
            if ok:
                keep+=1
                tri=acts_trivially_on_disc(g,GN,GNi,sub=B)
                keep_trivial+= 1 if tri else 0
                rows.append((nm,ok,tri))
            else:
                rows.append((nm,ok,None))
        for nm,ok,tri in rows:
            L('      %-22s preserves N: %-5s acts trivially on A_N: %s' % (nm,ok,tri))
        L('    --> %d of %d named generators preserve N; of those, %d act trivially on A_N'
          % (keep,len(gens),keep_trivial))
        L('')
if __name__ == '__main__':
    main()
