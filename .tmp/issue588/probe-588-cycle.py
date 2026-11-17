r"""Probe: is a dropped constructed subobject collected, and does `gc` see its cycle?

The rank-one lattice is the control: it has one construction registry that no
longer holds it.  A plane is the specimen.  `gc.is_tracked` decides whether the
collector can see into the object at all, which is what separates "a registry
still names it" from "its own graph is a cycle the collector cannot traverse".
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403


def specimen(build, label):
    built = build()
    tracked = {label: gc.is_tracked(built)}
    for name in ("inclusion", "module_generating_set", "gram"):
        try:
            attribute = getattr(built, name)()
        except Exception:
            continue
        tracked[name] = gc.is_tracked(attribute)
    reference = weakref.ref(built)
    del attribute
    del built
    collected = gc.collect()
    print(
        f"[probe] {label}: tracked {tracked} alive after the drop {reference() is not None}"
        f" (gc.collect() found {collected})",
        flush=True,
    )
    if reference() is not None:
        survivor = reference()
        print(f"  [probe] its type {type(survivor).__mro__[:4]}", flush=True)
        del survivor


specimen(lambda: Lattices(ZZ)([[2]]), "a rank-one lattice")
specimen(lambda: Lattices(ZZ)("U"), "U")

holder = NamedLattices.Tco
labels = tuple(holder.module_generating_set())
names = {str(label): holder.module_generator(label) for label in labels}
first_vector = holder.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
specimen(lambda: holder.primitive_isotropic_subobject(first_vector, names["ep"]), "a plane of T_Co")
specimen(lambda: holder.subobject_on((first_vector, names["ep"])), "the plane's bare module subobject")
specimen(lambda: holder.primary_form_tensor() if hasattr(holder, "primary_form_tensor") else holder.gram(), "T_Co's Gram")
