import traceback

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.modules.framed.formed.form_modules as fm

raw_module = fm._represented_module
raw_value = fm._represented_value_module
held = {}

def guarded_module(value, ring):
    key = (id(value), id(ring))
    entry = held.get(key)
    if entry is not None:
        held_value, held_ring, result = entry
        if held_value is value and held_ring is ring:
            return result
        print(f"[stale] _represented_module answered for a dead object at {key[0]}"
              f": recorded {type(held_value).__name__} -> {result!r}"
              f", asked about {type(value).__name__} -> {raw_module.f(value, ring)!r}", flush=True)
        fresh = raw_module.f(value, ring)
        held[key] = (value, ring, fresh)
        return fresh
    fresh = raw_module.f(value, ring)
    held[key] = (value, ring, fresh)
    return fresh

fm._represented_module = guarded_module

held_values = {}

def guarded_value_module(formed_module):
    key = id(formed_module)
    entry = held_values.get(key)
    if entry is not None:
        held_module, result = entry
        if held_module is formed_module:
            return result
        fresh = guarded_module(formed_module.value_module(), formed_module.base_ring())
        print(f"[stale-value] _represented_value_module answered for a dead formed module at {key}:"
              f" recorded {type(held_module).__name__} -> {result!r}, asked about {type(formed_module).__name__} -> {fresh!r}",
              flush=True)
        held_values[key] = (formed_module, fresh)
        return fresh
    fresh = guarded_module(formed_module.value_module(), formed_module.base_ring())
    held_values[key] = (formed_module, fresh)
    return fresh

fm._represented_value_module = guarded_value_module

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
    print(f"[probe] line cusps: {small.stable_orthogonal_group().cusps(1).cardinality()}", flush=True)
    print(f"[probe] plane cusps: {small.stable_orthogonal_group().cusps(2).cardinality()}", flush=True)
except Exception:
    traceback.print_exc()
    raise SystemExit(1)
