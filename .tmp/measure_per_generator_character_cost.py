"""Measured stage-B fraction: per-generator isometry-side character-image cost.

Direct block-gram N = U + U(2) + E8(-2) (target side measured 6.7 s; no
involution/coinvariant rebuild).  Times O(N) generation, then one
discriminant_morphism() and one spinor evaluation per ambient generator —
the per-generator work stage B performs before its (measured instant) GAP
orders.  Stage prints BEFORE each item; a cap leaves ordered attribution.
No Gamma_h, no Schreier family, no orbit work.
"""
import time

START = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic()-START:6.1f}s] {label}", flush=True)


stage("imports")
from sage_extensions.all import *

stage("N = U + U(2) + E8(-2) direct block gram")
U = Lattices(ZZ)([[0, 1], [1, 0]])
U2 = Lattices(ZZ)([[0, 2], [2, 0]])
N = U + U2 + Lattices(ZZ)("E8").twist(2)
stage(f"N: rank {N.rank()}, signature {N.signature_pair()}")

stage("O(N) object")
G = N.O()
stage(f"O(N): {G}")

stage("ambient generating family (group_generators length only)")
generators = tuple(G.group_generators())
stage(f"{len(generators)} ambient generators")

stage("O_plus construction (spinor morphism cold start)")
overlay = N.O_plus()
spinor_morphism = overlay.preimage_morphism()
stage("spinor morphism ready")

for i, g in enumerate(generators):
    stage(f"generator {i}: discriminant_morphism()")
    m = g.discriminant_morphism()
    stage(f"generator {i}: morphism done; spinor evaluation")
    sign = spinor_morphism(g)
    stage(f"generator {i}: spinor done (is_one={sign.is_one()})")

print("MEASURE_OK", flush=True)
