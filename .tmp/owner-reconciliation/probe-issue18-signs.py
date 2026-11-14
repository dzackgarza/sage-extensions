"""Issue-18: does the delivered line-stabilizer family act setwise ({+-1}) or only pointwise (+1)?

Rebuilds the apex stabilizer on the real Enriques N and the published line I_1_1 exactly as the
attribution probe does, then converts only a PREFIX of the family to integral isometries and prints
each one's action on the line. A -1 is the sign-reversing content the issue says is missing.
"""
import json, os, time
from sage_extensions.all import ZZ, Lattices

PREFIX = int(os.environ.get("PREFIX", "240"))
t0 = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic()-t0:8.1f}s] {label}", flush=True)


f = json.load(open("/work/tests/fixtures/unpolarized_enriques.json"))
N = Lattices(ZZ)([[int(x) for x in r] for r in f["lattice"]["gram"]])
rep = f["component_preserving_group"]["line_representatives"][0]
v = N([int(x) for x in rep["basis"][0]])
stage(f"N rank {N.rank()} sig {N.signature_pair()}; line {rep['id']}")

from tests.acceptance.consumer import lattice, element
from sage_indefinite_port.indefinite.recursive import EichlerRecursion
t = time.monotonic()
action = EichlerRecursion().isotropic_stabilizer_action((v,), ((-v,),))
stage(f"isotropic_stabilizer_action {time.monotonic()-t:.1f}s")
t = time.monotonic()
stab = action.stabilizer()
gens = tuple(stab.group_generators())
stage(f"stabilizer().group_generators() {time.monotonic()-t:.1f}s: {len(gens)} generators")

signs = []
negatives = []
t = time.monotonic()
for index, g in enumerate(gens[:PREFIX]):
    integral = N.integral_isometry(g)
    image = integral(v)
    if image == v:
        signs.append(1)
    elif image == -v:
        signs.append(-1)
        negatives.append(index)
    else:
        signs.append(None)
stage(f"converted {len(signs)} of {len(gens)} in {time.monotonic()-t:.1f}s")
print(f"SIGNS prefix={len(signs)} plus={signs.count(1)} minus={signs.count(-1)} other={signs.count(None)}", flush=True)
print(f"NEGATIVE INDICES {negatives[:20]}", flush=True)
print(f"SETWISE {'YES' if negatives else 'NOT-OBSERVED-IN-PREFIX'}", flush=True)
print("SIGNS_OK", flush=True)
