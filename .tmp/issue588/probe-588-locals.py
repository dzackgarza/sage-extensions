r"""Probe: the frames of the failing formed-module construction, with their locals."""

import traceback

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

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

small = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
try:
    small.stable_orthogonal_group().has_selected_finite_group_generating_set()
except Exception:
    frames = traceback.extract_tb(__import__("sys").exc_info()[2])
    for frame in frames[-14:]:
        print(f"[frame] {frame.filename.split('/')[-1]}:{frame.lineno} {frame.name}: {frame.line}", flush=True)
    import sys

    walker = sys.exc_info()[2]
    last = None
    while walker is not None:
        last = walker
        walker = walker.tb_next
    scope = last.tb_frame.f_locals
    import sage_extensions.categories.modules.framed.formed.form_modules as form_modules

    for key in ("domain", "codomain"):
        module = scope[key]
        try:
            ring = module.base_ring()
            value = module.value_module()
        except Exception as error:
            print(f"  [{key}] {error}", flush=True)
            continue
        print(
            f"  [{key}] id={id(module)} rank={module.module_rank()} ring={ring} id={id(ring)}"
            f" value_module {type(value).__name__} id={id(value)} value is ring {value is ring}",
            flush=True,
        )
        print(f"    {key} category {type(module.category()).__name__}", flush=True)
    morphism = scope["value_morphism"]
    print(
        f"  [value_morphism] id={id(morphism)} domain id={id(morphism.domain())}"
        f" codomain id={id(morphism.codomain())}",
        flush=True,
    )
    print(f"  [target_values] id={id(scope['target_values'])}", flush=True)
    print(f"  [source_values] id={id(scope['source_values'])}", flush=True)
    for key, value in list(form_modules._represented_module.cache.items())[:10]:
        print(f"  [entry] {key} -> {type(value).__name__} id={id(value)}", flush=True)
    raise SystemExit(1)
