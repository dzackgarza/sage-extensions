r"""Probe: which small lattices give a plane cusp row large enough to price.

For each candidate lattice the probe times the cusp rows and one cusp equality
question, and reports the row's cardinality.  Nothing is asserted.
"""

import os
import time
from time import perf_counter

START = perf_counter()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[{perf_counter() - START:8.1f} s rss {rss_mib():7.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403

U = Lattices(ZZ)("U")


def candidates():
    yield "6JRS = U+U+<-2>", U + U + Lattices(ZZ)([[-2]])
    yield "U+U(2)+<-2>", U + U.twist(2) + Lattices(ZZ)([[-2]])
    yield "U+U(2)+<-4>", U + U.twist(2) + Lattices(ZZ)([[-4]])
    yield "TEn = U+E8(-2)", NamedLattices.TEn


for name, lattice in candidates():
    say(f"--- {name}: rank {lattice.module_rank()}")
    try:
        subgroup = lattice.stable_orthogonal_group()
        say(f"    the full orthogonal group of {name}")
        for rank in (1, 2):
            t = perf_counter()
            row = subgroup.cusps(rank)
            say(f"    cusps({rank}) = {row.cardinality()} in {perf_counter() - t:.3f} s")
            points = tuple(row)
            if len(points) >= 2:
                t = perf_counter()
                decided = points[0] == points[1]
                say(
                    f"    one equality question between two rank-{rank} cusps:"
                    f" {1e3 * (perf_counter() - t):.3f} ms, equal={decided}"
                )
    except Exception as failure:  # noqa: BLE001 - the probe reports, it does not decide
        say(f"    !! {type(failure).__name__}: {failure}")

say("done")
