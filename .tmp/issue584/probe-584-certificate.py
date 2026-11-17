r"""Probe: the marginal bytes of one edge certificate of the kernel row's walk.

The record of the row (``results/issue381-the-incidence-holds.md``) carries the
certificate coefficient as arithmetic -- "three certificates a plane, each
retaining a flag and its two transporters" -- and not as a measurement.  This
probe makes one certificate of ``Otilde(T_Co)`` on the same objects the walk
makes it on and measures what it retains: the flag, the two cusp vertices (which
the walk shares with the two cusp rows), and the two transporters.
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
from sage_extensions.categories.isotropic_orbits import (
    ArithmeticCuspIncidence,
    FlagType,
    _arithmetic_cusp,
)

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
identity = subgroup.supergroup().one()
print(f"[{time.monotonic() - START:.1f} s] row objects, rss {rss_mib():.1f} MiB", flush=True)

inclusion = plane.inclusion()
domain = inclusion.domain()
basis = tuple(inclusion(domain.module_generator(label)) for label in domain.module_generating_set())
flag = lattice.isotropic_flag(basis[0], basis[1], flag_type=FlagType((1, 2)))
line, flag_plane = flag.terms()
print(f"  flag: line rank {line.module_rank()}, plane rank {flag_plane.module_rank()}", flush=True)
line_cusp = _arithmetic_cusp(subgroup, line)
plane_cusp = _arithmetic_cusp(subgroup, plane)
print(f"[{time.monotonic() - START:.1f} s] two cusps, rss {rss_mib():.1f} MiB", flush=True)

certificate = ArithmeticCuspIncidence(
    subgroup, flag, line_cusp, plane_cusp, identity, identity
)
print(f"[{time.monotonic() - START:.1f} s] one certificate made, rss {rss_mib():.1f} MiB", flush=True)

meter = Meter()
for shared in (lattice, subgroup, quotient, subgroup.supergroup(), plane, line_cusp, plane_cusp, identity):
    meter.walk(shared)
seeded = len(meter.seen)
flag_bytes = meter.walk(certificate.flag())
line_bytes = meter.walk(certificate.line_transporter())
plane_bytes = meter.walk(certificate.plane_transporter())
total = meter.walk(certificate)
print(
    f"\n[probe] RESULT certificate_marginal_bytes={flag_bytes + line_bytes + plane_bytes + total}"
    f" (flag {flag_bytes}, line transporter {line_bytes}, plane transporter {plane_bytes},"
    f" shell {total}), shared objects seeded {seeded}",
    flush=True,
)
print(
    f"[probe] at three certificates a plane and 189720 planes:"
    f" {3 * (flag_bytes + line_bytes + plane_bytes + total) * 189720 / 2**30:.2f} GiB",
    flush=True,
)
