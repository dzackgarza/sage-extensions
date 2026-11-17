r"""Probe: which value module `_represented_value_module` answers with, at the failing step."""

import traceback

from sage_extensions.all import *  # noqa: F401,F403

import sage_extensions.categories.modules.framed.formed.form_modules as form_modules
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

original = form_modules._represented_value_module


def watched(formed_module):
    answer = original(formed_module)
    value = formed_module.value_module()
    entries = [
        key
        for key in form_modules._represented_module.cache
        if key[0] == id(value) or key[1] == id(formed_module.base_ring())
    ]
    print(
        f"  [value] formed {type(formed_module).__name__} value_module {type(value).__name__}"
        f" id={id(value)} ring {type(formed_module.base_ring()).__name__} id={id(formed_module.base_ring())}"
        f" -> {type(answer).__name__} id={id(answer)} cache keys {entries}",
        flush=True,
    )
    return answer


form_modules._represented_value_module = watched

holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
tco_group = holder.stable_orthogonal_group()
for offset in range(20):
    built = holder.primitive_isotropic_subobject(first_vector + (offset + 1) * names["ep"], names["ep"])
    _arithmetic_cusp(tco_group, built)
del built
import gc
gc.collect()
print("[probe] the T_Co planes are dropped; the formed-module cache holds"
      f" {len(form_modules._represented_module.cache)} entries", flush=True)

small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
try:
    small.stable_orthogonal_group().has_selected_finite_group_generating_set()
    print("[probe] green", flush=True)
except Exception:
    traceback.print_exc()
    print("[probe] the cache now holds "
          f"{len(form_modules._represented_module.cache)} entries", flush=True)
    for key, value in list(form_modules._represented_module.cache.items())[:12]:
        alive = [type(part).__name__ for part in key]
        print(f"  [entry] key parts {alive} -> {type(value).__name__} id={id(value)}", flush=True)
    raise SystemExit(1)
