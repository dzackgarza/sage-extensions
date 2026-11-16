"""#570 round 2: the named question on the parent tree, with the line row in hand.

The row is built first, so the caches it warms are the ones the incidence has; the
question is then asked three times.  This is the before column for the transport
repair, whose after column is `.tmp/p570r2_witness.log`.
"""
import ast
import os
import time

START = time.monotonic()
ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")


def say(label):
    print(f"[t={time.monotonic() - START:8.2f}s] {label}", flush=True)


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
first = plane.inclusion()(plane.inclusion().domain().module_generator(0))
line = lattice.primitive_isotropic_subobject(first)
line_class = lattice.divided_discriminant_class(first)
began = time.monotonic()
row = tuple(subgroup.isotropic_orbit_representatives(1))
say(f"the line row: {len(row)} representatives in {time.monotonic() - began:.2f} s")
records = []
for entry in open(ROW_LOG, encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    records.append((int(position), lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})))
position = next(spot for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class)
cusp = _arithmetic_cusp(subgroup, lattice.primitive_isotropic_subobject(next(vector for spot, vector in records if spot == position)))
say(f"the cusp at recorded position {position}")
for attempt in range(3):
    began = time.monotonic()
    witness = cusp.transporter_witness(line)
    say(f"the named question, attempt {attempt + 1}: {witness is not None} in {time.monotonic() - began:.2f} s")
