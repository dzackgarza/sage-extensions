r"""Probe: whole cusp rows of the small lattices, printed element by element.

Two runs of this file -- one at the commit before the ingress repair and one
after it -- are diffed: the row's cardinality, and the span of every cusp in
the row's own order, which is the plane each cusp names.  Nothing is asserted;
the diff is the comparison.
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


from sage_extensions.categories.isotropic_orbits import _span_key


def _named(cusp):
    r"""The plane or line a cusp names, by the exact span key of its representative.

    A cusp of an arithmetic subgroup keeps its span; a cusp of the full
    orthogonal group keeps a representative.  ``_span_key`` names the
    sublattice either one names, as the row Hermite form of its generators.
    """
    span = getattr(cusp, "span", None)
    if span is not None:
        return span()[1]
    return _span_key(cusp.representative())[1]


U = Lattices(ZZ)("U")
U2 = U.twist(2)

CANDIDATES = {
    "6JRS": U + U + Lattices(ZZ)([[-2]]),
    "U+U(2)+<-2>": U + U2 + Lattices(ZZ)([[-2]]),
    "U+U(2)+<-4>": U + U2 + Lattices(ZZ)([[-4]]),
    "E10": NamedLattices.E10,
}

for name, lattice in CANDIDATES.items():
    for kind, group in (
        ("O(L)", lattice.O()),
        ("Otilde(L)", lattice.stable_orthogonal_group()),
    ):
        say(f"--- {name}: {kind}")
        for rank in (1, 2):
            t = perf_counter()
            row = group.cusps(rank)
            seconds = perf_counter() - t
            points = tuple(row)
            say(f"    cusps({rank}) = {row.cardinality()} in {seconds:.3f} s")
            for position, cusp in enumerate(points):
                print(f"    {kind} rank {rank} cusp {position}: {_named(cusp)}", flush=True)
            print(f"    {kind} rank {rank} positions: {[row.enumeration_inverse()(cusp) for cusp in points]}", flush=True)
            print(f"    {kind} rank {rank} membership: {[cusp in row for cusp in points]}  membership_of_rank", flush=True)

say("done")
