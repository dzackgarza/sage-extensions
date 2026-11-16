"""#570: the same question again, and the next cusp's, on the repaired tree.

The first question at the named cusp is measured in `.tmp/p570_question-fixed.log`
(98.80 s, of which the adjuster is 5.43 s).  This probe asks it a second time and
then asks the question at two further cusps of the same row, so the marginal cost
of one more cusp -- what a 527-cusp or 189720-plane row pays per element -- is
measured rather than implied.
"""
import ast
import os
import time

START = time.monotonic()
ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")
CUSPS = int(os.environ.get("PROBE_CUSPS", "2"))


def rss_mib():
    for line in open(f"/proc/{os.getpid()}/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[t={time.monotonic() - START:8.2f}s] {label}  rss={rss_mib():.0f} MiB", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
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
say("the plane's own line")

records = []
for entry in open(ROW_LOG, encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    vector = lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})
    records.append((int(position), vector))
say(f"{len(records)} recorded row representatives")

named = [position for position, vector in records
         if lattice.divided_discriminant_class(vector) == line_class]
say(f"the named cusp's positions: {named}")
position = named[0]
representative = lattice.primitive_isotropic_subobject(
    next(vector for spot, vector in records if spot == position))
cusp = _arithmetic_cusp(subgroup, representative)
say(f"the cusp at position {position}")

began = time.monotonic()
witness = cusp.transporter_witness(line)
say(f"first question: {witness is not None} in {time.monotonic() - began:.2f} s")
began = time.monotonic()
again = cusp.transporter_witness(line)
say(f"the same question again: {again is not None} in {time.monotonic() - began:.2f} s")

others = [spot for spot, _vector in records if spot != position][:CUSPS]
for spot in others:
    other = lattice.primitive_isotropic_subobject(
        next(vector for position_, vector in records if position_ == spot))
    other_cusp = _arithmetic_cusp(subgroup, other)
    began = time.monotonic()
    answer = other_cusp.transporter_witness(line)
    say(f"the question at position {spot}: {answer is not None} in {time.monotonic() - began:.2f} s")
