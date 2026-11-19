r"""#381: which in-repo plane route declines at T_Co, and what the other answers."""

import signal
import time

from sage_extensions.all import NamedLattices
from sage_extensions.categories.orthogonal_quotients import (
    _plane_orbit_from_odd_stabilizer,
    _plane_orbit_from_parabolic_stabilizer,
)

START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


class Cap(Exception):
    pass


def cap(signum, frame):
    raise Cap()


signal.signal(signal.SIGALRM, cap)

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
log(f"subgroup: {subgroup}")
signal.alarm(300)
try:
    representatives = lattice.Aut().isotropic_orbit_representatives(2)
    log(f"ambient plane orbits: {representatives.cardinality()}  [{time.perf_counter() - START:.2f}s]")
except Cap:
    log("the ambient plane row did not return inside 300 s")
    representatives = None
finally:
    signal.alarm(0)

if representatives is not None:
    first = representatives.an_element() if hasattr(representatives, "an_element") else tuple(representatives)[0]
    log(f"first representative: {type(first).__name__}")
    for name, route in (
        ("odd stabilizer", _plane_orbit_from_odd_stabilizer),
        ("parabolic stabilizer", _plane_orbit_from_parabolic_stabilizer),
    ):
        start = time.perf_counter()
        signal.alarm(180)
        try:
            value = route(subgroup, first)
            log(f"{name}: {'None (declined)' if value is None else f'{len(tuple(value))} orbits'}  [{time.perf_counter() - start:.2f}s]")
        except Cap:
            log(f"{name}: did not return inside 180 s")
        except Exception as error:
            log(f"{name}: raised {type(error).__name__}: {error}")
        finally:
            signal.alarm(0)
log("done")
