r"""Probe: O(L) plane rows of the medium lattices, and what one of their equality questions costs.

The full orthogonal group's cusp keeps a representative and its equality is the
port's transporter search, so a row of k orbits asks k(k-1)/2 searches at
admission.  Nothing is asserted.
"""

import os
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
U2 = U.twist(2)
M2 = Lattices(ZZ)([[2]])

CANDIDATES = {
    "U+U(2)+<-2,-2,-2>": U + U2 + Lattices(ZZ)([[-2, 0, 0], [0, -2, 0], [0, 0, -2]]),
    "U+U+<-2,-2,-2>": U + U + Lattices(ZZ)([[-2, 0, 0], [0, -2, 0], [0, 0, -2]]),
    "U(2)+E8(-2)": U2 + Lattices(ZZ)("E8").twist(-2),
    "TEn": NamedLattices.TEn,
}

for name, lattice in CANDIDATES.items():
    say(f"--- {name}: rank {lattice.module_rank()}")
    group = lattice.O()
    for rank in (1, 2):
        t = perf_counter()
        representatives = tuple(group.isotropic_orbit_representatives(rank))
        walk = perf_counter() - t
        say(f"    isotropic_orbit_representatives({rank}) = {len(representatives)} in {walk:.3f} s")
        if len(representatives) >= 2:
            t = perf_counter()
            row = group.cusps(rank)
            say(f"    cusps({rank}) = {row.cardinality()} in {perf_counter() - t:.3f} s")
            points = tuple(row)
            t = perf_counter()
            decided = points[0] == points[1]
            says = perf_counter() - t
            say(f"    one inequality question: {1e3 * says:.1f} ms, equal={decided}")
            count = len(points)
            say(
                f"    the ingress's {count * (count - 1) // 2} questions at that price:"
                f" {count * (count - 1) / 2 * says:.1f} s"
            )

say("done")
