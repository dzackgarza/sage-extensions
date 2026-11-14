"""Owner reproducer: vector stabilizer of a NON-isotropic, non-basis vector in a rank-10 (1,9) lattice.

The port's failing subgroup is {g in O(K) : g fixes -11e0-30e1+...}, a specific non-basis vector in the
Lorentzian quotient K. The basis-vector isotropic case works (164 generators, 620 s), so this probe varies
exactly that: a non-isotropic combination with several nonzero coordinates.
"""
import time, traceback
from sage_extensions.all import ZZ, Lattices

t0 = time.monotonic()
def stage(m): print(f"[t={time.monotonic()-t0:8.1f}s] {m}", flush=True)

L = Lattices(ZZ)([[0,1],[1,0]]) + Lattices(ZZ)([[-1,0,0,0,0,0,0,0],[0,-1,0,0,0,0,0,0],[0,0,-2,0,0,0,0,0],[0,0,0,-2,0,0,0,0],[0,0,0,0,-2,0,0,0],[0,0,0,0,0,-2,0,0],[0,0,0,0,0,0,-2,0],[0,0,0,0,0,0,0,-2]])
stage(f"L {L.signature_pair()}")
labels = tuple(L.module_generating_set())
coords = [0]*10
coords[0] = -11; coords[1] = -30
coords[2] = 23; coords[3] = 23
v = L(coords)
stage(f"v = {v}, q(v) = {v.q()}, content = {v.content()}")
S = L.O().stabilizer(v)
stage(f"S: {S}")
try:
    gens = tuple(S.group_generators())
    stage(f"GENERATORS OK: {len(gens)}")
    print("NONISOTROPIC_STABILIZER_OK", flush=True)
except Exception as e:
    print(f"FAIL {type(e).__name__}: {str(e)[:400]}", flush=True)
    traceback.print_exc()
    print("FAILURE_CAPTURED", flush=True)
