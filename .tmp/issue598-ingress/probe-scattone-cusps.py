r"""Probe: the Scattone plane cusp rows -- their build, their admission, and one equality question.

`6JRX` and `6JRY` are the two rank-21 cards whose plane orbit rows the gate
already reads (nine orbits for `6JRY` under `O`), so their ambient cusp rows are
the largest cusp rows this host can build inside a test call.  What the probe
prices is what the admission adds to the build.  Nothing is asserted.
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
    print(f"[{perf_counter() - START:9.1f} s rss {rss_mib():8.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403


def card_lattice(k):
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)([[-2 * k]])
    )


for tag, k, kind in (("6JRX", 1, "O"), ("6JRY", 2, "O")):
    lattice = card_lattice(k)
    group = lattice.O()
    say(f"--- {tag}: rank {lattice.module_rank()}, the card's O plane row")

    t = perf_counter()
    representatives = tuple(group.isotropic_orbit_representatives(2))
    build = perf_counter() - t
    say(f"    isotropic_orbit_representatives(2) = {len(representatives)} in {build:.3f} s")

    t = perf_counter()
    row = group.cusps(2)
    whole = perf_counter() - t
    say(f"    cusps(2) = {row.cardinality()} in {whole:.3f} s  (the admission: {whole - build:.3f} s)")

    points = tuple(row)
    if len(points) >= 2:
        t = perf_counter()
        decided = points[0] == points[1]
        question = perf_counter() - t
        count = len(points)
        say(
            f"    one inequality question: {1e3 * question:.3f} ms, equal={decided};"
            f" the ingress's {count * (count - 1) // 2} of them: {count * (count - 1) / 2 * question:.1f} s"
        )
    for position, cusp in enumerate(points):
        plane = cusp.representative()
        say(
            f"    cusp {position}: rank {plane.module_rank()} primitive"
            f" {plane.is_primitive()} isotropic {plane.is_totally_isotropic()}"
            f" in its cusp {plane in cusp} at {row.enumeration_inverse()(cusp)}"
        )

say("done")
