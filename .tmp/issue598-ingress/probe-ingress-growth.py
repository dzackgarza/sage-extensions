r"""Probe: the cusp row's build against its length, through the repaired admission.

The route's iterator materializes the whole 189720-plane row before it yields,
so no slice of the row exists; what is timed here is exactly what `cusps(2)`
does, one plane at a time, and then the admission the row ends with
(``_distinct_finite_ordered_set``, the call `cusps` makes).

Per plane: the split's walk draw, one transport and lift registration, one span
key and cusp, and the route's own finite action.  Then the admission, whole,
and the old literal ingress over a small prefix for its per-comparison
constant.  Nothing is asserted.
"""

import os
from time import perf_counter

START = perf_counter()
PLANES = int(os.environ.get("PROBE_PLANES", "1000"))
BAND = int(os.environ.get("PROBE_BAND", "100"))
PREFIXES = tuple(int(entry) for entry in os.environ.get("PROBE_PREFIXES", "20,40,80").split(","))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[{perf_counter() - START:9.1f} s rss {rss_mib():8.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
from sage_extensions.categories.orthogonal_quotients import (
    _composite_divided_class_action,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    _distinct_finite_ordered_set,
    finite_ordered_set,
)

lattice = NamedLattices.Tco
labels = tuple(lattice.module_generating_set())
names = {str(label): lattice.module_generator(label) for label in labels}
first_vector = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
source = lattice.primitive_isotropic_subobject(first_vector, names["ep"])
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
family = tuple(source.parabolic_stabilizer_generators())
say(f"T_Co rank {lattice.module_rank()}, Otilde(T_Co), {len(family)} parabolic generators")

identity_element = quotient._discriminant_group.one()
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
t = perf_counter()
lift, element = next(splittings)
walk = perf_counter() - t
quotient.register_isotropic_lift(source, quotient.supergroup.one(), family, identity_element)
say(f"the split's first lift (the finite image's whole coset walk) {walk:.1f} s")

t = perf_counter()
row = [_arithmetic_cusp(subgroup, source)]
say(f"the source plane's own cusp {1e3 * (perf_counter() - t):.3f} ms")

nexts, transports, cusps_time, carries = [], [], [], []
for position in range(1, PLANES):
    t = perf_counter()
    lift, element = next(splittings)
    nexts.append(perf_counter() - t)

    t = perf_counter()
    transported = lift.transport_isotropic_object(source)
    quotient.register_isotropic_lift(transported, lift, family, element)
    transports.append(perf_counter() - t)

    t = perf_counter()
    row.append(_arithmetic_cusp(subgroup, transported))
    cusps_time.append(perf_counter() - t)
    del transported

    t = perf_counter()
    _composite_divided_class_action(quotient, element, identity_element)
    carries.append(perf_counter() - t)

    if position < 3 or (position + 1) % max(1, PLANES // 10) == 0:
        say(f"plane {position + 1}/{PLANES}")
say(f"the row's {len(row)} planes, shape cusps")


def band(values, count, label):
    if len(values) < 2 * count:
        count = max(1, len(values) // 2)
    head = values[:count]
    tail = values[-count:]
    print(
        f"  {label:24s} first {len(head):7d}: {1e3 * sum(head) / len(head):9.3f} ms a plane"
        f"   last {len(tail):7d}: {1e3 * sum(tail) / len(tail):9.3f} ms a plane"
        f"   all: {1e3 * sum(values) / len(values):9.3f} ms",
        flush=True,
    )


print("\n[per-plane stages]", flush=True)
band(nexts, BAND, "the split's walk")
band(transports, BAND, "transport and lift reg")
band(cusps_time, BAND, "the cusp (span key)")
band(carries, BAND, "the finite action")
totals = [a + b + c + d for a, b, c, d in zip(nexts, transports, cusps_time, carries, strict=True)]
band(totals, BAND, "the plane, all stages")
build = walk + sum(totals)
say(f"the row built: {build:.1f} s ({1e6 * build / len(row):.0f} us a plane, the walk included)")

print("\n[the admission the row ends with: _distinct_finite_ordered_set]", flush=True)
t = perf_counter()
admitted = _distinct_finite_ordered_set(row)
ingress = perf_counter() - t
say(
    f"admitted {int(admitted.cardinality().finite_value())} cusps in {ingress:.3f} s"
    f"  ({1e6 * ingress / len(row):.2f} us a plane)"
)
positions = [admitted.index_of(cusp) for cusp in row]
say(
    f"each cusp's own position: the first {positions[0]}, the last {positions[-1]},"
    f" all in order = {positions == list(range(len(row)))}"
)
total = build + ingress
say(f"the row to its admission: {total:.1f} s, {1e6 * total / len(row):.0f} us a plane")

print("\n[the old literal ingress, over prefixes, for its per-comparison constant]", flush=True)
for count in PREFIXES:
    t = perf_counter()
    distinct = tuple(dict.fromkeys(row[:count]))
    seconds = perf_counter() - t
    say(
        f"  {count:5d} cusps: {seconds:9.3f} s   {1e6 * seconds / (count * (count - 1) / 2):8.1f} us a comparison"
        f"   {len(distinct)} distinct"
    )

print(f"\n[RESULT] planes={len(row)} walk={walk:.1f} s ingress={ingress:.3f} s total={total:.1f} s"
      f" rss_end={rss_mib():.1f} MiB", flush=True)
