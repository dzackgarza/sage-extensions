r"""Probe: which object keeps a dropped isotropic subobject alive.

The lattice's constructor registry holds the subobject weakly, so a plane the
caller drops must be collected -- unless something else in the tree holds it.
This probe builds one plane of ``U + U(2) + <-2>``, drops it, and prints the
referrers of the surviving object, with the owning container's name where the
referrer is a dictionary that can be found in a known object's ``__dict__``.
"""

import gc
import sys
import weakref

from sage_extensions.all import *  # noqa: F401,F403
from sage.structure.unique_representation import UniqueRepresentation


def named_holder(referrer, candidates):
    r"""A name for the structure holding ``referrer``, when one of ``candidates`` owns it."""
    for owner_name, owner in candidates:
        for attribute, value in list(vars(owner).items()):
            if value is referrer:
                return f"{owner_name}.{attribute}"
            if isinstance(value, dict):
                for key, item in list(value.items()):
                    if item is referrer:
                        return f"{owner_name}.{attribute}[{str(key)[:60]}]"
    return ""


lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
plane = lattice.primitive_isotropic_subobject(lattice.basis_vector(0), lattice.basis_vector(2))
reference = weakref.ref(plane)
print(f"[probe] the plane is built, retained {lattice.retained_primitive_isotropic_subobject_count()}", flush=True)
del plane
gc.collect()
survivor = reference()
print(f"[probe] after the drop the plane is alive: {survivor is not None}", flush=True)
if survivor is not None:
    print(f"[probe] the subobject's own type: {type(survivor).__name__}", flush=True)
    print(f"[probe] is it a UniqueRepresentation: {isinstance(survivor, UniqueRepresentation)}", flush=True)
    referrers = gc.get_referrers(survivor)
    print(f"[probe] referrers: {len(referrers)}", flush=True)
    candidates = [("lattice", lattice), ("the category", lattice.category())]
    for referrer in referrers:
        described = named_holder(referrer, candidates)
        print(
            f"  [{type(referrer).__name__}] {described or repr(referrer)[:160]}",
            flush=True,
        )
