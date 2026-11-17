r"""Probe: the old ingress and the repaired admission over one list of cusps.

Both admissions are applied, in one process, to the same plane cusps of
`Otilde(T_Co)` drawn from the route's own walk, and the two rows are compared
element by element: the objects, the span each names, the position each
answers, and membership for a member, for a cusp rebuilt from a member's span,
and for a cusp of the other rank.  Nothing is asserted; every comparison is
printed with its answer.
"""

import os
from time import perf_counter

START = perf_counter()
PLANES = int(os.environ.get("PROBE_PLANES", "100"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[{perf_counter() - START:9.1f} s rss {rss_mib():8.1f} MiB] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import (
    _arithmetic_cusp,
    _span_key,
    _subobject_of_span,
)
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
identity_element = quotient._discriminant_group.one()
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
t = perf_counter()
lift, element = next(splittings)
say(f"the split's first lift (the whole coset walk) {perf_counter() - t:.1f} s")
quotient.register_isotropic_lift(source, quotient.supergroup.one(), family, identity_element)

points = [_arithmetic_cusp(subgroup, source)]
for _position in range(1, PLANES):
    lift, element = next(splittings)
    transported = lift.transport_isotropic_object(source)
    quotient.register_isotropic_lift(transported, lift, family, element)
    points.append(_arithmetic_cusp(subgroup, transported))
    _composite_divided_class_action(quotient, element, identity_element)
    del transported
    if (_position + 1) % 25 == 0:
        say(f"plane {_position + 1}/{PLANES}")
say(f"{len(points)} plane cusps of Otilde(T_Co) drawn")

t = perf_counter()
old = finite_ordered_set(tuple(points))
old_seconds = perf_counter() - t
say(f"the old ingress, finite_ordered_set(tuple(points)): {old_seconds:.3f} s")

t = perf_counter()
new = _distinct_finite_ordered_set(points)
new_seconds = perf_counter() - t
say(f"the repaired admission, _distinct_finite_ordered_set(points): {new_seconds:.3f} s")

old_points = tuple(old)
new_points = tuple(new)
print(f"\n[cardinality] old {old.cardinality()}  new {new.cardinality()}", flush=True)
print(f"[counts] old {len(old_points)}  new {len(new_points)}  drawn {len(points)}", flush=True)
print(
    f"[the objects] every retained cusp is the one drawn, in its own position:"
    f" old {all(a is b for a, b in zip(old_points, points, strict=True))}"
    f"  new {all(a is b for a, b in zip(new_points, points, strict=True))}",
    flush=True,
)
mismatched = [
    position
    for position, (left, right) in enumerate(zip(old_points, new_points, strict=True))
    if left.span() != right.span()
]
print(f"[the planes, position by position] positions whose span differs: {mismatched}", flush=True)
span_keys = [_span_key(cusp.representative()) for cusp in points]
print(f"[the planes] distinct span keys among the {len(points)} cusps drawn: {len({key for key in span_keys})}", flush=True)

old_positions = [old.enumeration_inverse()(cusp) for cusp in old_points]
new_positions = [new.enumeration_inverse()(cusp) for cusp in new_points]
print(
    f"[the inverse] old {old_positions[:5]} ... {old_positions[-2:]}"
    f"  new {new_positions[:5]} ... {new_positions[-2:]}"
    f"  equal at every position: {old_positions == new_positions == list(range(len(points)))}",
    flush=True,
)
print(
    f"[membership] every drawn cusp in its row: old {all(cusp in old for cusp in old_points)}"
    f"  new {all(cusp in new for cusp in new_points)}",
    flush=True,
)

rebuilt = _arithmetic_cusp(subgroup, _subobject_of_span(lattice, points[0].span()))
print(
    f"[a cusp rebuilt from a member's span] same span: {rebuilt.span() == points[0].span()}"
    f"  equal to the member: {rebuilt == points[0]}"
    f"  old places it at {old.enumeration_inverse()(rebuilt)}"
    f"  new places it at {new.enumeration_inverse()(rebuilt)}"
    f"  old admits it: {rebuilt in old}  new admits it: {rebuilt in new}",
    flush=True,
)

foreign = _arithmetic_cusp(subgroup, lattice.primitive_isotropic_subobject(names["ep"]))
print(
    f"[the subgroup's cusp of another rank, which no plane row holds] rank {foreign.module_rank()}"
    f"  old places it at {old.enumeration_inverse()(foreign)}"
    f"  new places it at {new.enumeration_inverse()(foreign)}",
    flush=True,
)

print(
    f"\n[RESULT] cusps={len(points)} old_ingress={old_seconds:.3f} s"
    f" repaired={new_seconds:.3f} s"
    f" ratio={old_seconds / new_seconds:.0f}"
    f" per_comparison={1e6 * old_seconds / (len(points) * (len(points) - 1) / 2):.1f} us",
    flush=True,
)
