r"""Archived ADE root-lattice semantics on the live root-lattice owner.

The archived ``RootLattices`` category retained the selected Cartan type and
simple-root framing together with highest roots, Coxeter numbers, simple
reflections, fundamental weights, root signs/heights, and coroots.  The
``A2`` specimen is small enough to distinguish all of these operations from
mere root enumeration.
"""

from sage_extensions.all import *


def test_archived_a2_selected_simple_system_and_highest_root_are_live() -> None:
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.simple_roots()
    highest = lattice.highest_root()

    diagram = lattice.dynkin_diagram()
    # The irreducible finite root systems of rank two are A2, B2 and G2, and
    # only A2 is simply laced: its one bond has Coxeter matrix entry 3.
    assert diagram.is_connected()
    assert diagram.is_elliptic()
    assert diagram.coxeter_entry(diagram.vertex(0), diagram.vertex(1)) == 3
    assert lattice.root_system_type_name() == "A2"
    assert diagram.cardinality() == cardinal(2)
    assert lattice.coxeter_number() == 3
    assert highest == first + second
    assert highest.is_root()
    assert highest.is_positive_root()
    assert highest.height() == 2
    assert (-highest).is_negative_root()
    assert (-highest).height() == -2
    assert first.height() == 1
    assert second.height() == 1


def test_archived_simple_reflections_act_on_the_selected_root_framing() -> None:
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.simple_roots()
    first_reflection, second_reflection = lattice.simple_reflections()

    assert first_reflection(first) == -first
    assert second_reflection(second) == -second
    assert first_reflection(second) == first + second
    assert second_reflection(first) == first + second

    coxeter = first_reflection * second_reflection
    assert coxeter * coxeter * coxeter == lattice.Aut().one()
    assert coxeter != lattice.Aut().one()


def test_archived_a2_root_sign_partition_is_exact() -> None:
    lattice = Lattices(ZZ)("A2")
    roots = lattice.roots()
    positive = roots.condition_set(lambda root: root.is_positive_root())
    negative = roots.condition_set(lambda root: root.is_negative_root())

    assert roots.cardinality() == 6
    assert positive.cardinality() == 3
    assert negative.cardinality() == 3
    positive_heights = Set(root.height() for root in positive)
    negative_heights = Set(root.height() for root in negative)
    assert positive_heights.cardinality() == 2
    assert ZZ(1) in positive_heights and ZZ(2) in positive_heights
    assert negative_heights.cardinality() == 2
    assert ZZ(-1) in negative_heights and ZZ(-2) in negative_heights
    assert all(-root in negative for root in positive)
