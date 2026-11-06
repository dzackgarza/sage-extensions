"""Issue #286 item 3: the smallest lattice whose orbit call reaches _vector_denominator."""
import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

import sage_extensions.categories.isotropic_lifts as isotropic_lifts

START = time.monotonic()
CALLS = []

_original = isotropic_lifts._vector_denominator


def counter(vector, integral_module):
    CALLS.append(int(integral_module.module_rank()))
    return _original(vector, integral_module)


isotropic_lifts._vector_denominator = counter


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


def report(name, lattice):
    global CALLS
    CALLS = []
    began = time.monotonic()
    outcome = "returned"
    try:
        representatives = tuple(lattice.Aut().isotropic_orbit_representatives(1))
        outcome = f"{len(representatives)} orbits"
    except Exception as error:
        outcome = f"RAISED {type(error).__name__}: {str(error)[:90]}"
    elapsed = time.monotonic() - began
    print(
        f"[{time.monotonic() - START:8.1f}s] {name} (rank {lattice.module_rank()}): {outcome} "
        f"in {elapsed:.1f}s | _vector_denominator calls: {len(CALLS)}",
        flush=True,
    )


for name, build in (
    ("U + A1", lambda: Lattices(ZZ)("U") + Lattices(ZZ)("A1")),
    ("U + U + <2>", lambda: Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[2]])),
    ("U + U + U", lambda: Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)("U")),
    ("E8(-2) + U", lambda: Lattices(ZZ)("E8").twist(-2) + Lattices(ZZ)("U")),
):
    try:
        report(name, build())
    except Exception:
        print(f"{name}: construction RAISED", flush=True)
        traceback.print_exc()
print("DONE", flush=True)
