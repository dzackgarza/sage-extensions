r"""Probe: the kernel plane rows of the T_Co family with a smaller E-block.

`T_Co = <2> + U(2) + E8(-2)` has 189720 plane cusps and a 174 s transversal.
Replacing the E8 block by E7 or E6 shrinks the character image, so the row is
smaller and the transversal cheaper.  Nothing is asserted.
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


def scaled(block_name):
    return Lattices(ZZ)(block_name).twist(-2)


for name in ("E7", "E6"):
    lattice = M2 + U2 + scaled(name)
    say(f"--- <2> + U(2) + {name}(-2): rank {lattice.module_rank()}, |A_L| = {lattice.discriminant_group().cardinality()}")
    subgroup = lattice.stable_orthogonal_group()
    say("    the stable orthogonal group")
    quotient = subgroup.finite_character_quotient()
    say(f"    |im rho| = {quotient.image_order()}")
    for rank in (1, 2):
        t = perf_counter()
        row = subgroup.cusps(rank)
        elapsed = perf_counter() - t
        say(f"    cusps({rank}) = {row.cardinality()} in {elapsed:.3f} s")
        points = tuple(row)
        if len(points) >= 2:
            t = perf_counter()
            decided = points[0] == points[1]
            say(f"    one inequality question, rank {rank}: {1e3 * (perf_counter() - t):.3f} ms, equal={decided}")

say("done")
