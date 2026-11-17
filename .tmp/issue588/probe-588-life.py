r"""Probe: a cusp of T_Co named by a span, whether its plane is released, and the row's answers.

Cheap (no coset walk): one plane, one cusp, the drop test, and the acceptance
points on a lattice whose rows return in seconds -- the cusp counts, their spans
and the incidence's edges, which must read the same on both trees.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories.isotropic_orbits import (
    _arithmetic_cusp,
    _same_subobject,
    _span_key,
)

holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
subgroup = holder.stable_orthogonal_group()
plane = holder.primitive_isotropic_subobject(first_vector, names["ep"])
cusp = _arithmetic_cusp(subgroup, plane)
print(f"[probe] the cusp's rank: {cusp.module_rank()}", flush=True)
has_span = getattr(cusp, "span", None)
print(f"[probe] the cusp exposes span(): {callable(has_span)}", flush=True)
if callable(has_span):
    print(f"[probe] cusp.span() equals _span_key(plane): {cusp.span() == _span_key(plane)}", flush=True)
rebuilt = cusp.representative()
print(f"[probe] the rebuilt representative is the same subobject: {_same_subobject(rebuilt, plane)}", flush=True)
print(f"[probe] its span key equals the plane's: {_span_key(rebuilt) == _span_key(plane)}", flush=True)
print(f"[probe] the rebuilt representative is primitive: {rebuilt.is_primitive()}", flush=True)
print(f"[probe] the rebuilt representative is totally isotropic: {rebuilt.is_totally_isotropic()}", flush=True)
print(f"[probe] its rank: {rebuilt.module_rank()}", flush=True)
del rebuilt

# ---- the drop test: one plane, and twenty of them -------------------------
reference = weakref.ref(plane)
del plane
gc.collect()
print(f"[probe] one named plane is alive after the drop: {reference() is not None}", flush=True)

references = []
for offset in range(20):
    vector = first_vector + (offset + 1) * names["ep"]
    built = holder.primitive_isotropic_subobject(vector, names["ep"])
    _arithmetic_cusp(subgroup, built)
    references.append(weakref.ref(built))
del built
del vector
gc.collect()
survivors = sum(1 for reference in references if reference() is not None)
print(f"[probe] planes alive after being named by a cusp and dropped: {survivors} of 20", flush=True)

# ---- acceptance: a lattice whose rows return in seconds ------------------
small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
small_subgroup = small.stable_orthogonal_group()
line_cusps = small_subgroup.cusps(1)
plane_cusps = small_subgroup.cusps(2)
print(f"\n[probe] U+U(2)+<-2>: line cusps {line_cusps.cardinality()}, plane cusps {plane_cusps.cardinality()}", flush=True)
for position, cusp in enumerate(plane_cusps):
    representative = cusp.representative()
    print(
        f"  [plane cusp {position}] span {_span_key(representative)}"
        f" primitive {representative.is_primitive()}"
        f" totally isotropic {representative.is_totally_isotropic()}"
        f" rank {representative.module_rank()}",
        flush=True,
    )
for position, cusp in enumerate(line_cusps):
    representative = cusp.representative()
    print(
        f"  [line cusp {position}] span {_span_key(representative)}"
        f" primitive {representative.is_primitive()}"
        f" totally isotropic {representative.is_totally_isotropic()}",
        flush=True,
    )
relation = small_subgroup.tits_building_incidence()
edges = [
    incidence
    for incidence in relation
]
print(f"[probe] the incidence holds {len(edges)} certificates", flush=True)
for incidence in edges:
    print(
        f"  [edge] line {_span_key(incidence.line_cusp().representative())}"
        f" plane {_span_key(incidence.plane_cusp().representative())}",
        flush=True,
    )
