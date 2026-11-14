r"""Fixed-source primitive embeddings of rank two.

A primitive U in 2U has unimodular even complement of signature (1,1), so U,
and no glue: one class, pointwise stabilizer O(U) of order four. A primitive
U(2) in 2U has complement U(2), and the two anti-isometries of the
discriminant forms differ by the surjective image of O(U(2)): one class.
"""

from sage_extensions.all import *
from sage_extensions.categories.abstract_categories.arrow_categories import CosliceCategory
from sage_indefinite_port.indefinite.marked_lattices import automorphism_group_generators, isometry, primitive_marking_classes


def _two_u():
    hyperbolic = Lattices(ZZ)("U")
    return hyperbolic, hyperbolic + hyperbolic


def test_hyperbolic_plane_has_one_fixed_source_class_and_order_four_stabilizer():
    source, ambient = _two_u()
    category = CosliceCategory(Lattices(ZZ), source)
    classes = tuple(primitive_marking_classes(category, source, ambient))
    assert len(classes) == 1
    generators = tuple(automorphism_group_generators(category, classes[0]))
    assert ambient.O().subgroup(generators).cardinality() == cardinal(4)


def test_scaled_hyperbolic_plane_has_one_fixed_source_class():
    _, ambient = _two_u()
    source = Lattices(ZZ)("U").twist(2)
    category = CosliceCategory(Lattices(ZZ), source)
    assert len(tuple(primitive_marking_classes(category, source, ambient))) == 1


def test_fixed_source_transporter_exchanges_the_summands():
    source, ambient = _two_u()
    e, f, u, v = tuple(ambient.module_generators())
    category = CosliceCategory(Lattices(ZZ), source)
    first = category.object(source.hom([e, f], codomain=ambient))
    second = category.object(source.hom([u, v], codomain=ambient))
    witness = isometry(category, first, second)
    assert witness(e) == u and witness(f) == v
