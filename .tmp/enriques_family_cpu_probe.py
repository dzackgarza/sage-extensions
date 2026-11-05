"""Issue #17: does the case_3 Γ_h generating family realize inside the 600 s budget?

Wall time is meaningless while the VM is shared, so the budget is enforced and
reported in CPU seconds (SIGPROF on ITIMER_PROF counts process CPU time only).
Every stage prints both clocks: wall since start and cumulative process CPU.
"""
import os
import signal
import sys
import time

os.environ["SE_DEBUG_STAGES"] = "1"

WALL_START = time.monotonic()
CPU_START = time.process_time()
BUDGET_CPU = 600.0


def stage(label):
    print(
        f"[wall={time.monotonic() - WALL_START:8.1f}s cpu={time.process_time() - CPU_START:8.1f}s] {label}",
        flush=True,
    )


class Budget(BaseException):
    pass


def over_budget(signum, frame):
    raise Budget()


signal.signal(signal.SIGPROF, over_budget)

stage("imports")
from tests.acceptance.consumer import element, lattice, subgroup_classes, isotropic_classes
from tests.fixtures.oracle_fixtures import load_enriques_87_polarizations, load_e10_fundamental_domain

_ENRIQUES = load_enriques_87_polarizations()
_E10 = load_e10_fundamental_domain()
case = _ENRIQUES[2]
stage(f"case_3: order {case['group_order']}, L/P/F {case['line_orbits']}/{case['plane_orbits']}/{case['flag_orbits']}")

from sage_extensions.catalogue import Involutions

involution = Involutions.I_En
invariant = involution.primitive_extension().invariant
transport = lattice(_E10["gram"]).twist(2).Isom(invariant).an_element()
polarization = invariant.inclusion()(transport(element(transport.domain(), case["face_polarization"])))
stage("polarization transported")

anti_invariant_group = involution.polarized(polarization).coinvariant_extension_subgroup()
stage("coinvariant_extension_subgroup()")
N = anti_invariant_group.supergroup().domain()
group = anti_invariant_group.intersection(N.O_plus())
stage(f"G_h built; N = {N}")

print("---- the acceptance obligation: the generating family of G_h, and T1..T4 ----", flush=True)
signal.setitimer(signal.ITIMER_PROF, BUDGET_CPU)
try:
    generators = tuple(group.group_generators())
except Budget:
    stage(f"BUDGET: group_generators() exceeded {BUDGET_CPU:.0f} CPU seconds")
    print("FAMILY_OVER_BUDGET", flush=True)
    sys.exit(3)
finally:
    signal.setitimer(signal.ITIMER_PROF, 0)
stage(f"group_generators() returned {len(generators)} generators")

t1 = time.monotonic()
t1c = time.process_time()
form = N.discriminant_group()
print(f"[T1] N.discriminant_group(): wall {time.monotonic() - t1:.2f}s cpu {time.process_time() - t1c:.2f}s -> {form}", flush=True)

t2 = time.monotonic()
t2c = time.process_time()
target = form.orthogonal_group()
print(f"[T2] form.orthogonal_group(): wall {time.monotonic() - t2:.2f}s cpu {time.process_time() - t2c:.2f}s", flush=True)

t3 = time.monotonic()
t3c = time.process_time()
images = tuple(generator.discriminant_morphism() for generator in generators)
print(f"[T3] per-generator discriminant_morphism() x {len(generators)}: wall {time.monotonic() - t3:.2f}s cpu {time.process_time() - t3c:.2f}s", flush=True)

t4 = time.monotonic()
t4c = time.process_time()
image = target.subgroup_on(images)
order = int(image.cardinality())
print(f"[T4] target.subgroup_on(images).cardinality(): wall {time.monotonic() - t4:.2f}s cpu {time.process_time() - t4c:.2f}s -> {order}", flush=True)
print(f"published group_order = {case['group_order']}; equal: {order == case['group_order']}", flush=True)

stage("T1..T4 done")
print("FAMILY_MEASURED", flush=True)
