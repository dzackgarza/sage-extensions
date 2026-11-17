r"""Probe: what the kernel plane row retains per plane, and where the bytes sit.

The row is ``subgroup.tits_building_incidence()`` for ``Otilde(T_Co) = ker rho``;
its plane row is ``_plane_orbit_from_parabolic_stabilizer``: the slicing plane's
certified parabolic, the split of its cosets in the finite image, and one
``register_isotropic_lift(transported, splitting, family)`` per representative.
This probe runs exactly that loop over PROBE_PLANES representatives -- the same
first lift, the same iterator, the same calls in the same order -- and records

  * the process's VmRSS after every plane, and
  * with PROBE_METER_EVERY > 0, the marginal bytes of every object the loop
    retains, by a referents walk against a ``seen`` set that persists across the
    metered planes (so an object shared with the row -- the lattice, the parents,
    the categories, the parabolic family, the identity -- is counted once, at the
    plane that first reaches it).

The meter's ``seen`` set is itself memory: one Python integer per object walked,
about 50 bytes each.  Metering every plane would therefore add tens of kilobytes
a plane to the very slope the probe is measuring, which is why PROBE_METER_EVERY
samples instead of covering, and why the headline slopes are taken with the meter
off (PROBE_METER_EVERY=0).

PROBE_MODE=baseline registers exactly as the row does.  PROBE_MODE=noreg makes
the same plane and the same span key and does not register: the two runs on the
same specimens differ by exactly what the call retains.
"""
import gc
import os
import sys
import time

START = time.monotonic()
PLANES = int(os.environ.get("PROBE_PLANES", "10"))
MODE = os.environ.get("PROBE_MODE", "baseline")
MAXDEPTH = int(os.environ.get("PROBE_MAXDEPTH", "14"))
METER_EVERY = int(os.environ.get("PROBE_METER_EVERY", "0"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def stage(label):
    print(f"  [{time.monotonic() - START:9.2f} s] {label}   rss {rss_mib():8.1f} MiB", flush=True)


class Meter:
    r"""Marginal bytes by structure, shared objects counted at their first reach."""

    def __init__(self):
        self.seen = set()
        self.totals = {}
        self.counts = {}
        self.last = []
        self.breakdowns = {}

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

    def measure(self, name, obj, breakdown=False):
        if breakdown:
            parts = {}
            attributes = getattr(obj, "__dict__", None)
            if isinstance(attributes, dict):
                for key in list(attributes):
                    parts[key] = self.walk(attributes[key])
            parts["(the object itself)"] = self.walk(obj)
            size = sum(parts.values())
            self.breakdowns[name] = parts
        else:
            size = self.walk(obj)
        self.totals[name] = self.totals.get(name, 0) + size
        self.counts[name] = self.counts.get(name, 0) + 1
        self.last.append((name, size))
        return size


def inventory(quotient, label):
    lines = []
    for name, value in sorted(quotient.__dict__.items()):
        if isinstance(value, dict):
            lines.append(f"{name} (dict of {len(value)}, {sys.getsizeof(value)} B)")
        elif isinstance(value, (list, tuple, set)):
            lines.append(f"{name} ({type(value).__name__} of {len(value)})")
        else:
            lines.append(f"{name} ({type(value).__name__})")
    print(f"      inventory at {label}: quotient has {len(quotient.__dict__)} attributes: "
          + ", ".join(lines), flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first_vector = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first_vector, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
ambient = subgroup.supergroup()
stage(f"T_Co, Otilde(T_Co), its quotient: mode {MODE}, meter every {METER_EVERY}")

print(f"[probe] the slicing plane is parabolic complete: {plane.is_parabolic_complete()}", flush=True)
family = tuple(plane.parabolic_stabilizer_generators())
stage(f"the plane's certified parabolic: {len(family)} generators")
print(f"[probe] tuple(family) is family: {tuple(family) is family}", flush=True)

meter = Meter()
if METER_EVERY:
    seed_before = time.monotonic()
    for shared in (lattice, subgroup, quotient, ambient, quotient._discriminant_group, plane, *family):
        meter.walk(shared)
    stage(f"meter seeded over the row's shared objects ({len(meter.seen)} objects,"
          f" {time.monotonic() - seed_before:.1f} s)")

splittings = quotient._iter_splitting_isometries_in_im_rho(family)
carried = next(splittings)
stage("the split's first lift (the finite image's whole coset walk)")

samples = []
plane_bytes = []
plane_numbers = []
planes = []
for position in range(PLANES):
    splitting = carried if position == 0 else next(splittings)
    transported = splitting.transport_isotropic_object(plane)
    span = _span_key(transported)
    metered = METER_EVERY and (position % METER_EVERY == 0)
    if metered:
        meter.last = []
        sampled = True
        meter.measure("transported plane", transported, breakdown=sampled)
        meter.measure("span key", span)
    if MODE == "baseline":
        quotient.register_isotropic_lift(transported, splitting, family)
        if metered:
            registry = quotient.__dict__["_isotropic_lift_registry"]
            key = next(reversed(registry))
            value = registry[key]
            assert key == span, "the registry key is not the span this plane was registered under"
            meter.measure("registry entry key", key)
            meter.measure("family tuple", value[1])
            meter.measure("lift", value[0], breakdown=True)
            meter.measure("registry entry shell", value)
    planes.append(transported)
    samples.append(rss_mib())
    if metered:
        plane_bytes.append(sum(size for _name, size in meter.last))
        plane_numbers.append(position + 1)
    if position < 3 or (position + 1) % max(1, PLANES // 10) == 0 or position + 1 == PLANES:
        print(f"  [plane {position + 1:6d}/{PLANES}] rss {samples[-1]:8.1f} MiB"
              + (f"  marginal {plane_bytes[-1]:7d} B"
                 f"  ({', '.join(f'{name} {size}' for name, size in meter.last)})" if metered else ""),
              flush=True)

stage(f"the plane row's first {len(planes)} planes")

if METER_EVERY:
    print("\n[attribution] marginal bytes by structure over the metered planes", flush=True)
    total = 0
    for name, size in sorted(meter.totals.items()):
        print(f"  {name:22s} {size:12d} B over {meter.counts[name]:5d} objects"
              f" = {size / max(1, len(plane_numbers)):9.1f} B a metered plane", flush=True)
        total += size
    print(f"  {'total':22s} {total:12d} B = {total / max(1, len(plane_numbers)):.1f} B a plane",
          flush=True)
    for named, parts in meter.breakdowns.items():
        print(f"  the {named}'s marginal, by its own attribute: "
              + ", ".join(f"{key} {size}" for key, size in sorted(parts.items())), flush=True)
    inventory(quotient, "the end")

band = max(1, PLANES // 10)
print("\n[slope] rss, per band of planes", flush=True)
for end in range(band, PLANES + 1, band):
    steps = band
    print(f"  planes {end - steps + 1:6d}..{end:6d}:"
          f" {1000 * (samples[end - 1] - samples[end - 1 - steps]) / steps:8.1f} KB a plane",
          flush=True)

print(
    f"\n[probe] RESULT mode={MODE} planes={len(planes)} wall={time.monotonic() - START:.1f} s"
    f" rss={rss_mib():.1f} MiB after_first_lift={samples[0]:.1f} MiB last_rss={samples[-1]:.1f} MiB"
    f" growth_per_plane_bytes={1024 * 1024 * (samples[-1] - samples[0]) / max(1, len(planes) - 1):.0f}"
    f" lifts_retained={len(quotient.__dict__.get('_isotropic_lift_registry', {}))}",
    flush=True,
)
