"""#570 round 2: the named question on the repaired path, with the rows' words in hand.

Builds the Otilde line row (which now retains the word that transported each
representative), finds the cusp carrying the plane's own line's divided class, and asks
`cusp.transporter_witness(line)` at it.  The plane's own line is registered as a
transported object whose source is a line outside the row -- what the incidence holds,
where the line comes from an ambient flag -- so the one ambient witness between the two
roots is paid once and every later question is a composition.  Before the repair the
same question was 27.40 s and 27.10 s warm.
"""
import ast
import os
import time

START = time.monotonic()
ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")


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
quotient = subgroup.finite_character_quotient()
say("the plane's own line")

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
say(f"its transport is registered: {quotient.isotropic_transport_of(cusp.representative()) is not None}")

# The datum the incidence holds: the line, and the word that carried it there from a
# line no row registered.  One search produces that word, as the incidence's own
# ambient flag would; it is paid once and is not part of a per-object question.
outside = lattice.primitive_isotropic_subobject(lattice.linear_combination(
    {label: ZZ(value) for label, value in {"h": 0, "a1": 0, "a2": 0, "a3": 0, "a4": 0, "a5": 0, "a6": 0, "a7": 0, "a8": 0, "ep": 1, "em": 0}.items() if value}
))
say(f"the outside line is the plane's own line: {str(outside.inclusion()(outside.inclusion().domain().module_generator(0))) == str(first)}")
began = time.monotonic()
carrier = subgroup.supergroup().isotropic_equivalence_witness(outside, line)
say(f"one ambient witness for the incidence's word: {carrier is not None} in {time.monotonic() - began:.2f} s")
quotient.register_isotropic_transport(line, outside, carrier)
say(f"roots: line {quotient.transported_from_root(line)[0] is outside}, cusp {quotient.transported_from_root(cusp.representative())[0] is not None}")

for attempt in range(3):
    began = time.monotonic()
    witness = cusp.transporter_witness(line)
    say(f"the named question, attempt {attempt + 1}: {witness is not None} in {time.monotonic() - began:.2f} s")
    if witness is not None:
        say(f"  in the subgroup: {witness in subgroup}")
