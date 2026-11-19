r"""#381: the first line's K_v line-orbit enumeration at T_Co, capped."""

import signal
import time

from sage_extensions.all import NamedLattices, ZZ
from sage_extensions.categories.isotropic_orbits import _planes_through_line

START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


class Cap(Exception):
    pass


def cap(signum, frame):
    raise Cap()


signal.signal(signal.SIGALRM, cap)

lattice = NamedLattices.Tco
signal.alarm(300)
try:
    representatives = lattice.Aut().isotropic_orbit_representatives(1)
    log(f"line representatives of L: {representatives.cardinality()}  [{time.perf_counter() - START:.2f}s]")
    first = representatives.an_element() if hasattr(representatives, "an_element") else tuple(representatives)[0]
    log(f"first representative: {first}")
    line = lattice.primitive_isotropic_subobject(
        first.inclusion()(first.module_generator(first.module_generating_set()[0]))
    )
    reduction = line.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    log(f"K_v: rank {quotient.module_rank()}, signature {quotient.signature()}, disc {quotient.discriminant()}")
    start = time.perf_counter()
    signal.alarm(300)
    try:
        orbits = quotient.Aut().isotropic_orbit_representatives(1)
        log(f"K_v line orbits: {orbits.cardinality()}  [{time.perf_counter() - start:.2f}s]")
    except Cap:
        log(f"K_v line orbits: did not return inside 300 s  [{time.perf_counter() - start:.2f}s]")
    finally:
        signal.alarm(0)
    start = time.perf_counter()
    signal.alarm(300)
    try:
        planes = _planes_through_line(lattice.Aut(), line, None)
        log(f"planes through the first line: {len(tuple(planes))}  [{time.perf_counter() - start:.2f}s]")
    except Cap:
        log(f"planes through the first line: did not return inside 300 s  [{time.perf_counter() - start:.2f}s]")
    finally:
        signal.alarm(0)
except Cap:
    log("line representatives themselves did not return inside 300 s")
finally:
    signal.alarm(0)
log("done")
