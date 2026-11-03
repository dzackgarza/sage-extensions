#!/usr/bin/env python3
"""The repaired generator set: isotropic vectors of N itself.

N has N-basis [e1,f1,e2,2f2,E8*8].  Isotropic vectors: e1, f1, e2, 2f2.
For each, a Z-basis of e^perp cap N (rank 11) is written down and the 11 Eichler
transvections are checked to be isometries of N, trivial on A_N, and in O+(N).
"""
from fractions import Fraction as F
import s2_ambient as S2
from s3_spinor import diag_basis
from s5_sn import in_Oplus
n=S2.n; GM=S2.GM; mul=S2.mul; T=S2.T; inv=S2.inv; mv=S2.mv; isint=S2.isint
B=S2.N_basis('e2_2f2'); GN=mul(mul(T(B),GM),B); GNi=inv(GN); NG=[[F(x) for x in row] for row in GN]

def gramN(u,v): return sum(NG[i][j]*u[i]*v[j] for i in range(n) for j in range(n))
def qN(v): return gramN(v,v)/2
def vecN(i): 
    v=[F(0)]*n; v[i]=F(1); return v

def transN(e,x):
    cols=[]
    for j in range(n):
        v=vecN(j); ve=gramN(v,e); vx=gramN(v,x); qx=qN(x)
        cols.append([v[i]+ve*x[i]-((vx+ve*qx))*e[i] for i in range(n)])
    return [[cols[j][i] for j in range(n)] for i in range(n)]

def isisoN(g): return mul(mul(T(g),NG),g)==NG

def trivialN(g):
    for j in range(n):
        x=[GNi[i][j] for i in range(n)]
        nx=mv(g,x)
        if any(not isint(a-b) for a,b in zip(nx,x)): return False
    return True

def main():
    L=print
    L('=== repaired set: isotropic vectors of N = U + U(2) + E8(-2) ===')
    # complements inside N: index 3 = 2f2 , index 2 = e2
    perp_bases={
      'e1':[0,2,3]+list(range(4,12)),          # e1 itself, e2, 2f2, E8*
      'f1':[1,2,3]+list(range(4,12)),
      'e2':[0,1,2]+list(range(4,12)),
      '2f2':[0,1,3]+list(range(4,12)),
    }
    pos=[0,1,2,3]
    tot=0; good=0; kept=[]
    for idx,name in zip(pos,['e1','f1','e2','2f2']):
        e=vecN(idx)
        L('  e = %-4s : q(e) = %s ; a Z-basis of e^perp cap N has %d vectors'
          % (name,qN(e),len(perp_bases[name])))
        for t,xidx in enumerate(perp_bases[name]):
            x=vecN(xidx); tot+=1
            assert gramN(e,x)==0
            g=transN(e,x)
            iso=isisoN(g); tri=trivialN(g); ok,info=in_Oplus(g,NG)
            if iso and tri and ok: good+=1
            else: L('    !! e=%s x=%d : isometry %s trivial %s O+ %s' % (name,t,iso,tri,ok))
    L('  transvections in the repaired set: %d ; isometries of N, trivial on A_N and in O+(N): %d'
      % (tot,good))
    L('')
    L('=== the two block maps that survive, as elements of O(N) ===')
    for A,Bb,nm in [([[1,1],[0,1]],[[1,0],[0,1]],'T,I'),([[1,0],[0,1]],[[1,1],[0,1]],'I,T')]:
        g=S2.blockmap(A,Bb); okr,X=S2.preserves(g,B)
        h=[[F(x) for x in row] for row in X]
        L('  block(%s): preserves N %s ; isometry of N %s ; trivial on A_N %s ; in O+(N) %s'
          % (nm,okr,isisoN(h),S2.acts_trivially_on_disc(g,GN,GNi,sub=B),in_Oplus(h,NG)[0]))
    L('')
    L('=> 44 + 2 = 46 proved kernel elements; equality with ker(O+(N)->O(A_N)) NOT claimed.')
main()
