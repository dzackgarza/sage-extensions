"""Issue #286: the port pin, the O(T_Co) generator call, and the isotropic orbit count."""
import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


import sage_indefinite_port

stage(f"port imported from {sage_indefinite_port.__file__}")

T = NamedLattices.Tco
stage(f"T_Co: rank {T.module_rank()}, signature {T.signature()}, even {T.is_even()}")
O = T.Aut()
stage("O(T_Co) built")

began = time.monotonic()
try:
    generators = tuple(O.group_generators())
    stage(f"O(T_Co).group_generators(): {len(generators)} generators in {time.monotonic() - began:.1f}s")
except Exception:
    print(f"group_generators RAISED after {time.monotonic() - began:.1f}s", flush=True)
    traceback.print_exc()
    generators = ()

if generators:
    began = time.monotonic()
    try:
        representatives = tuple(O.isotropic_orbit_representatives(1))
        stage(f"isotropic_orbit_representatives(1): {len(representatives)} orbits in {time.monotonic() - began:.1f}s")
    except Exception:
        print("isotropic_orbit_representatives RAISED", flush=True)
        traceback.print_exc()
        representatives = ()
    for line in representatives[:5]:
        vector = line.inclusion()(line.module_generator(0))
        print("   representative vector square:", vector.q(), "| class:", T.discriminant_class(vector), flush=True)
print("DONE", flush=True)
