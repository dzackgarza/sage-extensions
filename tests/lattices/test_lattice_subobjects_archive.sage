r"""Archived lattice-subobject semantics on the live embedded-subobject owner.

The archived ``Subobjects`` category treated a lattice subobject as its actual
embedding into an ambient lattice and required primitivity, saturation, sum, intersection,
and orthogonal complement to be computed from that arrow.
These specimens keep those mathematical requirements without restoring the
archived wrapper.
"""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/modules/framed/formed/integrallattice/subobjects.sage",
    "live_owner": "sage_extensions/categories/abstract_categories/arrow_categories.py",
    "disposition": "reconciled-live-owner",
}


def _same_embedded_subobject(left, right) -> bool:
    left.inclusion().factor_through(right.inclusion())
    right.inclusion().factor_through(left.inclusion())
    return True


def test_archived_nonprimitive_subobject_saturates_inside_the_same_lattice() -> None:
    lattice = Lattices(ZZ)("U")
    e, _f = lattice.module_generators()
    doubled_line = lattice.subobject_on((2 * e,))
    primitive_line = lattice.subobject_on((e,))

    assert doubled_line.ambient_lattice() is lattice
    assert not doubled_line.is_primitive()
    saturation = doubled_line.saturation()
    assert saturation.ambient_lattice() is lattice
    assert saturation.is_primitive()
    assert _same_embedded_subobject(saturation, primitive_line)


def test_archived_sum_and_intersection_are_join_and_meet_of_embedded_subobjects() -> None:
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    doubled_line = lattice.subobject_on((2 * e,))
    transverse_line = lattice.subobject_on((f,))

    join = doubled_line.sum(transverse_line)
    meet = doubled_line.intersection(transverse_line)

    assert join.ambient_lattice() is lattice
    assert join.index() == 2
    assert join.inclusion().is_in_image(2 * e)
    assert join.inclusion().is_in_image(f)
    assert not join.inclusion().is_in_image(e)

    assert meet.ambient_lattice() is lattice
    assert meet.module_rank() == 0


def test_archived_orthogonal_complement_retains_the_actual_embedding() -> None:
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    doubled_line = lattice.subobject_on((2 * e,))
    primitive_line = lattice.subobject_on((e,))

    perpendicular = doubled_line.orthogonal_complement()

    assert perpendicular.ambient_lattice() is lattice
    assert _same_embedded_subobject(perpendicular, primitive_line)
    for generator in perpendicular.embedded_module_generators():
        assert lattice.b(generator, 2 * e) == 0
    assert not perpendicular.inclusion().is_in_image(f)
