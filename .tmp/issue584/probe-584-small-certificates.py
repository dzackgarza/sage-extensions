r"""Probe: the marginal bytes of the edge certificates a returned row holds.

The record of #381 carries the certificate coefficient as arithmetic -- "three
certificates a plane, each retaining a flag and its two transporters" -- and not
as a measurement, because the ``T_Co`` row never returned.  The row *does* return
on ``U + U(2) + <-2>``, so one certificate's own bytes are readable there: this
probe makes the row return, seeds a marginal meter with everything the row
shares (the lattice, the subgroup, the quotient, the two cusp rows), and then
measures each returned certificate's own objects -- the flag and the two
transporters the walk built.
"""
import gc
import os
import sys
import time

START = time.monotonic()
MAXDEPTH = 16


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


class Meter:
    def __init__(self):
        self.seen = set()

    def walk(self, obj, depth=0):
        if depth > MAXDEPTH:
            return 0
        oid = id(obj)
        if oid in self.seen:
            return 0
        self.seen.add(oid)
        total = sys.getsizeof(obj)
        if isinstance(obj, (int, float, bool, str, bytes, complex, type(None), type)):
            return total
        try:
            referents = gc.get_referents(obj)
        except TypeError:
            return total
        for child in referents:
            total += self.walk(child, depth + 1)
        return total


from sage_extensions.all import *  # noqa: F401,F403

lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
print(f"[{time.monotonic() - START:.1f} s] U + U(2) + <-2>, Otilde, rss {rss_mib():.1f} MiB",
      flush=True)
began = time.monotonic()
line_cusps = tuple(subgroup.cusps(1))
plane_cusps = tuple(subgroup.cusps(2))
print(f"[{time.monotonic() - START:.1f} s] the two cusp rows: {len(line_cusps)} lines,"
      f" {len(plane_cusps)} planes ({time.monotonic() - began:.1f} s)",
      flush=True)
began = time.monotonic()
incidences = tuple(subgroup.tits_building_incidence())
print(f"[{time.monotonic() - START:.1f} s] the incidence returned {len(incidences)}"
      f" certificates in {time.monotonic() - began:.1f} s, rss {rss_mib():.1f} MiB",
      flush=True)

meter = Meter()
for shared in (lattice, subgroup, quotient, subgroup.supergroup()):
    meter.walk(shared)
for cusp in (*line_cusps, *plane_cusps):
    meter.walk(cusp)
for cusp in (*line_cusps, *plane_cusps):
    meter.walk(cusp.representative())
shared_count = len(meter.seen)
print(f"  seeded {shared_count} shared objects", flush=True)

sizes = []
for incidence in incidences:
    flag_bytes = meter.walk(incidence.flag())
    line_bytes = meter.walk(incidence.line_transporter())
    plane_bytes = meter.walk(incidence.plane_transporter())
    shell = meter.walk(incidence)
    sizes.append(flag_bytes + line_bytes + plane_bytes + shell)
    print(
        f"  certificate: flag {flag_bytes} B, line transporter {line_bytes} B,"
        f" plane transporter {plane_bytes} B, shell {shell} B  = {sizes[-1]} B",
        flush=True,
    )

mean = sum(sizes) / max(1, len(sizes))
print(
    f"\n[probe] RESULT certificates={len(sizes)} mean_bytes={mean:.0f}"
    f" min_bytes={min(sizes) if sizes else 0} max_bytes={max(sizes) if sizes else 0}"
    f" total_bytes={sum(sizes)} at_three_a_plane={3 * mean:.0f} B",
    flush=True,
)
