r"""Probe: `Otilde(T_Co)`'s line cusp row -- its length, its walk, and the ingress.

The plane row is 189720 cusps and its walk materializes a 174 s transversal, so
the line row is the only row of this lattice small enough to be measured whole.
Nothing is asserted.
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
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
say("Otilde(T_Co)")

t = perf_counter()
row = subgroup.cusps(1)
say(f"cusps(1) = {row.cardinality()} in {perf_counter() - t:.3f} s")
points = tuple(row)
say(f"the row read out: {len(points)} cusps")

if len(points) >= 2:
    t = perf_counter()
    decided = points[0] == points[1]
    say(f"one inequality question between two line cusps: {1e3 * (perf_counter() - t):.3f} ms, equal={decided}")

for count in (20, 40, 80):
    if count > len(points):
        continue
    t = perf_counter()
    distinct = tuple(dict.fromkeys(points[:count]))
    seconds = perf_counter() - t
    say(
        f"the literal ingress over {count} cusps: {seconds:.3f} s"
        f"  ({1e6 * seconds / (count * (count - 1) / 2):.1f} us a comparison), {len(distinct)} distinct"
    )

say("done")
