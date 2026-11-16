"""#570 round 2: which stage of the Lorentzian perfect complex changes its count.

The stabilizer family at the named line is built from O(K), K = u^perp/u of rank 9,
and O(K)'s family size changes between processes: this probe reads the perfect
complex's own counts -- quotient cells, their stabilizers, the adjacencies -- so the
varying stage is named rather than guessed.
"""
import os
import time

START = time.monotonic()


def say(label):
    print(f"[t={time.monotonic() - START:7.2f}s] {label}  hashseed={os.environ.get('PYTHONHASHSEED')}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage_indefinite_port.indefinite.lorentzian_cells import (
    NONNEGATIVE_SQUARES,
    perfect_complex,
)
from sage_indefinite_port.indefinite.indefinite_reduction import indefinite_reduced_presentation
from sage_indefinite_port.invariants import AttackProfile

lattice = NamedLattices.Tco
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
first = plane.inclusion()(plane.inclusion().domain().module_generator(0))
import ast
records = []
for entry in open(".tmp/p570_row.log", encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    records.append((int(position), lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})))
line_class = lattice.divided_discriminant_class(first)
vector = next(vector for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class)
say("the row representative's line")
reduction = lattice.primitive_isotropic_subobject(vector).isotropic_reduction()
K = reduction.quotient_lattice()
say(f"K rank {K.module_rank()} signature {tuple(K.signature_pair())}")

began = time.monotonic()
presentation = indefinite_reduced_presentation(K)
say(f"reduction {time.monotonic() - began:.2f} s, reduced rank {presentation.reduced.module_rank()}")
profile = AttackProfile.from_lattice(presentation.reduced)
say(f"profile positive index {profile.positive_index}, sign {profile.sign}")
signed = profile.signed_view
say(f"signed view rank {signed.module_rank()} signature {tuple(signed.signature_pair())}")
began = time.monotonic()
complex_ = perfect_complex(signed, NONNEGATIVE_SQUARES, retain_facet_orbits=False)
say(f"perfect_complex {time.monotonic() - began:.2f} s")
cells = tuple(complex_.quotient_cells())
adjacencies = tuple(complex_.adjacencies())
say(f"quotient cells {len(cells)} with rows {[len(cell.rows) for cell in cells]}")
say(f"adjacencies {len(adjacencies)} with transporters {[adjacency.transporter is not None for adjacency in adjacencies]}")
backend = complex_.local_backend()
stabilizers = tuple(tuple(backend.cell_stabilizer(cell)) for cell in cells)
say(f"cell stabilizers {[len(stabilizer) for stabilizer in stabilizers]}")
say(f"component preserving {len(complex_.component_preserving_generators())}, full {len(complex_.full_orthogonal_group_generators())}")
