r"""Probe: how big is a congruence subgroup's cusp row, and what does one equality cost?

Nothing is asserted; the probe reports counts and times so that a row large
enough to price the ingress can be chosen.
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

for name, lattice, level in (
    ("2U", U + U, 3),
    ("U+U(2)+<-2>", U + U.twist(2) + Lattices(ZZ)([[-2]]), 2),
):
    say(f"--- {name}, Gamma({level})")
    group = lattice.O()
    gamma = group.congruence_preimage(level)
    say(f"    the congruence subgroup")
    for rank in (1, 2):
        t = perf_counter()
        row = gamma.cusps(rank)
        say(f"    cusps({rank}) = {row.cardinality()} in {perf_counter() - t:.3f} s")
        points = tuple(row)
        if len(points) >= 2:
            t = perf_counter()
            decided = points[0] == points[1]
            say(
                f"    one inequality question, rank {rank}:"
                f" {1e3 * (perf_counter() - t):.3f} ms, equal={decided}"
            )

say("done")
