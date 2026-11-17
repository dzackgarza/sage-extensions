r"""Probe: which small lattice and finite-index subgroup gives a large plane row cheaply.

For each candidate the probe reports |A_L|, the index of the kernel of the
discriminant representation, and the plane cusp row's cardinality and build
time.  Nothing is asserted.
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
D2 = Lattices(ZZ)([[-2, 0], [0, -2]])
D3 = Lattices(ZZ)([[-2, 0, 0], [0, -2, 0], [0, 0, -2]])

CANDIDATES = {
    "U+U2+<-2,-2>": U + U2 + D2,
    "U+U+<-2,-2>": U + U + D2,
    "U+U2+<-2,-2,-2>": U + U2 + D3,
    "U+U+<-2,-2,-2>": U + U + D3,
}

for name, lattice in CANDIDATES.items():
    say(f"--- {name}: rank {lattice.module_rank()}")
    discriminant = lattice.discriminant_group()
    say(f"    |A_L| = {discriminant.cardinality()}  (order {int(discriminant.cardinality().finite_value())})")
    group = lattice.O()
    say("    the full orthogonal group O(L)")
    ambient_target = discriminant.orthogonal_group()
    kernel = group.discriminant_preimage(ambient_target.trivial_subgroup())
    say("    the kernel of the discriminant representation")
    for rank in (2,):
        t = perf_counter()
        row = kernel.cusps(rank)
        elapsed = perf_counter() - t
        say(f"    the kernel's cusps({rank}) = {row.cardinality()} in {elapsed:.3f} s")
        t2 = perf_counter()
        ambient_row = group.cusps(rank)
        say(f"    O(L)'s cusps({rank}) = {ambient_row.cardinality()} in {perf_counter() - t2:.3f} s")

say("done")
