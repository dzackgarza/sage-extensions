#!/usr/bin/env python3
"""H4: the real spinor norm of every named generator.

O+(p,q) := ker(sn_R : O(p,q) -> R*/R*^2).  For p,q >= 1 the four components of
O(p,q) are labelled by (det g , c(g)) where c(g) = sign of the determinant of
the block of g on a fixed maximal positive-definite subspace P.  Since a
reflection in a positive-norm vector has (det,c) = (-1,-1) and one in a
negative-norm vector has (-1,+1), while the identity component is (+1,+1),
    sn_R(g) = +1  <=>  det g = c(g).
The script validates that rule on random reflections of both norm signs, then
applies it to the 48 named generators.
"""
from fractions import Fraction as F
import random, s2_ambient as S2
from s3_spinor import diag_basis
from s4_validate import refl
n=S2.n; GM=S2.GM; GMi=S2.GMi; mul=S2.mul; mv=S2.mv; gram=S2.gram; q=S2.q
B=S2.N_basis('e2_2f2'); GN=mul(mul(S2.T(B),GM),B); GNi=S2.inv(GN)

def components(g,G):
    k=len(G)
    vecs=diag_basis(G)
    Bm=[[vecs[j][0][i] for j in range(k)] for i in range(k)]
    detg=S2.matdet(g)
    gp=mul(S2.inv(Bm),mul(g,Bm))
    pos=[j for j in range(k) if vecs[j][2]>0]; neg=[j for j in range(k) if vecs[j][2]<0]
    dpos=S2.matdet([[gp[i][j] for j in pos] for i in pos])
    dneg=S2.matdet([[gp[i][j] for j in neg] for i in neg])
    return detg,dpos,dneg,(1 if dpos>0 else -1)

def in_Oplus(g,G):
    detg,dpos,dneg,c=components(g,G)
    return detg==c, dict(det=detg,dpos=dpos,dneg=dneg,c=c)

def main():
    L=print
    L('=== validation: reflections s_v with random v of both norm signs (M) ===')
    random.seed(7); good=0; tot=0
    forced=[]
    for coef in [(1,0,0,0),(1,1,1,1),(2,0,0,2),(1,-1,2,0),(3,1,0,1)]:
        v=[F(0)]*n
        for i,c in enumerate(coef): v[i]=F(c)
        forced.append(v)
    for v in forced+[[F(random.randint(-2,2)) for _ in range(n)] for _ in range(12)]:
        if gram(v,v)==0: continue
        tot+=1
        ok,info=in_Oplus(refl(GM,v),GM)
        expect = gram(v,v)>0
        L('  (v,v)=%5s  det=%2s  c=%2s  => sn_R=+1 : %-5s  expected %-5s  %s'
          % (gram(v,v),info['det'],info['c'],ok,expect,'OK' if ok==expect else 'MISMATCH'))
        if ok==expect: good+=1
    L('  rule agrees with the theory (sn_R(s_v) = (v,v) mod squares) on %d of %d reflections' % (good,tot))
    L('')
    L('=== the 48 named generators on M, and on N when they preserve it ===')
    gens=[]
    for A,Bb,nmA,nmB in [([[0,-1],[1,0]],[[1,0],[0,1]],'S','I'),([[1,1],[0,1]],[[1,0],[0,1]],'T','I'),
                         ([[1,0],[0,1]],[[0,-1],[1,0]],'I','S'),([[1,0],[0,1]],[[1,1],[0,1]],'I','T')]:
        gens.append(('block(A=%s,B=%s)'%(nmA,nmB),S2.blockmap(A,Bb)))
    names=['e1','f1','e2','f2']
    for idx in range(4):
        for j,xv in enumerate(S2.basis_e_perp(idx)):
            gens.append(('T(e=%s,x=%d)'%(names[idx],j),S2.transvection(S2.vec(idx),xv,1)))
    allM=[]; allN=[]
    for nm,g in gens:
        okM,infoM=in_Oplus(g,GM)
        okr,X=S2.preserves(g,B)
        if okr:
            okN,infoN=in_Oplus([[F(x) for x in row] for row in X],GN)
            allN.append((nm,okN))
            L('  %-20s det %2s c %2s -> O+(M) %-5s | preserves N, in O+(N) %s'%(nm,infoM['det'],infoM['c'],okM,okN))
        else:
            L('  %-20s det %2s c %2s -> O+(M) %-5s | does not preserve N'%(nm,infoM['det'],infoM['c'],okM))
        allM.append((nm,okM))
    L('')
    L('all 48 named generators in O+(M): %s' % all(i[1] for i in allM))
    L('all 42 N-preserving generators in O+(N): %s' % all(i[1] for i in allN))
if __name__ == '__main__':
    main()
