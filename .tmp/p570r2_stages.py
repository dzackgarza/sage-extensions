"""#570 round 2: the named transporter question, stage by stage, on the current tree.

Rebuilds the cusp from `.tmp/p570_row.log` (position 492 of 527, the Otilde line row
representative carrying the plane's own line's divided class) and times every part
of `cusp.transporter_witness(line)`: the finite-image separation, the presence of the
row's registered lifts, the ambient isometry search, the stabilizer family and its
closure, and the adjuster.  The parabolic family is asked three times on the same
line so that a size that changes inside one process is visible, and the whole
question is asked a second time for the warm cost.
"""
import ast
import os
import time

START = time.monotonic()
DEPTH = [0]
ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")


def rss_mib():
    for line in open(f"/proc/{os.getpid()}/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[t={time.monotonic() - START:8.2f}s] {'.' * DEPTH[0]} {label}  rss={rss_mib():.0f} MiB", flush=True)


def timed(label, call):
    began = time.monotonic()
    answer = call()
    say(f"{label}: {time.monotonic() - began:.2f} s")
    return answer


from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.orthogonal_quotients as oq
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

lattice = timed("T_Co", lambda: NamedLattices.Tco)
subgroup = timed("Otilde(T_Co)", lambda: lattice.stable_orthogonal_group())
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
plane_domain = plane.inclusion().domain()
first = plane.inclusion()(plane_domain.module_generator(next(iter(plane_domain.module_generating_set()))))
line = lattice.primitive_isotropic_subobject(first)
line_class = lattice.divided_discriminant_class(first)
say(f"the plane's own line, divided class {line_class}")

records = []
for entry in open(ROW_LOG, encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    vector = lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})
    records.append((int(position), vector))
named = [spot for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class]
say(f"{len(records)} recorded representatives; the named cusp's positions: {named}")
position = named[0]
representative = lattice.primitive_isotropic_subobject(next(vector for spot, vector in records if spot == position))
cusp = _arithmetic_cusp(subgroup, representative)
quotient = timed("finite_character_quotient()", lambda: subgroup.finite_character_quotient())

say("registered lifts: line=%s cusp=%s" % (
    quotient.isotropic_lift_of(line) is not None,
    quotient.isotropic_lift_of(representative) is not None,
))
say("invariant_separates_isotropic_orbits: %s" % timed(
    "  separation", lambda: quotient.invariant_separates_isotropic_orbits(line, representative)))

ambient = subgroup.supergroup()
for attempt in range(3):
    family = timed(f"isotropic_stabilizer_generators(representative), attempt {attempt + 1}",
                   lambda: ambient.isotropic_stabilizer_generators(representative))
    say(f"  family size {len(tuple(family))}")
    if attempt == 0:
        first_family = tuple(family)

witness = timed("ambient isotropic_equivalence_witness(line, representative)",
                lambda: ambient.isotropic_equivalence_witness(line, representative))
say(f"  witness is None: {witness is None}; in subgroup: {witness in subgroup}")

stabilizer = timed("exact_isotropic_stabilizer_generators(representative)",
                   lambda: quotient.exact_isotropic_stabilizer_generators(representative))
say(f"  stabilizer family size {len(tuple(stabilizer))}")
adjusted = timed("adjust_witness_into_subgroup", lambda: quotient.adjust_witness_into_subgroup(witness, stabilizer))
say(f"  adjusted is None: {adjusted is None}")

began = time.monotonic()
second = cusp.transporter_witness(line)
say(f"the whole question again: {second is not None} in {time.monotonic() - began:.2f} s")
began = time.monotonic()
third = cusp.transporter_witness(line)
say(f"the whole question a third time: {third is not None} in {time.monotonic() - began:.2f} s")
