#!/usr/bin/env python3
"""Exact discriminant-form arithmetic for N = U + U(2) + E8(-2).

Conventions: (,) is the bilinear form with (v,v) = 2*q(v); the discriminant
form is q_L(x) = (x,x) mod 2Z on A_L = L^v/L, realised as coker(G) (so
A_L = {G^{-1} m mod Z^k}), with b(x,y) = (x,y) mod Z.
Nothing here enumerates lattice isometries: only finite forms over Z/2 are
touched, and their isometry groups are counted by type + a validated formula.
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

def det(G):
    n=len(G); A=[[F(G[i][j]) for j in range(n)] for i in range(n)]; d=F(1)
    for c in range(n):
        p=next((r for r in range(c,n) if A[r][c]!=0),None)
        if p is None: return F(0)
        if p!=c: A[c],A[p]=A[p],A[c]; d=-d
        d*=A[c][c]; pv=A[c][c]
        for r in range(c+1,n):
            f=A[r][c]/pv
            if f: A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return d

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
    # Cartan matrix of E8: chain of 7 nodes 0..6, node 7 attached to node 2 (det = 1)
    n=8; G=[[0]*n for _ in range(n)]
    for i in range(7): G[i][i]=2
    for i in range(6): G[i][i+1]=G[i+1][i]=-1
    G[7][7]=2; G[2][7]=G[7][2]=-1
    return G
def sc(k,M): return [[k*M[i][j] for j in range(len(M))] for i in range(len(M))]

def fl(x): return x-(x.numerator//x.denominator)

def disc(G):
    n=len(G); Gi=inv(G)
    cols=[[Gi[j][i] for j in range(n)] for i in range(n)]
    zero=tuple(F(0) for _ in range(n)); els={zero:0}; order=[zero]; fr=[zero]
    while fr:
        new=[]
        for x in fr:
            for c in cols:
                y=tuple(fl(a+b) for a,b in zip(x,c))
                if y not in els: els[y]=len(order); order.append(y); new.append(y)
        fr=new
    def q(x):
        s=sum(F(x[i])*F(G[i][j])*F(x[j]) for i in range(n) for j in range(n))
        return F(int(s)%2) if s.denominator==1 else fl(s)
    def b(x,y):
        s=sum(F(x[i])*F(G[i][j])*F(y[j]) for i in range(n) for j in range(n))
        return fl(s)
    return dict(order=order,els=els,q=q,b=b,size=len(order),det=det(G))

def qdist(D):
    d={}
    for x in D['order']:
        v=D['q'](x); d[v]=d.get(v,0)+1
    return dict(sorted(d.items(), key=lambda kv: (kv[0])))

def add(D,x,y): return tuple(fl(a+b) for a,b in zip(x,y))
def subgroup(D,gens):
    zero=tuple(F(0) for _ in range(len(D['order'][0]))); S={zero}; fr=[zero]
    while fr:
        new=[]
        for x in fr:
            for g in gens:
                y=add(D,x,g)
                if y not in S: S.add(y); new.append(y)
        fr=new
    return S
def perp(D,S): return {x for x in D['order'] if all(D['b'](x,s)==0 for s in S)}
def restrict(D,S): return dict(order=list(S),q=D['q'],b=D['b'],size=len(S),det=D['det'])

def ortho_order(m,eps):
    """|O^eps_{2m}(2)| ; eps=+1 split, -1 non-split.  Validated against brute force below."""
    r=2**(m*(m-1)+1)*(2**m-eps)
    for i in range(1,m): r*=(2**(2*i)-1)
    return r

def zero_count_order(D):
    """For a 2-elementary module with q integral everywhere and b nondegenerate."""
    dim=1
    while 2**dim<D['size']: dim+=1
    assert 2**dim==D['size']
    assert dim%2==0
    Z=sum(1 for x in D['order'] if D['q'](x)==0)
    m=dim//2
    plus=2**(dim-1)+2**(m-1); minus=2**(dim-1)-2**(m-1)
    eps=1 if Z==plus else (-1 if Z==minus else None)
    assert eps is not None, (Z,dim)
    return dim,eps,Z,ortho_order(m,eps)

def qsmap(D):
    """Coordinates over F_2 + q-values, for the 2-elementary case."""
    order=D['order']; k=0
    while 2**k<len(order): k+=1
    zero=tuple(F(0) for _ in range(len(order[0])))
    basis=[]; cur={zero}
    for x in order:
        if x in cur: continue
        basis.append(x)
        cur=cur|{add(D,y,x) for y in cur}
        if 2**len(basis)==len(order): break
    coord={zero:tuple(0 for _ in range(k))}
    for i,bv in enumerate(basis):
        vec=tuple(1 if j==i else 0 for j in range(k))
        new={}
        for y,c in coord.items():
            new[add(D,y,bv)]=tuple((c[j]+vec[j])%2 for j in range(k))
        coord.update(new)
    assert len(coord)==len(order)
    return {coord[x]:D['q'](x) for x in order}

def brute_order(qs,k):
    vecs=list(product([0,1],repeat=k)); cnt=0
    def rec(i,map_,chosen):
        nonlocal cnt
        if i==k: cnt+=1; return
        e=tuple(1 if j==i else 0 for j in range(k))
        for w in vecs:
            if qs[w]!=qs[e]: continue
            ok=True; newmap=dict(map_)
            for v,iv in map_.items():
                nv=tuple((v[j]+e[j])%2 for j in range(k)); nw=tuple((iv[j]+w[j])%2 for j in range(k))
                if qs[nv]!=qs[nw]: ok=False; break
                if nv in map_ and map_[nv]!=nw: ok=False; break
            if not ok: continue
            for v,iv in map_.items():
                nv=tuple((v[j]+e[j])%2 for j in range(k)); nw=tuple((iv[j]+w[j])%2 for j in range(k))
                newmap[nv]=nw
            newmap[e]=w
            rec(i+1,newmap,chosen+[w])
    zero=tuple(0 for _ in range(k))
    rec(0,{zero:zero},[])
    return cnt

def standard(dim,eps):
    m=dim//2
    def q(v):
        s=0
        for i in range(m-1): s+=v[2*i]*v[2*i+1]
        if m>=1:
            a,b=v[dim-2],v[dim-1]
            if eps==1: s+=a*b
            else: s+=a*a+a*b+b*b
        return F(s%2)
    els=list(product([0,1],repeat=dim))
    return dict(order=els,q=q,size=2**dim,det=None,
                b=lambda x,y: F((q(tuple((x[i]+y[i])%2 for i in range(dim)))-q(x)-q(y))%2))

def factor(n):
    d={}; p=2
    while p*p<=n:
        while n%p==0: d[p]=d.get(p,0)+1; n//=p
        p+=1
    if n>1: d[n]=d.get(n,0)+1
    return ' * '.join('%d^%d'%(p,e) if e>1 else '%d'%p for p,e in sorted(d.items()))

def weyl_orbits():
    G=E8(); n=8
    vecs=list(product([0,1],repeat=n))
    def n2(v): return sum(G[i][j]*v[i]*v[j] for i in range(n) for j in range(n))
    roots=[v for v in product([-1,0,1],repeat=n) if n2(v)==2]
    def refl(r,x):
        c=sum(G[i][j]*x[i]*r[j] for i in range(n) for j in range(n))
        return tuple((x[i]-c*r[i])%2 for i in range(n))
    rem=set(vecs); out=[]
    while rem:
        v=next(iter(rem)); orb={v}; fr=[v]
        while fr:
            new=[]
            for x in fr:
                for r in roots:
                    y=refl(r,x)
                    if y not in orb: orb.add(y); new.append(y)
            fr=new
        out.append(len(orb)); rem-=orb
    return len(roots), sorted(out)

def lagrangian(D):
    order=D['order']; zero=tuple(F(0) for _ in range(len(order[0]))); target=int(round(D['size']**0.5))
    cands=[x for x in order if x!=zero and D['q'](x)==0]
    def rec(S):
        if len(S)==target:
            return S if perp(D,S)==S else None
        for x in cands:
            if x in S or any(D['b'](x,y)!=0 for y in S): continue
            T=subgroup(D,list(S)+[x])
            if len(T)!=2*len(S): continue
            r=rec(T)
            if r: return r
        return None
    return rec(subgroup(D,[zero]))

def main():
    L=print
    L('=== 1. lattices: det and discriminant form ===')
    for name,G in [('U',U()),('U(2)',U2()),('E8 (Cartan)',E8()),
                   ('E8(-2) = -2*E8',sc(-2,E8())),('E8(-1) = -E8',sc(-1,E8())),
                   ('N = U+U(2)+E8(-2)',bdiag(U(),U2(),sc(-2,E8()))),
                   ('M = U+U+E8(-2)',bdiag(U(),U(),sc(-2,E8()))),
                   ('U+U+E8(-1)',bdiag(U(),U(),sc(-1,E8()))),
                   ('U(2)+E8(-2) (rank 6)',bdiag(U2(),sc(-2,E8()))),
                   ('U(2)^5',bdiag(*[U2() for _ in range(5)]))]:
        D=disc(G)
        L('%-24s rank %2d  det %6s  |A| %5d   q-dist %s' % (name,len(G),det(G),D['size'],qdist(D)))
    L('')
    L('=== 2. A_N is the split quadratic space of dimension 10 ===')
    DN=disc(bdiag(U(),U2(),sc(-2,E8())))
    dim,eps,Z,ordN=zero_count_order(DN)
    L('A_N: |A| = %d = 2^%d ; number of x with q(x)=0 : %d' % (DN['size'],dim,Z))
    L('     (split type in dim 10 would have 2^9+2^4 = %d zeros)' % (2**9+2**4))
    L('     => A_N is isometric to the split (plus) quadratic space of dim 10 over F_2')
    L('|O(A_N)| = |O^+_10(2)| = %d = %s' % (ordN,factor(ordN)))
    L('     matches the in-repo measured value 46998591897600 : %s' % (ordN==46998591897600))
    D5=disc(bdiag(*[U2() for _ in range(5)]))
    L('A_{U(2)^5}: q-dist %s ; zeros %d ; |O| = %d  => isometric to A_N as a form : %s'
      % (qdist(D5), sum(1 for x in D5['order'] if D5['q'](x)==0), zero_count_order(D5)[3],
         zero_count_order(D5)[3]==ordN))
    DU2=disc(U2()); DE8m2=disc(sc(-2,E8()))
    L('A_{U(2)}: q-dist %s, |O| = %d ; A_{E8(-2)}: q-dist %s, |O| = %d'
      % (qdist(DU2), zero_count_order(DU2)[3], qdist(DE8m2), zero_count_order(DE8m2)[3]))
    L('     |W(E8)| = %d ;  |O(A_{E8(-2)})| = |O_8^+(2)| = %d = |W(E8)|/2 : %s'
      % (696729600, zero_count_order(DE8m2)[3], zero_count_order(DE8m2)[3]==696729600//2))
    L('')
    L('=== 3. the order formula validated against brute force ===')
    for dim2,eps2 in [(2,1),(2,-1),(4,1),(4,-1),(6,1)]:
        Dm=standard(dim2,eps2)
        qmap={v:Dm['q'](v) for v in product([0,1],repeat=dim2)}
        bo=brute_order(qmap,dim2)
        L('    dim %d eps %+d : brute force %8d  formula %8d  %s'
          % (dim2,eps2,bo,ortho_order(dim2//2,eps2),'OK' if bo==ortho_order(dim2//2,eps2) else 'MISMATCH'))
    L('')
    L('=== 4. 2-elementary / duality facts used for the kernel ===')
    L('    every q-value on A_N lies in {0,1} (integral): %s'
      % all(DN['q'](x).denominator==1 for x in DN['order']))
    L('    hence 2*N^v is in N and ker(O(N)->O(A_N)) = ker(O(N)->O(N/2N)): see report (E1)')
    L('')
    L('=== 5. W(E8) orbits on E8/2E8 (quoted at Enriques_compu_rev.tex:1460-1461) ===')
    nroots,orbs=weyl_orbits()
    L('    roots of E8: %d ; orbit sizes of W(E8) on E8/2E8: %s  (quoted: sizes 1, 120, 135)' % (nroots,orbs))
    L('')
    L('=== 6. overlattices M supset N with M = U+U+L, L even negative definite rank 8 ===')
    L('    |A_M| * [M:N]^2 = |A_N| = 2^10, so k = [M:N] in {1,2,4,8,16,32} with |disc L| = 2^(10-2log2 k)')
    H=lagrangian(DN)
    L('    Lagrangian H in A_N: %s  (|H| = %s, self-orthogonal: %s)'
      % ('found' if H else 'none', len(H) if H else None, (perp(DN,H)==H) if H else None))
    if H:
        L('    => the even overlattice M = N + H-dual is unimodular of index 2^5 = 32,')
        L('       signature (2,10); by Milnor it is U+U+E8(-1) = II_{2,10}.')
main()
