"""Issue #286 item 1: the orbit search with the guard set from the sandbox's headroom."""
import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


import sage_indefinite_port

stage(f"port: {sage_indefinite_port.__file__}")
T = NamedLattices.Tco
O = T.Aut()

began = time.monotonic()
generators = tuple(O.group_generators())
stage(f"O(T_Co).group_generators(): {len(generators)} in {time.monotonic() - began:.1f}s")

began = time.monotonic()
try:
    representatives = tuple(O.isotropic_orbit_representatives(1))
    elapsed = time.monotonic() - began
    stage(f"isotropic_orbit_representatives(1): {len(representatives)} orbits in {elapsed:.1f}s")
    vectors = tuple(line.inclusion()(line.module_generator(0)) for line in representatives)
    stage(f"vectors read: {len(vectors)}")
    assert all(vector.q() == 0 for vector in vectors), "a representative is not isotropic"
    assert all(vector.is_primitive() is True for vector in vectors), "a representative is not primitive"
    stage("every representative is primitive and isotropic")
    classes = tuple(T.discriminant_class(vector) for vector in vectors)
    stage(f"classes read: {len(tuple(set(classes)))} distinct")
except Exception:
    print(f"RAISED after {time.monotonic() - began:.1f}s", flush=True)
    traceback.print_exc()
print("DONE", flush=True)
