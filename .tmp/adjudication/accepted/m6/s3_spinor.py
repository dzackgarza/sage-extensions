#!/usr/bin/env python3
"""H4: which named generators lie in O+ (identity component / real spinor kernel)?

Also: exact witnesses for the discriminant-action failure on N, and the
two-reflection identity tau_{e,x} = s_x s_{x+q(x)e} for q(x) != 0.
"""
from fractions import Fraction as F
import s2_ambient as S2

n=S2.n; GM=S2.GM; GMi=S2.GMi
inv=S2.inv; mul=S2.mul; T=S2.T; mv=S2.mv; isint=S2.isint; ident=S2.ident
gram=S2.gram; q=S2.q

# ---------- exact diagonalisation of the Gram matrix (Lagrange) ----------
def lagrange(G):
    """Return (T, diagvals) with T^T G T = diag(diagvals), T unimodular-ish rational."""
    k=len(G); A=[[F(G[i][j]) for j in range(k)] for i in range(k)]
    Tm=ident(k); d=[]
    basis=list(range(k))
    def norm(e):
        return sum(A[i][j]*e[i]*e[j] for i in range(k) for j in range(k))
    idx=list(range(k)); cur=[ [F(1 if j==i else 0) for j in range(k)] for i in range(k)]
    # work on the subspace spanned by cur
    while cur:
        # find a vector in span(cur) with nonzero norm (search small combinations)
        found=None
        for coef in [[1]+[0]*(len(cur)-1)]+[[0]*i+[1]+[0]*(len(cur)-i-1) for i in range(1,len(cur))]:
            v=[sum(coef[t]*cur[t][j] for t in range(len(cur))) for j in range(k)]
            if norm(v)!=0: found=v; break
        if found is None:
            raise RuntimeError('degenerate')
        v=found; nv=norm(v)
        base=[v[j]/nv for j in range(k)]
        # replace: orthogonalise all other generators against v
        newcur=[]
        for u in cur:
            cu=sum(A[i][j]*u[i]*v[j] for i in range(k) for j in range(k))
            if all(u[j]==0 for j in range(k)): continue
            if [u[j]/1 for j in range(k)]==[v[j] for j in range(k)]: continue
            w=[u[j]-cu*base[j] for j in range(k)]
            if any(x!=0 for x in w): newcur.append(w)
        cur=newcur
        d.append(nv)
        Tm=[[Tm[i][j] for j in range(k)] for i in range(k)]
        Tm=[[Tm[i][j] for j in range(k)] for i in range(k)]
        # accumulate: T columns are v, w, ...
        pass
    return d

def diag_basis(G):
    """Gram-Schmidt on the indefinite form: returns list of mutually orthogonal
    vectors (as coordinate rows) with norms +-1, spanning Q^rank."""
    k=len(G)
    def norm(v): return sum(F(G[i][j])*v[i]*v[j] for i in range(k) for j in range(k))
    def dot(u,v): return sum(F(G[i][j])*u[i]*v[j] for i in range(k) for j in range(k))
    vecs=[]
    pool=[[F(1 if j==i else 0) for j in range(k)] for i in range(k)]
    while pool:
        # find a nonzero-norm combination: try the pool vectors, then pairwise sums
        picked=None
        for v in pool:
            if norm(v)!=0: picked=v; break
        if picked is None:
            for a in range(len(pool)):
                for b in range(a+1,len(pool)):
                    w=[pool[a][i]+pool[b][i] for i in range(k)]
                    if norm(w)!=0: picked=w; break
                if picked: break
        if picked is None: raise RuntimeError('degenerate')
        v=picked; nv=norm(v)
        s=1 if nv>0 else -1
        u=[c/ (nv*s) for c in v]
        # normalise so that (u,u) = s   (scale by |nv|)
        base=[F(c) for c in v]
        scale=abs(nv)**F(1,2) if False else None
        vecs.append((u,s,nv))
        # orthogonalise the pool
        newpool=[]
        for w in pool:
            if any(w[i]!=0 for i in range(k)):
                c=dot(w,v)/nv
                z=[w[i]-c*v[i] for i in range(k)]
                if any(x!=0 for x in z): newpool.append(z)
        pool=newpool
    return vecs

def op_plus_test(g,G):
    """g in O+ (identity component) iff det g = 1 and the positive 2x2 block in a
    diagonalising basis has positive determinant."""
    k=len(G)
    vecs=diag_basis(G)
    assert len(vecs)==k
    # basis matrix: columns u_i (unnormalised direction) => B^T G B = diag(s_i * |nv|)
    B=[[vecs[j][0][i] for j in range(k)] for i in range(k)]
    D=[[F(0)]*k for _ in range(k)]
    for j in range(k): D[j][j]=vecs[j][2]     # (u_j,u_j) with u_j as built
    detg=S2.matdet(g)
    gB=mul(g,B)
    gp=mul(inv(B),gB)                          # g in the diagonalising basis
    pos=[j for j in range(k) if vecs[j][2]>0]
    neg=[j for j in range(k) if vecs[j][2]<0]
    def subdet(M,Is,Js):
        return S2.matdet([[M[i][j] for j in Is] for i in Js]) if len(Is)==len(Js) else None
    dpos=subdet(gp,pos,pos); dneg=subdet(gp,neg,neg)
    return dict(det=detg,dpos=dpos,dneg=dneg,npos=len(pos),nneg=len(neg),
                in_Oplus=(detg==1 and dpos is not None and dpos>0))

def main():
    L=print
    # re-derive the generator lists exactly as in s2
    B=S2.N_basis('e2_2f2'); GN=mul(mul(T(B),GM),B); GNi=inv(GN)
    gens=[]
    for A,Bb,nmA,nmB in [([[0,-1],[1,0]],[[1,0],[0,1]],'S','I'),([[1,1],[0,1]],[[1,0],[0,1]],'T','I'),
                         ([[1,0],[0,1]],[[0,-1],[1,0]],'I','S'),([[1,0],[0,1]],[[1,1],[0,1]],'I','T')]:
        gens.append(('block(A=%s,B=%s)'%(nmA,nmB),S2.blockmap(A,Bb)))
    names=['e1','f1','e2','f2']
    for idx in range(4):
        for j,xv in enumerate(S2.basis_e_perp(idx)):
            gens.append(('T(e=%s,x=%d)'%(names[idx],j),S2.transvection(S2.vec(idx),xv,1)))
    L('total named generators: %d' % len(gens))
    L('')
    L('=== 1. isometry + triviality on A_M (the quoted claim) + O+ membership of M ===')
    D=diag_basis(GM); posn=sum(1 for v in D if v[2]>0); negn=sum(1 for v in D if v[2]<0)
    L('M has signature (%d,%d) computed from the Gram matrix' % (posn,negn))
    bad=0
    for nm,g in gens:
        iso=S2.is_iso(g); tri=S2.acts_trivially_on_disc(g,GM,GMi)
        op=op_plus_test(g,GM)
        if not iso or not tri: bad+=1
        L('  %-20s isometry %-5s trivial on A_M %-5s det %s  -> in O+(M): %s (pos.block det %s)'
          % (nm,iso,tri,op['det'],op['in_Oplus'],op['dpos']))
    L('generators failing isometry or A_M-triviality: %d' % bad)
    L('')
    L('=== 2. the index-2 sublattice N: preservation, A_N-action, O+(N) ===')
    DN=diag_basis(GN); L('N has signature (%d,%d)' % (sum(1 for v in DN if v[2]>0),sum(1 for v in DN if v[2]<0)))
    keep=[]; nontriv=[]
    for nm,g in gens:
        okr,X=S2.preserves(g,B)
        if not okr: 
            L('  %-20s does not preserve N' % nm); continue
        tri=S2.acts_trivially_on_disc(g,GN,GNi,sub=B)
        h=[[F(x) for x in row] for row in X]
        op=op_plus_test(h,GN)
        keep.append((nm,tri,op['in_Oplus']))
        if not tri: nontriv.append(nm)
        L('  %-20s preserves N; trivial on A_N %-5s ; in O+(N) %s' % (nm,tri,op['in_Oplus']))
    L('')
    L('descended generators: %d ; of them trivial on A_N: %d ; NOT trivial: %d'
      % (len(keep),sum(1 for k in keep if k[1]),len(nontriv)))
    L('witnesses (preserve N, act NON-trivially on A_N): %s' % nontriv)
    L('all descended generators in O+(N): %s' % all(k[2] for k in keep))
    L('')
    L('=== 3. explicit coset witness for tau_{f2,x}, x a basis vector of E8(-2) ===')
    # N^v generator 1/2 e2 : coordinates in N-basis
    e2h=[F(0)]*n; e2h[2]=F(1,2)
    for j,xv in enumerate(S2.basis_e_perp(3)):
        nm='T(e=f2,x=%d)'%j
        g=dict(gens)[nm]
        w=mv(g,e2h)
        diff=[w[i]-e2h[i] for i in range(n)]
        # is diff in N?
        inN=all(isint(c) for c in mv(inv(B),diff))
        L('  %-14s tau(1/2 e2) - 1/2 e2 = %s ; lies in N: %s ; q(x) = %s'
          % (nm,[str(c) for c in diff],inN,q(S2.basis_e_perp(3)[j])))
    L('')
    L('=== 4. two-reflection identity  tau_{e,x} = s_x * s_{x+q(x)e}  for q(x) != 0 ===')
    def refl(v):
        nv=gram(v,v); cols=[]
        for j in range(n):
            u=[F(1 if i==j else 0) for i in range(n)]
            c=2*gram(u,v)/nv
            cols.append([u[i]-c*v[i] for i in range(n)])
        return [[cols[j][i] for j in range(n)] for i in range(n)]
    ok=0; tested=0
    for idx in range(4):
        e=S2.vec(idx)
        for xv in S2.basis_e_perp(idx):
            if q(xv)==0: continue
            tested+=1
            tau=S2.transvection(e,xv,1)
            x2=[xv[i]+q(xv)*e[i] for i in range(n)]
            lhs=mul(refl(xv),refl(x2))
            if lhs==tau: ok+=1
    L('  identity verified for %d of %d transvections with q(x) != 0' % (ok,tested))
    L('  => spinor norm of every such transvection is q(x)*q(x) = square, so it lies in O+.')
if __name__ == '__main__':
    main()
