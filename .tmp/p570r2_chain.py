"""#570 round 2: the chain from O(K) to the returned family, in one order, without the family first."""
import os
import time

START = time.monotonic()


def say(label):
    print(f"[t={time.monotonic() - START:7.2f}s] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
import ast
from sage_indefinite_port.indefinite.marked_lattices import RECURSION

lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
first = plane.inclusion()(plane.inclusion().domain().module_generator(0))
line_class = lattice.divided_discriminant_class(first)
records = []
for entry in open(".tmp/p570_row.log", encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    records.append((int(position), lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})))
representative = lattice.primitive_isotropic_subobject(
    next(vector for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class))
vector = representative.inclusion()(representative.inclusion().domain().module_generator(0))
K = lattice.primitive_isotropic_subobject(vector).isotropic_reduction().quotient_lattice()

ok = tuple(RECURSION.orthogonal_group_generators(K))
say(f"O(K): {len(ok)}")
action = RECURSION.isotropic_stabilizer_action((vector,), ((-vector,),))
rational = action.rational_group()
say(f"rational group generators: {len(tuple(rational.group_generators()))}")
stabilizer = action.stabilizer()
inside = tuple(stabilizer.group_generators())
say(f"integral stabilizer generators: {len(inside)}")
family = tuple(lattice.integral_isometry(generator) for generator in inside)
say(f"integral family: {len(family)}")
again = RECURSION.isotropic_stabilizer_action((vector,), ((-vector,),))
say(f"a second action: rational {len(tuple(again.rational_group().group_generators()))}, stabilizer {len(tuple(again.stabilizer().group_generators()))}")
