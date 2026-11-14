r"""Stabilizers of a primitive nondegenerate sublattice through complement and glue.

Issue 47 example: L=U, S=Z(e+f)=<2>, K=Z(e-f)=<-2>, glue of order two, trivial
action on Z/2 factors. The setwise stabilizer has order 4 and the pointwise
stabilizer of e+f has order 2, {id, e<->f}.

For U+A1 and S the A1 summand, L=S+K with no glue: setwise order 8, pointwise 4.
"""

from sage_extensions.all import *


def _arrow(ambient, *vectors):
    return ambient.subobject_on(vectors).inclusion()


def _order(group, generators):
    return group.subgroup(tuple(generators)).cardinality()


def test_glued_plane_in_u_has_issue_47_stabilizer_orders():
    ambient = Lattices(ZZ)("U")
    e, f = tuple(ambient.module_generators())
    embedding = _arrow(ambient, e + f)
    group = ambient.O()
    assert group.setwise_stabilizer(embedding).cardinality() == cardinal(4)
    assert group.pointwise_stabilizer(embedding).cardinality() == cardinal(2)


def test_summand_of_u_plus_a1_has_split_stabilizers():
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    e, f, x = tuple(ambient.module_generators())
    embedding = _arrow(ambient, x)
    group = ambient.O()
    setwise = tuple(group.setwise_stabilizer(embedding).group_generators())
    pointwise = tuple(group.pointwise_stabilizer(embedding).group_generators())
    assert group.subgroup(setwise).cardinality() == cardinal(8)
    assert group.subgroup(pointwise).cardinality() == cardinal(4)
    assert all(element(x) == x for element in pointwise)
    assert all(element(x) in (x, -x) for element in setwise)


def test_nonprimitive_sublattice_keeps_only_its_index_two_stabilizer():
    r"""S=<x1,2*x2> in U+A1+A1 has saturation <x1,x2>, stabilized by order 32; the swap is excluded."""
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("A1") + Lattices(ZZ)("A1")
    e, f, x1, x2 = tuple(ambient.module_generators())
    group = ambient.O()
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    embedding = _arrow(ambient, x1, x2 + x2)
    setwise = tuple(group.setwise_stabilizer(embedding).group_generators())
    assert group.subgroup(setwise).cardinality() == cardinal(16)


def test_transporter_carries_a_summand_to_its_translate():
    r"""The Eichler transvection sends x to x+2e of the same square: S'=Z(x+2e) is equivalent."""
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    e, f, x = tuple(ambient.module_generators())
    moved = x + e + e
    assert ambient.q(moved) == ambient.q(x)
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    first = arrows.object(_arrow(ambient, x))
    second = arrows.object(_arrow(ambient, moved))
    from sage_indefinite_port.indefinite.marked_lattices import isometry

    witness = isometry(arrows, first, second)
    assert witness(x) in (moved, -moved)
    assert all(ambient.b(witness(p), witness(q)) == ambient.b(p, q) for p in (e, f, x) for q in (e, f, x))
