r"""Probe: the per-plane retention of the registered lift, on the fast specimen.

The row's own plane row (:mod:`probe-584-retention`) needs the finite image's
whole coset walk before its first plane -- about four minutes a slice.  The
retention it measures does not need that walk: any distinct primitive isotropic
planes of ``T_Co`` with one registered lift each reproduce it, and the isometries
of the ambient orthogonal group's own generating family are words in the row's
own generators.  So this probe registers PROBE_PLANES planes carried by ambient
words -- the same ``register_isotropic_lift`` calls, the same family, the same
plane -- and measures the resident set and the marginal bytes of every structure
per plane.

PROBE_MODE=baseline registers; PROBE_MODE=noreg makes the same plane, the same
span key and the same call shape but does not register.  The two runs differ by
exactly what the registry holds.
"""
import gc
import os
import random
import sys
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "1000"))
MODE = os.environ.get("PROBE_MODE", "baseline")
MAXDEPTH = int(os.environ.get("PROBE_MAXDEPTH", "14"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


class Meter:
    def __init__(self):
        self.seen = set()
        self.totals = {}
        self.counts = {}
        self.last = []

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

    def measure(self, name, obj):
        size = self.walk(obj)
        self.totals[name] = self.totals.get(name, 0) + size
        self.counts[name] = self.counts.get(name, 0) + 1
        self.last.append((name, size))
        return size


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
ambient = subgroup.supergroup()
family = tuple(plane.parabolic_stabilizer_generators())
print(f"[{time.monotonic() - START:.1f} s] row objects, {len(family)} generators,"
      f" mode {MODE}, rss {rss_mib():.1f} MiB", flush=True)
quotient.register_isotropic_lift(plane, ambient.one(), family)

meter = Meter()
for shared in (lattice, subgroup, quotient, ambient, quotient._discriminant_group, plane, *family,
               *tuple(ambient.group_generators())):
    meter.walk(shared)
print(f"  meter seeded over {len(meter.seen)} shared objects", flush=True)

generators = tuple(ambient.group_generators())
random.seed(584)
candidates = []
for generator in generators[:24]:
    lift = generator
    for _power in range(60):
        candidates.append(lift)
        lift = generator * lift
for _word in range(4 * PLANES):
    lift = generators[random.randrange(len(generators))]
    for _step in range(random.randrange(0, 3)):
        lift = generators[random.randrange(len(generators))] * lift
    candidates.append(lift)
print(f"  {len(generators)} ambient generators, {len(candidates)} candidate isometries",
      flush=True)

seen = {_span_key(plane)}
base_rss = rss_mib()
samples = []
marginals = []
planes = []
attempted = 0
for lift in candidates:
    if len(planes) >= PLANES:
        break
    attempted += 1
    target = lift.transport_isotropic_object(plane)
    span = _span_key(target)
    if span in seen:
        continue
    seen.add(span)
    meter.last = []
    meter.measure("transported plane", target)
    if MODE == "baseline":
        quotient.register_isotropic_lift(target, lift, family)
        registry = quotient.__dict__["_isotropic_lift_registry"]
        key = next(reversed(registry))
        assert key == span
        meter.measure("registry entry key", key)
        meter.measure("registry entry shell", registry[key])
        meter.measure("family tuple", registry[key][1])
        meter.measure("lift", registry[key][0])
    planes.append(target)
    samples.append(rss_mib())
    marginals.append(sum(size for _name, size in meter.last))
    if len(planes) % max(1, PLANES // 10) == 0:
        print(
            f"  [{len(planes):6d}/{PLANES}] rss {samples[-1]:8.1f} MiB"
            f" ({1000 * (samples[-1] - base_rss) / len(planes):7.1f} KB a plane)"
            f"  marginal {marginals[-1]:7d} B",
            flush=True,
        )

count = len(planes)
total = sum(meter.totals.values())
print(f"\n[attribution] marginal bytes by structure over {count} planes", flush=True)
for name, size in sorted(meter.totals.items()):
    print(f"  {name:22s} {size:12d} B over {meter.counts[name]:6d} objects"
          f" = {size / max(1, count):9.1f} B a plane", flush=True)
print(f"  {'total':22s} {total:12d} B = {total / max(1, count):.1f} B a plane", flush=True)

band = max(1, count // 10)
print("\n[slope] every band", flush=True)
for start in range(band - 1, count, band):
    steps = min(band, start + 1)
    if start - steps + 1 < 0:
        continue
    print(
        f"  planes {start + 1 - steps:6d}..{start + 1:6d}:"
        f" {1000 * (samples[start] - samples[start - steps]) / steps:7.1f} KB a plane rss;"
        f" {sum(marginals[start - steps + 1:start + 1]) / steps:9.0f} B marginal",
        flush=True,
    )

print(
    f"\n[probe] RESULT mode={MODE} planes={count} candidates_used={attempted}"
    f" wall={time.monotonic() - START:.1f} s rss={rss_mib():.1f} MiB"
    f" base_rss={base_rss:.1f} MiB growth_per_plane_bytes="
    f"{1024 * 1024 * (samples[-1] - base_rss) / max(1, count):.0f}"
    f" marginal_per_plane_bytes={total / max(1, count):.0f}"
    f" lifts_retained={len(quotient.__dict__.get('_isotropic_lift_registry', {}))}",
    flush=True,
)
