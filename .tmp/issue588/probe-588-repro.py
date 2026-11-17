r"""Probe: the small lattice's ambient generator resolution, the cheapest failing step."""

import traceback

from sage_extensions.all import *  # noqa: F401,F403

holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

tco_group = holder.stable_orthogonal_group()
references = []
for offset in range(20):
    built = holder.primitive_isotropic_subobject(first_vector + (offset + 1) * names["ep"], names["ep"])
    _arithmetic_cusp(tco_group, built)
    references.append(built)
del built
del references
import gc
gc.collect()
print("[probe] the T_Co planes are dropped", flush=True)

small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
group = small.stable_orthogonal_group()
try:
    decision = group.has_selected_finite_group_generating_set()
    print(f"[probe] the ambient group's selected generators are decided: {decision}", flush=True)
    generators = group.group_generators()
    print(f"[probe] generators: {len(tuple(generators))}", flush=True)
    subgroup = small.stable_orthogonal_group()
    print(f"[probe] line cusps: {small.stable_orthogonal_group().cusps(1).cardinality()}", flush=True)
    print(f"[probe] plane cusps: {small.stable_orthogonal_group().cusps(2).cardinality()}", flush=True)
except Exception:
    traceback.print_exc()
    raise SystemExit(1)
