"""Exact verification for the N = U (+) U(2) (+) E8(-2) adjudication (H1-H4).

Conventions
  <.,.> integral Z-lattice, q(x) = <x,x>/2 (even lattice);
  U = Z^2, Gram [[0,1],[1,0]];  U(2) = Z^2, Gram [[0,2],[2,0]];
  E8 = Z^8 with Gram = Cartan matrix C (roots: <a,a>=2, q(a)=1);
  E8(-2) = same Z^8 with Gram -2C  =>  A_{E8(-2)} = (1/2)Z^8/Z^8 = (Z/2)^8,
  which is what Enriques_compu_rev.tex:1458 ("2^8 orbit representatives") uses.
Ambient V: coordinates (a1,b1,a2,b2,e1..e8);  M = Z^12 with Gram G;
  N = {x in M : x_{a2} even} = U (+) <2a2,b2> (+) E8(-2) ≅ U (+) U(2) (+) E8(-2).
  (Enriques_compu_rev.tex:1519-1520 asserts exactly this embedding.)
"""
from fractions import Fraction as F
from itertools import product
from math import prod

def matmul(A,B):
    n,k,m=len(A),len(B),len(B[0])
    return [[sum(A[i][t]*B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]
def T(A): return [list(r) for r in zip(*A)]
def det(M):
    n=len(M); M=[[F(v) for v in row] for row in M]; d=F(1)
    for i in range(n):
        p=next((r for r in range(i,n) if M[r][i]!=0),None)
        if p is None: return F(0)
        if p!=i: M[i],M[p]=M[p],M[i]; d=-d
        d*=M[i][i]
        for r in range(i+1,n):
            f=M[r][i]/M[i][i]
            for c in range(i,n): M[r][c]-=f*M[i][c]
    return d

C=[[0]*8 for _ in range(8)]
for i in range(8): C[i][i]=2
for i,j in [(0,2),(2,3),(3,4),(4,5),(5,6),(6,7),(1,3)]: C[i][j]=C[j][i]=-1
G=[[F(0)]*12 for _ in range(12)]
G[0][1]=G[1][0]=F(1); G[2][3]=G[3][2]=F(1)
for i in range(8):
    for j in range(8): G[4+i][4+j]=F(-2*C[i][j])

def q(x): return sum(x[i]*G[i][j]*x[j] for i in range(12) for j in range(12))/2
def B(x,y): return sum(x[i]*G[i][j]*y[j] for i in range(12) for j in range(12))
def vec(**kw):
    x=[F(0)]*12
    idx={'a1':0,'b1':1,'a2':2,'b2':3}
    for k,v in kw.items():
        if k in idx: x[idx[k]]=F(v)
        else: x[4+int(k[1:])-1]=F(v)
    return x
a1,b1,a2,b2=vec(a1=1),vec(b1=1),vec(a2=1),vec(b2=1)
roots=[vec(**{f'e{i}':1}) for i in range(1,9)]

BN=[[F(0)]*12 for _ in range(12)]
for i in range(12): BN[i][i]=F(2 if i==2 else 1)
Nbas=[BN[i] for i in range(12)]

def inN(x): return all(v.denominator==1 for v in x) and x[2]%2==0
def inM(x): return all(v.denominator==1 for v in x)
def inNdual(x): return all(B(x,n).denominator==1 for n in Nbas)
def inMdual(x):
    if any(x[i].denominator!=1 for i in (0,1,2,3)): return False
    return all((2*x[i]).denominator==1 for i in range(4,12))
def canon(x):
    y=[F(v) for v in x]
    if y[2].denominator==1 and y[2]%2!=0: y[2]-=2
    return tuple(y)

print("="*70); print("H1  embedding N subset M = U+U+E8(-2)")
print("  det G   = |A_M| =",det(G),"   |A_N| = det G_N =",det(matmul(matmul(T(BN),G),BN)))
print("  [M:N] = ",det(BN),"   [N^v:M^v] = |A_N|/([M:N]*|A_M|) =",1024//(2*256))
gens=[a2, vec(b2=F(1,2))]+[vec(**{f'e{i}':F(1,2)}) for i in range(1,9)]
assert all(inNdual(g) for g in gens)
cl=set()
for eps in product([0,1],repeat=10):
    x=[F(0)]*12
    for e,g in zip(eps,gens):
        if e:
            for i in range(12): x[i]+=g[i]
    cl.add(canon(x))
print("  |A_N| enumerated =",len(cl),"  q_N values:",{(2*q(x))%1 for x in cl})
print("  zeros of q_N (isotropic classes) =",sum(1 for x in cl if q(x)%1==0),"(split 2m=10 form: 2^9+2^4=528)")
print("  A_N = A_{U(2)} (+) A_M orthogonal: <a2,e1/2> =",B(a2,gens[2]),"; <b2/2,e1/2> =",B(gens[1],gens[2]))
print("  q_N(a2),q_N(b2/2),q_N(a2+b2/2) =",q(a2)%1,q(gens[1])%1,q([a2[i]+gens[1][i] for i in range(12)])%1)

def ord_split(m):
    r=2
    for k in range(2,m+1): r*=(2**k-1)*(2**(k-1)+1)*2**(2*k-2)
    return r
print("  |O(q_N)| by repo recursion (tests/test_finite_form_groups.py:3-4), m=5:",ord_split(5))
print("  in-repo value 46998591897600 :",ord_split(5)==46998591897600,
      "  = 2^21*3^5*5^2*7*17*31 :",2**21*3**5*5**2*7*17*31==ord_split(5))

print("="*70); print("Lemma T: T_{e,x}(y)=y+<y,e>x-<y,x>e-q(x)<y,e>e")
def Tmap(e,x):
    return lambda y:[y[i]+B(y,e)*x[i]-B(y,x)*e[i]-q(x)*B(y,e)*e[i] for i in range(12)]
def isom(f,vset):
    return all(q(f([F(v) for v in y]))==q(y) for y in vset)
vset=[tuple(vec(**{}) )]
testvecs=[]
for i in range(12):
    v=[F(0)]*12; v[i]=F(1); testvecs.append(tuple(v))
    v=[F(0)]*12; v[i]=F(1,2); testvecs.append(tuple(v))
r0=roots[0]
for (e,x,tag) in [(a1,a2,"e=a1 isotropic, x=a2 isotropic"),(a1,r0,"e=a1, x=r0 root"),
                  (a2,r0,"e=a2, x=r0 root"),(b2,r0,"e=b2, x=r0 root")]:
    f=Tmap(e,x)
    print("   ",tag,": <e,x> =",B(e,x)," q(e) =",q(e)," isometry:",isom(f,testvecs))
xbad=[b1[i]+a2[i]+r0[i] for i in range(12)]
print("   counter-check WITHOUT x perp e (e=a1, x=b1+a2): isometry:",isom(Tmap(a1,xbad),testvecs),
      " <e,x> =",B(a1,xbad)," q(x) =",q(xbad),"  (so x perp e is genuinely needed)")

print("="*70); print("H3 witness:  T = E_{a2,r0}  (a2 = canonical isotropic vector, r0 = root of E8(-2))")
Tw=Tmap(a2,r0)
print("  r0 in a2^perp(M):",B(a2,r0)==0," r0 in E8(-2) subset M:",inM(r0)," q(r0) =",q(r0))
print("  T(N) subset N :",all(inN(Tw(list(n))) for n in Nbas))
print("  T(M) subset M :",all(inM(Tw(list(m))) for m in [BN[i] for i in range(12)]))
inv=Tmap(a2,[-v for v in r0])
print("  T^{-1}=T_{a2,-r0} (additivity, tex:1446) fixes N too:",all(inN(inv(list(n))) for n in Nbas))
halfAm=[]
for eps in product([0,1],repeat=8):
    x=[F(0)]*4+[F(1,2)*e for e in eps]; halfAm.append(tuple(x))
print("  T acts trivially on A_M = (1/2)Z^8/Z^8 :",
      all(inM([Tw(list(y))[i]-y[i] for i in range(12)]) for y in halfAm))
print("   (A_M = (1/2)Z^8/Z^8 : T(1/2 e_i) - 1/2 e_i =",[Tw([F(0)]*4+[F(1,2) if j==0 else F(0) for j in range(8)])[k]-
      ([F(0)]*4+[F(1,2) if j==0 else F(0) for j in range(8)])[k] for k in range(12)],")")
hb=[F(0)]*12; hb[3]=F(1,2)
print("  1/2 b2 in N^v:",inNdual(hb))
Tw_hb=Tw(hb)
print("  T(1/2 b2) - 1/2 b2 =",[Tw_hb[i]-hb[i] for i in range(12)]," in N ?",inN([Tw_hb[i]-hb[i] for i in range(12)]))
print("  => T acts NON-trivially on A_N  (moves the class [1/2 b2])")
def refl(v):
    return lambda y:[y[i]-B(y,v)*v[i]/q(v) for i in range(12)]
print("  reflection factorisation  T = sigma_{r0} o sigma_{r0+q(r0)a2} :",
      all(abs(refl(r0)(refl([r0[i]+q(r0)*a2[i] for i in range(12)])([F(v) for v in y]))[i]-Tw([F(v) for v in y])[i])<F(1,10**9)
          for y in testvecs))
print("  both reflections integral on N:",all(inN(refl(r0)(list(n))) and inN(refl([r0[i]+q(r0)*a2[i] for i in range(12)])(list(n))) for n in Nbas))
print("  spinor: theta(T)=q(r0)*q(r0+q(r0)a2) =",q(r0)*q([r0[i]+q(r0)*a2[i] for i in range(12)]),"== 1 mod squares")

print("="*70); print("H3/H4 reflections in small-norm vectors do NOT act trivially")
v=[a2[i]*2+b2[i] for i in range(12)]
print("  v = 2a2+b2 in N, q(v) =",q(v)," theta(sigma_v) = q(v) =",q(v),"= 2 mod squares (not 1)")
print("  sigma_v(1/2 b2) - 1/2 b2 =",[refl(v)(hb)[i]-hb[i] for i in range(12)]," in N ?",inN([refl(v)(hb)[i]-hb[i] for i in range(12)]))
print("  sigma_v integral on N:",all(inN(refl(v)(list(n))) for n in Nbas))
r_adj=roots[2]   # e3 : B_E8(e1,e3) = -1, so (e1,e3) = -2 mod 4 -> nontrivial shift
print("  r_adj = e3 (adjacent simple root): B_E8(r0,r_adj) =",B(r0,r_adj))
y_half=[F(0)]*4+[F(1,2) if j==2 else F(0) for j in range(8)]
sh=[refl(r0)(y_half)[k]-y_half[k] for k in range(12)]
print("  sigma_r0(1/2 e3) - 1/2 e3 =",sh," in N (i.e. in E8(-2)) ?",inN(sh))
print("  => sigma_r0 acts NON-trivially on D(N) although (r0,r0) = -4 and sn(sigma_r0) = -(r0,r0)/2 = 2")

print("="*70); print("W(E8) orbits on A_{E8(-2)} = (1/2)Z^8/Z^8  (tex:1459-1460 says 1,120,135)")
def in_origin(x): return all(v.denominator==1 for v in x)
classes_Am=[]
for eps in product([0,1],repeat=8):
    x=[F(0)]*8
    for e,i in zip(eps,range(8)):
        if e: x[i]=F(1,2)
    classes_Am.append(tuple(x))
def reflW(i,x):
    """s_i acting on (1/2)Z^8/Z^8, E8 in SIMPLE-ROOT coordinates (Gram = C, alpha_i = e_i):
       y -> y - (y,alpha_i) alpha_i ; on v=2y in Z^8: v -> v - (sum_k v_k C_ik) e_i (mod 2)."""
    v=[2*x[j] for j in range(8)]
    s=sum(v[k]*C[i][k] for k in range(8))
    w=[v[j]-(s if j==i else 0) for j in range(8)]
    return tuple(F(w[j]%2,2) for j in range(8))
seen=set(); orbits=[]
for x in classes_Am:
    if x in seen: continue
    orb={x}; frontier=[x]
    while frontier:
        y=frontier.pop()
        for i in range(8):
            z=reflW(i,y)
            if z not in orb: orb.add(z); frontier.append(z)
    seen|=orb; orbits.append(len(orb))
print("  W(E8)-orbit sizes on A_{E8(-2)} =",sorted(orbits)," (sum =",sum(orbits),")")


print("="*70); print("rank_2 (GHS 0810.1614 p.3: max rank of a sublattice with det coprime to 2)")
def mod2_rank(Gram):
    n=len(Gram); rows=[[int(Gram[i][j])%2 for j in range(n)] for i in range(n)]
    r=0
    for c in range(n):
        piv=None
        for i in range(r,n):
            if rows[i][c]: piv=i; break
        if piv is None: continue
        rows[r],rows[piv]=rows[piv],rows[r]
        for i in range(n):
            if i!=r and rows[i][c]:
                rows[i]=[(rows[i][k]+rows[r][k])%2 for k in range(n)]
        r+=1
    return r
print("   rank of the mod-2 form on M/2M (12 dims) =",mod2_rank(G),"-> rank_2(M) <=",mod2_rank(G))
GNb=matmul(matmul(T(BN),G),BN)
print("   rank of the mod-2 form on N/2N (12 dims) =",mod2_rank(GNb),"-> rank_2(N) <=",mod2_rank(GNb))
print("   (GHS Prop 3.4 needs rank_2 >= 6 and two hyperbolic planes; M has 2 planes but rank_2 = 4;")
print("    N has only ONE hyperbolic plane: div_N(e) = 2 for 0 != e in N cap U(2) isotropic)")

print("="*70); print("divisibility of the canonical isotropic vectors")
def div(vec, lat_dual_gens):
    from math import gcd
    vals=[abs(B(vec,y)) for y in lat_dual_gens]
    vals=[v for v in vals if v!=0]
    d=0
    for v in vals: d=gcd(d,int(v)) if v.denominator==1 else d
    return d
print("   div_M(a2): (a2,b2) =",B(a2,b2),"  div_M(a1): (a1,b1) =",B(a1,b1))
print("   (a2, N^v): (a2, 1/2 b2) =",B(a2,[F(0)]*3+[F(1,2)]+[F(0)]*8),"  => (a2,N^v)=1/2 Z ; 2a2 in N => div_N(2a2)=2")

print("="*70); print("H4: the four elementary block maps of SL_2(Z)^2 on U(+)U are Eichler transvections")
def block(A,lr):
    """isometry of U(+)U given by X |-> A X (left) or X A^ad (right) in the det model
       a1=E11,b1=E22,a2=E12,b2=-E21; returns the 4x4 matrix on (a1,b1,a2,b2)."""
    # coordinate maps: X = x1*E11 + y1*E22 + x2*E12 + y2*(-E21) = [[x1,x2],[-y2,y1]]
    def toX(c): return [[c[0],c[2]],[-c[3],c[1]]]
    def toC(X): return [F(X[0][0]),F(X[1][1]),F(X[0][1]),-F(X[1][0])]
    cols=[]
    for i in range(4):
        c=[F(0)]*4; c[i]=F(1)
        X=toX(c)
        Y=matmul(A,X) if lr=='L' else matmul(X,[[A[1][1],-A[0][1]],[-A[1][0],A[0][0]]])
        cols.append(toC(Y))
    return [[cols[j][i] for j in range(4)] for i in range(4)]
def apply4(M4,c):
    out=[F(0)]*12
    for i in range(4):
        for j in range(4):
            if M4[i][j]:
                out[i]+=F(M4[i][j])*c[j]
    return out
E1=[[1,1],[0,1]]; E2=[[1,0],[1,1]]
for A,lr,tag in [(E1,'L','left by [[1,1],[0,1]]'),(E2,'L','left by [[1,0],[1,1]]'),
                 (E1,'R','right by [[1,1],[0,1]]'),(E2,'R','right by [[1,0],[1,1]]')]:
    M4=block(A,lr)
    print("  ",tag,": matrix on (a1,b1,a2,b2) =",M4)
    found=False
    for (e,x) in [(a1,a2),(a2,b1),(b1,a2),(a2,a1),(a1,b2),(b2,a1),(b1,b2),(b2,b1),
                  ([-v for v in a1],a2),([-v for v in a2],b1),([-v for v in b1],a2),([-v for v in b2],a1)]:
        f=Tmap(e,x)
        ok=True
        for j in range(4):
            col=[F(0)]*12
            for i in range(4): col[i]=F(M4[i][j])
            if f([F(int(i==j)) for i in range(12)])!=col: ok=False
        for j in range(4,12):
            if f([F(int(i==j)) for i in range(12)])!=[F(int(i==j)) for i in range(12)]: ok=False
        if ok:
            print("       = T_{%s,%s}  with q(x) = %s"%(str(e[:4]),str(x[:4]),q(x)))
            found=True; break
    if not found: print("       (no single Eichler transvection found in the search list)")
print("  additivity check: T_{a1,a2+r0} = T_{a1,r0} o T_{a1,a2} :",
      all(Tmap(a1,[a2[i]+r0[i] for i in range(12)])([F(v) for v in y])==Tmap(a1,r0)(Tmap(a1,a2)([F(v) for v in y])) for y in testvecs))
print("  => theta(T_{a1,a2}) = theta(T_{a1,a2+r0})/theta(T_{a1,r0}) = (q(x+r0)^2)/(q(r0)^2) = 1")
