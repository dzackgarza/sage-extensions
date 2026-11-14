"""Issue #17 §4: T1 and T2 on the real N, in CPU seconds (contention-invariant)."""
import os
import time

os.environ["SE_DEBUG_STAGES"] = "1"
WALL = time.monotonic()
CPU = time.process_time()


def stage(label):
    print(f"[wall={time.monotonic() - WALL:8.1f}s cpu={time.process_time() - CPU:8.1f}s] {label}", flush=True)


from tests.acceptance.consumer import element, lattice
from tests.fixtures.oracle_fixtures import load_enriques_87_polarizations, load_e10_fundamental_domain

_ENRIQUES = load_enriques_87_polarizations()
_E10 = load_e10_fundamental_domain()
case = _ENRIQUES[2]
from sage_extensions.catalogue import Involutions

involution = Involutions.I_En
invariant = involution.primitive_extension().invariant
transport = lattice(_E10["gram"]).twist(2).Isom(invariant).an_element()
polarization = invariant.inclusion()(transport(element(transport.domain(), case["face_polarization"])))
anti_invariant_group = involution.polarized(polarization).coinvariant_extension_subgroup()
N = anti_invariant_group.supergroup().domain()
stage(f"N = {N}")

t1, c1 = time.monotonic(), time.process_time()
form = N.discriminant_group()
print(f"[T1] N.discriminant_group(): wall {time.monotonic() - t1:.2f}s cpu {time.process_time() - c1:.2f}s -> {form}", flush=True)

t2, c2 = time.monotonic(), time.process_time()
target = form.orthogonal_group()
print(f"[T2] T1.orthogonal_group(): wall {time.monotonic() - t2:.2f}s cpu {time.process_time() - c2:.2f}s", flush=True)

t3, c3 = time.monotonic(), time.process_time()
order = int(target.cardinality())
print(f"[T2.order] T2.cardinality(): wall {time.monotonic() - t3:.2f}s cpu {time.process_time() - c3:.2f}s -> {order}", flush=True)
print(f"[T2.order] equals |O(A_N)| = 46998591897600: {order == 46998591897600}", flush=True)
stage("T1/T2 published")
print("T1T2_MEASURED", flush=True)
