"""#541: the Otilde(T_Co) plane row to its first plane, with a load calibration.

Runs `NamedLattices.Tco.stable_orthogonal_group().isotropic_orbit_representatives(2)`
and counts every plane the walk transports.  Three things make two runs of two
trees comparable:

* `calib=` -- the wall time of a fixed workload (300000 integer additions and one
  GAP `Order(SymmetricGroup(8))`), timed first in the same process, because this
  VM is shared and its load decided earlier readings (a `group` stage measured
  1.81 s at load 1.0 and 6.36 s at 11.6).
* the count is written to a file after every transport, so a kill cannot lose it;
* `faulthandler` dumps the stack at the deadline even if a GIL-holding GAP call
  starves the watchdog thread, so the stage the row is in is named, not guessed.

A watchdog prints the count every 30 s and leaves at the deadline.
"""
import faulthandler
import os
import sys
import threading
import time

START = time.perf_counter()
DEADLINE = float(os.environ.get("ROW_DEADLINE", "500"))
PROGRESS = os.environ.get("ROW_PROGRESS", "/repos/sage-extensions/.tmp/plane-count.txt")

from sage.libs.gap.libgap import libgap  # noqa: E402

from sage_extensions.all import *  # noqa: E402
from sage_extensions.categories.lattice_morphisms import LatticeIsometryMethods  # noqa: E402


CALIBRATION_WORK = 10000000


def calibration():
    """The fixed workload: Python integers and one GAP call, about 0.25 s idle."""
    began = time.perf_counter()
    total = 0
    for value in range(CALIBRATION_WORK):
        total += value * value * value
    libgap.Order(libgap.SymmetricGroup(8))
    return total and (time.perf_counter() - began)


libgap.Order(libgap.SymmetricGroup(8))  # warm up the interface, untimed
CALIB = {"start": calibration()}

counter = {"planes": 0, "first": None, "last": None}
lock = threading.Lock()
original = LatticeIsometryMethods.transport_isotropic_object


def counting(self, obj):
    began = time.perf_counter()
    result = original(self, obj)
    with lock:
        counter["planes"] += 1
        if counter["first"] is None:
            counter["first"] = began - START
        counter["last"] = time.perf_counter() - START
        state = dict(counter)
    try:
        with open(PROGRESS, "w") as handle:
            handle.write(f"{state['planes']} {state['first']} {state['last']}\n")
    except OSError:
        pass
    return result


LatticeIsometryMethods.transport_isotropic_object = counting


def report(prefix):
    elapsed = time.perf_counter() - START
    with lock:
        planes, first, last = counter["planes"], counter["first"], counter["last"]
    print(f"{prefix} elapsed {elapsed:.1f} s, planes transported {planes}", flush=True)
    if first is None:
        print(f"{prefix} no plane transported yet", flush=True)
        return
    print(f"{prefix} first plane at {first:.1f} s, last at {last:.1f} s", flush=True)
    window = last - first
    if window > 0 and planes > 1:
        print(f"{prefix} {(planes - 1) / window:.2f} planes/s over the walk "
              f"({1e3 * window / (planes - 1):.1f} ms a plane)", flush=True)


def watchdog():
    while True:
        time.sleep(30)
        report("  [tick]")
        if time.perf_counter() - START > DEADLINE:
            report("[cap]")
            print(f"[cap] calibration start {CALIB['start']:.3f} s", flush=True)
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)


faulthandler.dump_traceback_later(120, repeat=True, file=sys.stdout)
threading.Thread(target=watchdog, daemon=True).start()

lattice = NamedLattices.Tco
group = lattice.stable_orthogonal_group()
print(f"row: {group} on rank {int(lattice.module_rank())}", flush=True)
print(f"calibration {CALIB['start']:.3f} s", flush=True)
report("before the row")
planes = group.isotropic_orbit_representatives(2)
report("after the row")
print(f"calibration end {calibration():.3f} s", flush=True)
print(f"row returned {planes.cardinality()} representatives", flush=True)
print(f"RESULT calib={CALIB['start']:.3f} planes={counter['planes']} "
      f"first={counter['first']}", flush=True)
