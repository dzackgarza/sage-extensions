r"""The S_7 candidate for R_P = rho(Stab_{O(L)}(P)) on T_Co, and the Gamma_{Co,2} rows it gives.

Everything is in O(q) = O^+_10(2); no integral parabolic is built.  J = [P/2]
for the explicit plane P = <ep, 2h + a_i + a_j>.  S = Stab_{O(q)}(J) acts on
J^perp/J (128 cosets; O(q) fixes w, so the action is O^+_6(2) = S_8 on the
six-dimensional part).  The candidate R is the preimage in S of a point
stabilizer S_7: it contains the kernel of that action (the unipotent radical
and the GL(J) Levi factor).  The probe checks [S : R] = 8 and counts the
orbits of R and of R cap Stab(p), p in J, on the 67456 conjugates of A_{U(2)}:
the plane and flag rows of Gamma_{Co,2} = rho^{-1}(Stab A_{U(2)}) if R = R_P.
"""
import sys, time
sys.path.insert(0, "tests")
from sage.all import *  # noqa
from sage_extensions.all import *  # noqa
from sage.libs.gap.libgap import libgap
import coble_gamma_co_2_incidence_rows as driver

t0 = time.monotonic()
def log(m): print(f"[{time.monotonic()-t0:7.1f}s] {m}", flush=True)

L = NamedLattices.Tco
A = L.discriminant_group()
Oq = A.orthogonal_group()
elements = tuple(A.elements())
rank = A.elements().ranking_map()
def idx(e): return int(rank(e)) + 1
def perm(g): return libgap.PermList([idx(g(e)) for e in elements])
G = libgap.Group(*[perm(g) for g in Oq.group_generators()])
log(f"|O(q)| = {G.Size()}")
gen = {l: L.module_generator(l) for l in L.module_generating_set()}
e8 = [gen[f"a{i}"] for i in range(1, 9)]
r = next(a + b for i, a in enumerate(e8) for b in e8[i + 1:] if L.pairing(a + b, a + b) == -8)
plane = L.primitive_isotropic_subobject(gen["ep"], 2 * gen["h"] + r)
Jset = driver._plane_class_set(L, plane)
J = libgap.Set([idx(e) for e in Jset])
Jnz = [e for e in Jset if e != A.zero()]
b0 = A.b(A.zero(), A.zero())
perp = [e for e in elements if all(A.b(e, j) == b0 for j in Jnz)]
log(f"|J| = {len(Jset)}, |J^perp| = {len(perp)}, q on J: {[A.q(j) for j in Jnz]}")
cosets = sorted({tuple(sorted(idx(e + j) for j in Jset)) for e in perp})
blocks = libgap([list(c) for c in cosets])
S = libgap.Stabilizer(G, J, libgap.OnSets)
log(f"|Stab J| = {S.Size()}, cosets of J in J^perp: {len(cosets)}")
hom = libgap.ActionHomomorphism(S, blocks, libgap.OnSets)
img = libgap.Image(hom)
log(f"|image on J^perp/J| = {img.Size()}, kernel order {libgap.Kernel(hom).Size()}")
iso = libgap.IsomorphismGroups(img, libgap.SymmetricGroup(8))
log(f"image isomorphic to S_8: {iso != libgap.eval('fail')}")
R = libgap.PreImage(hom, libgap.PreImage(iso, libgap.Stabilizer(libgap.SymmetricGroup(8), 8)))
log(f"|R| = {R.Size()}, [Stab J : R] = {S.Size() / R.Size()} (|rho(Stab P)| of #360: 247726080)")
log(f"R orbits on J minus 0: {[int(libgap.Length(o)) for o in libgap.Orbits(R, [idx(j) for j in Jnz])]}")

AU2 = libgap.Set([idx(e) for e in driver._decomposition(L)])
H = libgap.Orbit(G, AU2, libgap.OnSets)
log(f"|O(q).A_U(2)| = {libgap.Length(H)}")
def sizes(K):
    return sorted((int(libgap.Length(o)) for o in libgap.Orbits(K, H, libgap.OnSets)), reverse=True)
planes = sizes(R)
log(f"plane rows: {len(planes)} orbits, sizes {planes}")
p = idx(Jnz[0])
F = libgap.Intersection(R, libgap.Stabilizer(G, p))
flags = sizes(F)
log(f"flag rows: {len(flags)} orbits, sizes {flags}, |R cap Stab p| = {F.Size()}")
Sp = libgap.Stabilizer(G, p)
log(f"line rows (Stab p): {len(sizes(Sp))} orbits, sizes {sizes(Sp)}")
