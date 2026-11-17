r"""A primitive isotropic plane whose last holder drops it is collected.

A plane of a lattice is a parent: its module, its Gram, its category placement
and its inclusion.  What names it is its span, the row Hermite form of its
generator coordinates in the ambient lattice's basis, and that name is a datum
of the lattice rather than of the object.  Being named by a span does not make
the object immortal: nothing in the library keeps a plane alive once the caller
that constructed it has dropped it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_dropped_plane_is_collected() -> None:
    r"""A plane and its inclusion are collected, and the span still names one plane.

    \(U \oplus U\) has basis \(e_1, f_1, e_2, f_2\) with \(b(e_i, f_i) = 1\) and
    \(q(e_i) = q(f_i) = 0\), so \(\langle e_1, f_2 \rangle\) is a primitive
    totally isotropic plane and \(e_2\) lies in it for no choice of generators.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, _f1, e2, f2 = lattice.module_generators()
    plane = lattice.primitive_isotropic_subobject(e1, f2)
    plane_reference = weakref.ref(plane)
    inclusion_reference = weakref.ref(plane.inclusion())

    del plane
    gc.collect()

    assert plane_reference() is None
    assert inclusion_reference() is None
    rebuilt = lattice.primitive_isotropic_subobject(e1, f2)
    assert rebuilt.module_rank() == 2
    assert e1 in rebuilt
    assert f2 in rebuilt
    assert e2 not in rebuilt
