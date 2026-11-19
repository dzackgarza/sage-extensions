r"""Gamma_{Co,2}'s line, plane and flag rows on T_Co as double cosets in O(q).

Gamma = rho^{-1}(P_0), P_0 = Stab_{O(q)}(A_{U(2)}), contains ker rho, so for a
single O(L)-orbit X = O(L)/Stab(x) the Gamma-orbits on X are the double cosets
P_0 \ O(q) / rho(Stab(x)), i.e. the orbits of rho(Stab(x)) on the O(q)-orbit of
A_{U(2)} (rho onto O(q): Nikulin, Izv. 1980, Thm 3.6.3, T_Co 2-elementary
indefinite).  This probe computes, in O(q) only, the orbits of

* rho(Stab_{O(L)}(P))           (planes),
* Stab_{O(q)}(p), p in J        (lines: rho(Stab(v)) = Stab(p), checked below),
* rho(Stab(P)) cap Stab_{O(q)}(p) (flags)

on the 67456 conjugates of A_{U(2)}, and the sizes of the P_0-orbits on the
527 singular points and the 23715 classes J.
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
def perm(g): return libgap.PermList([int(rank(g(e))) + 1 for e in elements])
def pts(S): return libgap.Set([int(rank(e)) + 1 for e in S])
G = libgap.Group(*[perm(g) for g in Oq.group_generators()])
log(f"|O(q)| = {G.Size()}")
AU2 = pts(driver._decomposition(L))
P0 = libgap.Stabilizer(G, AU2, libgap.OnSets)
log(f"|P_0| = {P0.Size()}")
H = libgap.Orbit(G, AU2, libgap.OnSets)
log(f"|O(q).A_U(2)| = {libgap.Length(H)}")

labels = tuple(L.module_generating_set())
gen = {l: L.module_generator(l) for l in labels}
ep = gen["ep"]
log(f"generators {labels}; (h,h) = {L.pairing(gen['h'], gen['h'])}")
others = [l for l in labels if l not in ("ep", "fp")]
h = gen["h"]
e8 = [gen[f"a{i}"] for i in range(1, 9)]
# a vector r of E8(-2) of norm -8 (an E8 vector of norm 4); then 2h + r is isotropic
# and orthogonal to ep, and <ep, 2h + r> is a primitive isotropic plane.  O(L) has
# one plane orbit on T_Co (the O row), so any such plane represents it.
r = next(a + b for i, a in enumerate(e8) for b in e8[i + 1:]
         if L.pairing(a + b, a + b) == -8)
plane = L.primitive_isotropic_subobject(ep, 2 * h + r)
log(f"plane {plane}; parabolic complete: {plane.is_parabolic_complete()}")
rho = L.discriminant_representation()
RP = libgap.Group(*[perm(rho(g)) for g in plane.parabolic_stabilizer_generators()])
J = pts(driver._plane_class_set(L, plane))
StabJ = libgap.Stabilizer(G, J, libgap.OnSets)
log(f"|rho(Stab P)| = {RP.Size()}, |Stab J| = {StabJ.Size()}, index {StabJ.Size()/RP.Size()}")
zero = int(rank(A.zero())) + 1
Jpts = [x for x in J if int(x) != zero]
log(f"rho(Stab P) orbits on J minus 0: {[list(o) for o in libgap.Orbits(RP, Jpts)]}")

def orbit_sizes(K):
    return sorted((int(libgap.Length(o)) for o in libgap.Orbits(K, H, libgap.OnSets)), reverse=True)

planes = orbit_sizes(RP); log(f"plane orbits: {len(planes)} sizes {planes}")
p = Jpts[0]
Sp = libgap.Stabilizer(G, p)
log(f"|Stab p| = {Sp.Size()}, [O(q):Stab p] = {G.Size()/Sp.Size()}")
lines = orbit_sizes(Sp); log(f"line orbits: {len(lines)} sizes {lines}")
flags_total = 0
for q in Jpts:
    F = libgap.Intersection(RP, libgap.Stabilizer(G, q))
    f = orbit_sizes(F); log(f"flag orbits at p={q}: {len(f)} sizes {f}, |F| = {F.Size()}")
F = libgap.Intersection(RP, Sp)
log(f"flag orbits (one flag type): {len(orbit_sizes(F))}")

singular = libgap.Orbit(G, p)
log(f"P_0-orbits on the {libgap.Length(singular)} singular points: "
    f"{sorted((int(libgap.Length(o)) for o in libgap.Orbits(P0, singular)), reverse=True)}")
classesJ = libgap.Orbit(G, J, libgap.OnSets)
log(f"P_0-orbits on the {libgap.Length(classesJ)} classes J: "
    f"{sorted((int(libgap.Length(o)) for o in libgap.Orbits(P0, classesJ, libgap.OnSets)), reverse=True)}")
