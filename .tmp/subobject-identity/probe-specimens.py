r"""Probe: which constructed subobject survives the drop of its only holder.

A plane of a lattice is a parent with its module, its Gram, its category
placement and its inclusion.  The specimens differ in how much of the library's
machinery the ambient lattice carries, so the drop test is run on each.
"""

import gc
import weakref

from sage_extensions.all import *  # noqa: F401,F403


def specimen(build, label):
    built = build()
    reference = weakref.ref(built)
    inclusion = weakref.ref(built.inclusion())
    del built
    gc.collect()
    print(
        f"[probe] {label}: the plane alive after the drop {reference() is not None},"
        f" its inclusion {inclusion() is not None}",
        flush=True,
    )


def rank_four():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, _f1, _e2, f2 = lattice.module_generators()
    return lattice.primitive_isotropic_subobject(e1, f2)


def rank_five():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2) + Lattices(ZZ)([[-2]])
    cusp = next(iter(lattice.stable_orthogonal_group().cusps(2)))
    return cusp.representative()


def tco():
    lattice = NamedLattices.Tco
    labels = tuple(lattice.module_generating_set())
    names = {str(label): lattice.module_generator(label) for label in labels}
    first = lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    )
    return lattice.primitive_isotropic_subobject(first, names["ep"])


specimen(rank_four, "a plane of U+U")
specimen(rank_five, "a plane of U+U(2)+<-2>")
specimen(tco, "a plane of T_Co")
