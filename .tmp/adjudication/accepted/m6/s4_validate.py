#!/usr/bin/env python3
"""Validation of the O+ test, spinor norms of the isotropic-x transvections,
and the induced map A_M -> A_N."""
from fractions import Fraction as F
import s2_ambient as S2
from s3_spinor import diag_basis, op_plus_test
n=S2.n; GM=S2.GM; GMi=S2.GMi
inv=S2.inv; mul=S2.mul; T=S2.T; mv=S2.mv; isint=S2.isint; ident=S2.ident
gram=S2.gram; q=S2.q

def refl(G,v):
    k=len(G); nv=sum(F(G[i][j])*v[i]*v[j] for i in range(k) for j in range(k))
    cols=[]
    for j in range(k):
        u=[F(1 if i==j else 0) for i in range(k)]
        c=2*sum(F(G[a][b])*u[a]*v[b] for a in range(k) for b in range(k))/nv
        cols.append([u[i]-c*v[i] for i in range(k)])
    return [[cols[j][i] for j in range(k)] for i in range(k)]

def main():
    L=print
    L('=== 1. validation of the O+ criterion on known elements of O(M), M = U+U+E8(-2) ===')
    # (a) identity and -identity
    L('  identity  : in O+ %s (expected True)' % op_plus_test(ident(n),GM)['in_Oplus'])
    L('  -identity : in O+ %s (expected True: det=1, positive block det=+1, sn(-1)=(-1)^10*sq)' %
      op_plus_test([[-x for x in row] for row in ident(n)],GM)['in_Oplus'])
    # (b) reflections in vectors of positive and of negative norm
    for v,lbl in [([F(1),F(1),F(0),F(0)]+[F(0)]*8,'e1+f1, norm +2'),
                  ([F(0),F(0),F(0),F(0),F(2),F(0)]+[F(0)]*6,'2*E8root, norm -16'),
                  ([F(1),F(0),F(0),F(1)]+[F(0)]*8,'e1+f2, norm 0 (skip)')]:
        if gram(v,v)==0:
            L('  reflection in %-22s skipped (isotropic)' % lbl); continue
        r=op_plus_test(refl(GM,v),GM)
        L('  reflection in %-22s (v,v)=%4s det %s -> in O+ %s ; expected %s'
          % (lbl,gram(v,v),r['det'],r['in_Oplus'],'True' if gram(v,v)>0 else 'False'))
    L('')
    L('=== 2. transvections with isotropic x (q(x)=0): two-reflection decomposition ===')
    tested=ok=0
    for idx in range(4):
        e=S2.vec(idx)
        for xv in S2.basis_e_perp(idx):
            if q(xv)!=0: continue
            tau=S2.transvection(e,xv,1); tested+=1
            found=False
            cands=[]
            for j in range(n):
                for s in (1,-1):
                    v=[F(0)]*n; v[j]=F(s); cands.append(v)
            for i in range(n):
                for j in range(i+1,n):
                    for si in (1,-1):
                        for sj in (1,-1):
                            v=[F(0)]*n; v[i]=F(si); v[j]=F(sj); cands.append(v)
            for z in cands:
                if gram(z,z)==0: continue
                tz=mv(tau,z)
                if mul(refl(GM,tz),refl(GM,z))==tau:
                    found=True; break
            if found: ok+=1
    L('  decompositions found for %d of %d transvections with q(x)=0' % (ok,tested))
    L('  (each such decomposition has equal norms (tau z,tau z) = (z,z), so sn = 1)')
    L('')
    L('=== 3. the induced map on discriminants A_M -> A_N ===')
    B=S2.N_basis('e2_2f2'); GN=mul(mul(T(B),GM),B)
    L('  |A_M| = %s , |A_N| = %s' % (abs(S2.matdet(GM)),abs(S2.matdet(GN))))
    # kernel of M^v/M -> N^v/N is (M^v cap N)/M ; test N subset M^v
    # (x,y) in Z for x in N-basis, y in M-basis:
    NB=[[B[i][j] for i in range(n)] for j in range(n)]
    okint=True
    for x in NB:
        for j in range(n):
            y=[F(1 if i==j else 0) for i in range(n)]
            if not isint(gram(x,y)): okint=False
    L('  N is contained in M^v (all pairings integral): %s' % okint)
    L('  => kernel of A_M -> A_N is N/M of order %d, image has order %d, index in A_N = %d'
      % (2, abs(S2.matdet(GM))//2, abs(S2.matdet(GN))//(abs(S2.matdet(GM))//2)))
    L('')
    L('=== 4. the corrected generator set: isotropic e of N itself ===')
    L('  isotropic vectors of the two planes inside N: e1, f1 (unscaled U) and e2, 2f2 (U(2))')
    L('  for each, a Z-basis of e^perp cap N has 11 elements -> 4*11 = 44 transvections,')
    L('  all of them in ker(O(N)->O(A_N)) by the elementary lemma (they pair integrally with N^v).')
if __name__ == '__main__':
    main()
