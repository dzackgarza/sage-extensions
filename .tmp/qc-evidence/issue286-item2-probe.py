"""Issue #286 item 2: what the orbit search retains, by allocation site."""
import os
import threading
import time
import tracemalloc

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


import sage_indefinite_port

stage(f"port: {sage_indefinite_port.__file__}")
T = NamedLattices.Tco
O = T.Aut()

generators = tuple(O.group_generators())
stage(f"O(T_Co).group_generators(): {len(generators)} in {time.monotonic() - START:.1f}s")

# Tracing starts here: the growth to attribute is the search's, and tracing the
# generator call as well only triples its cost without changing the question.
tracemalloc.start(25)
first = tracemalloc.take_snapshot()
stage("snapshot 1 taken")

result = {}


def search():
    try:
        result["value"] = tuple(O.isotropic_orbit_representatives(1))
    except BaseException as error:  # noqa: BLE001 - reported, not handled
        result["error"] = repr(error)


worker = threading.Thread(target=search, daemon=True)
worker.start()
stage("orbit search started in a worker thread")

time.sleep(90)
second = tracemalloc.take_snapshot()
stage("snapshot 2 taken, 90 s later")

statistics = second.compare_to(first, "traceback")
print("=== top ten allocation sites by size difference ===", flush=True)
for index, statistic in enumerate(statistics[:10]):
    print(f"--- {index + 1}: {statistic.size_diff / 2**20:.1f} MiB, {statistic.count_diff} blocks, traceback:", flush=True)
    for line in statistic.traceback.format()[-8:]:
        print("   ", line, flush=True)
print(f"orbit search finished during the sample: {'value' in result or 'error' in result}", flush=True)
if "value" in result:
    print("orbits:", len(result["value"]), flush=True)
if "error" in result:
    print("error:", result["error"], flush=True)
print("DONE", flush=True)
os._exit(0)
