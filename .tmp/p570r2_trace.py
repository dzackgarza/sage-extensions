"""#570 round 2: a trace of every orthogonal-group family the delegated line family asks for.

Wraps the recursion's own entry points so each family it returns is named with its
rank, its Gram key, whether the groupoid cache answered, and its size. The point is to
name the exact lattice whose family size changes between processes.
"""
import os
import time

START = time.monotonic()
DEPTH = [0]


def say(label):
    print(f"[t={time.monotonic() - START:7.2f}s] {'.' * DEPTH[0]} {label}", flush=True)


from sage_extensions.all import *  # noqa: F401,F403

import sage_indefinite_port.indefinite.recursive as recursive
import sage_indefinite_port.indefinite.lorentzian_cells as cells
from sage_indefinite_port.indefinite.groupoid_cache import IsometryGroupoidCache

original_group = recursive.EichlerRecursion.orthogonal_group_generators


def traced_group(self, lattice):
    DEPTH[0] += 1
    say(f"enter orthogonal_group_generators rank {lattice.module_rank()}")
    began = time.monotonic()
    try:
        answer = original_group(self, lattice)
    finally:
        DEPTH[0] -= 1
    say(f"exit  orthogonal_group_generators rank {lattice.module_rank()}: {len(tuple(answer))} in {time.monotonic() - began:.2f} s")
    return answer


recursive.EichlerRecursion.orthogonal_group_generators = traced_group

original_cached = IsometryGroupoidCache.cached_group


def traced_cached(self, lattice):
    answer = original_cached(self, lattice)
    say(f"cached_group rank {lattice.module_rank()}: {'miss' if answer is None else str(len(tuple(answer))) + ' hit'}")
    return answer


IsometryGroupoidCache.cached_group = traced_cached

original_lorentzian = cells.lorentzian_orthogonal_group_generators


def traced_lorentzian(lattice):
    answer = original_lorentzian(lattice)
    say(f"lorentzian_orthogonal_group_generators rank {lattice.module_rank()}: {len(tuple(answer))}")
    return answer


recursive.lorentzian_orthogonal_group_generators = traced_lorentzian

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
import ast
records = []
for entry in open(".tmp/p570_row.log", encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    records.append((int(position), lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})))
line_class = lattice.divided_discriminant_class(first)
representative = lattice.primitive_isotropic_subobject(
    next(vector for spot, vector in records if lattice.divided_discriminant_class(vector) == line_class))
say("the named line")
family = tuple(subgroup.supergroup().isotropic_stabilizer_generators(representative))
say(f"family {len(family)}")
