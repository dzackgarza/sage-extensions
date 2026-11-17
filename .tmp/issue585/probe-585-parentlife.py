r"""Probe: which owned Parents a caller can actually release.

An owned parent belongs to its class, and a class is not collectable: the
question this probe answers is whether a dropped parent is released anyway, for
an ordinary lattice and for a subobject of a live lattice.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403


def released(build, label):
    r"""Build one object by ``build()``, drop it, collect, and report the lifetime."""
    obj = build()
    reference = weakref.ref(obj)
    kind = type(obj).__name__[:60]
    del obj
    gc.collect()
    print(f"[probe] {label}: {kind} is alive after the drop: {reference() is not None}", flush=True)


holder = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
released(lambda: Lattices(ZZ)([[2]]), "a lattice nothing else names")
released(lambda: Lattices(ZZ)("U"), "another lattice nothing else names")
released(lambda: holder.basis_vector(0), "a vector of the held lattice")
released(lambda: holder.primitive_isotropic_subobject(holder.basis_vector(0), holder.basis_vector(2)), "a plane of the held lattice")
released(lambda: holder.primitive_isotropic_subobject(holder.basis_vector(0)), "a line of the held lattice")
released(lambda: holder.primitive_isotropic_subobject(), "the zero subobject")
