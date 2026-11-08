r"""Issue 48: contents of vectors and the doubled form of an odd lattice.

On U, v=e+4f is primitive of square 8 and w=2(e+f) has square 8 and content 2,
so they are inequivalent; content 2 selects the square-2 primitive stratum.
Square 7 has no content-2 stratum. 2e and 4e have different content.

On I_{2,1}, the discriminant group is trivial but that of (L,2b) is (Z/2)^3,
and the coordinate swap acts nontrivially only on the doubled group.
"""

from sage_extensions.all import *


def _marked(ambient, vector):
    source = Lattices(ZZ)([[vector.q()]])
    from sage_extensions.categories.abstract_categories.arrow_categories import CosliceCategory

    category = CosliceCategory(Lattices(ZZ), source)
    return category, category.object(source.hom([vector], codomain=ambient))


def test_content_strata_of_square_eight_in_u():
    ambient = Lattices(ZZ)("U")
    e, f = tuple(ambient.module_generators())
    group = ambient.O()
    assert group.vector_orbit_representatives(7, content=2).cardinality() == cardinal(0)
    stratum = tuple(group.vector_orbit_representatives(8, content=2))
    assert stratum and all(point.content() == 2 and ambient.q(point) == 8 for point in stratum)
    from sage_indefinite_port.indefinite.marked_lattices import isometry

    v, w = e + 4*f, 2*(e + f)
    category, marked_v = _marked(ambient, v)
    assert isometry(category, marked_v, category.object(marked_v.arrow().domain().hom([w], codomain=ambient))) is None


def test_null_vectors_of_different_content_are_inequivalent():
    ambient = Lattices(ZZ)("U")
    e, f = tuple(ambient.module_generators())
    from sage_indefinite_port.indefinite.marked_lattices import isometry

    source = Lattices(ZZ)([[0]])
    from sage_extensions.categories.abstract_categories.arrow_categories import CosliceCategory

    category = CosliceCategory(Lattices(ZZ), source)
    first = category.object(source.hom([2*e], codomain=ambient))
    second = category.object(source.hom([4*e], codomain=ambient))
    assert isometry(category, first, second) is None
    assert ambient.O().vector_orbit_representatives(0, content=3).cardinality() > cardinal(0)


def test_doubling_keeps_the_group_but_not_the_discriminant():
    ambient = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, -1]])
    doubled, functor = ambient.doubled_form()
    assert ambient.discriminant_group().cardinality() == cardinal(1)
    assert doubled.discriminant_group().cardinality() == cardinal(8)
    labels = tuple(ambient.module_generating_set())
    a, b, c = tuple(ambient.module_generators())
    swap = ambient.Aut()(dict(zip(labels, (b, a, c), strict=True)))
    doubled_swap = functor(swap)
    assert doubled_swap.discriminant_isometry() != doubled.O().one().discriminant_isometry()


def test_index_two_sublattices_of_a_hyperbolic_summand():
    r"""U in U+U has three index-two sublattices; O(U) exchanges <e,2f>, <2e,f> and fixes <e+f,2f>."""
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    e, f, _u, _v = tuple(ambient.module_generators())
    saturated = ambient.subobject_on((e, f)).inclusion()
    assert ambient.O().nonprimitive_sublattice_classes(saturated, (1, 2)).cardinality() == cardinal(2)
