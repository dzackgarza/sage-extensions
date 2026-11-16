"""#570 round 2: where the parabolic family's size comes from, and whether it is one number.

Builds T_Co's named line (row position 492) and walks the induction's own stages,
printing the size at each: the reduction K = u^perp/u, the recursive O(K) generating
family, the pointwise perpendicular kernel, the rational group built from them, and
the integral stabilizer inside it whose generators are the returned family.  Two runs
with different PYTHONHASHSEED show whether a size depends on an unordered iteration.
"""
import ast
import os
import time

START = time.monotonic()
ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")


def say(label):
    print(f"[t={time.monotonic() - START:8.2f}s] {label}  hashseed={os.environ.get('PYTHONHASHSEED')}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403

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
line_class = lattice.divided_discriminant_class(first)
records = []
for entry in open(ROW_LOG, encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    vector = lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})
    records.append((int(position), vector))
representative = lattice.primitive_isotropic_subobject(
    next(vector for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class))
say("the named line")

from sage_indefinite_port.indefinite.marked_lattices import RECURSION

ambient = subgroup.supergroup()
began = time.monotonic()
delegated = tuple(ambient.isotropic_stabilizer_generators(representative))
say(f"delegated family: {len(delegated)} generators in {time.monotonic() - began:.2f} s")

vector = representative.inclusion()(representative.inclusion().domain().module_generator(0))
reduction = vector.parent().primitive_isotropic_subobject(vector).isotropic_reduction()
quotient = reduction.quotient_lattice()
say(f"K = u^perp/u, rank {quotient.module_rank()}")

began = time.monotonic()
kernel = tuple(reduction.pointwise_perpendicular_kernel().group_generators())
say(f"pointwise perpendicular kernel: {len(kernel)} generators in {time.monotonic() - began:.2f} s")

began = time.monotonic()
okay = tuple(RECURSION.orthogonal_group_generators(quotient))
say(f"recursive O(K) family: {len(okay)} generators in {time.monotonic() - began:.2f} s")

began = time.monotonic()
action = RECURSION.isotropic_stabilizer_action((vector,), ((-vector,),))
rational = action.rational_group()
say(f"rational group: {len(tuple(rational.group_generators()))} generators in {time.monotonic() - began:.2f} s")

began = time.monotonic()
stabilizer = action.stabilizer()
inside = tuple(stabilizer.group_generators())
say(f"integral stabilizer: {len(inside)} generators in {time.monotonic() - began:.2f} s")

began = time.monotonic()
again = tuple(ambient.isotropic_stabilizer_generators(representative))
say(f"delegated family again: {len(again)} generators in {time.monotonic() - began:.2f} s")

began = time.monotonic()
images = subgroup.finite_character_quotient()
say(f"finite character quotient: {time.monotonic() - began:.2f} s")
began = time.monotonic()
image = images.image_subgroup_of(tuple(delegated)) if hasattr(images, "image_subgroup_of") else None
say(f"image subgroup: {time.monotonic() - began:.2f} s")
