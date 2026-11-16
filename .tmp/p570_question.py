"""#570: the named transporter question, with each of its own calls timed.

The question is `cusp.transporter_witness(line)` at the Otilde(T_Co) cusp of a
plane's own line -- exactly the call the #381 evidence measured at > 355 s.  This
probe rebuilds that cusp's representative from the coordinates `.tmp/p570_row.log`
recorded (row position 492 of 527) and runs the real call with each stage it passes
through wrapped on the class: an "enter" line with no matching "exit" names the
stage that does not come back.
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


from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.orthogonal_quotients as oq
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
from sage_extensions.categories.lattice_morphisms import LatticeIsometryMor


def wrap(cls, name):
    original = getattr(cls, name)

    def timed(self, *arguments, **keywords):
        DEPTH[0] += 1
        say(f"enter {name}")
        began = time.monotonic()
        try:
            return original(self, *arguments, **keywords)
        finally:
            DEPTH[0] -= 1
            say(f"exit  {name}  {time.monotonic() - began:.2f} s")

    setattr(cls, name, timed)


for name in (
    "invariant_separates_isotropic_orbits",
    "separates_witness_orbits",
    "exact_isotropic_stabilizer_generators",
    "adjust_witness_into_subgroup",
    "isotropic_lift_of",
    "image",
    "splitting_isometries",
):
    wrap(oq.OrthogonalCharacterQuotient, name)
wrap(LatticeIsometryMor, "isotropic_equivalence_witness")
wrap(LatticeIsometryMor, "isotropic_stabilizer_generators")

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
say("Otilde(T_Co)")
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
plane_domain = plane.inclusion().domain()
plane_labels = tuple(plane_domain.module_generating_set())
first = plane.inclusion()(plane_domain.module_generator(plane_labels[0]))
line = lattice.primitive_isotropic_subobject(first)
line_class = lattice.divided_discriminant_class(first)
say(f"the plane's own line, divided class {line_class}")

candidate = None
for entry in open(ROW_LOG, encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    vector = lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})
    if lattice.divided_discriminant_class(vector) == line_class:
        candidate = (int(position), vector)
        break
if candidate is None:
    raise SystemExit("no recorded row representative carries the plane line's class")
position, vector = candidate
representative = lattice.primitive_isotropic_subobject(vector)
say(f"the cusp's own line: row position {position}, distinct from the plane's line {vector != first}")

cusp = _arithmetic_cusp(subgroup, representative)
say("the cusp")

say("the named question: cusp.transporter_witness(line)")
began = time.monotonic()
witness = cusp.transporter_witness(line)
answered = time.monotonic() - began
say(f"answered {witness is not None} in {answered:.2f} s; in the subgroup: {witness in subgroup}")
