"""#570 round 2: is the reduced presentation of the cusp's quotient one lattice or several?"""
import ast
import os
import time

START = time.monotonic()


def say(label):
    print(f"[t={time.monotonic() - START:7.2f}s] {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_indefinite_port.indefinite.indefinite_reduction import indefinite_reduced_presentation

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
vector = next(vector for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class)
K = lattice.primitive_isotropic_subobject(vector).isotropic_reduction().quotient_lattice()


def gram(lattice):
    labels = tuple(lattice.module_generating_set())
    basis = tuple(lattice.module_generator(label) for label in labels)
    return tuple(tuple(int(lattice.b(left, right)) for right in basis) for left in basis)


for attempt in range(2):
    reduced = indefinite_reduced_presentation(K).reduced
    say(f"attempt {attempt + 1}: reduced gram {gram(reduced)}")
