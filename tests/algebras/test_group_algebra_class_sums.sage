r"""The class sums of a group ring are the sums over the group's conjugacy classes.

For a finite group \(G\), the centre \(Z(R[G])\) has the class sums
\(\sum_{h\in C} h\) over the conjugacy classes \(C\) of \(G\) as an
\(R\)-basis, so it is spanned by them and its rank is the number of classes
(Isaacs, *Character Theory of Finite Groups*, Theorem 2.4).  A conjugacy class
is an orbit of the group's own conjugation action: ``G.conjugacy_classes()`` is
that action's orbit set, and the class sum is the module's linear combination
with coefficient one on one of those orbits.

For a finite group a class closed up by hand beside that orbit has the same
elements, so no comparison of values tells the two routes apart, and this
repository's test rules refuse a mock of the group's method.  What these tests
pin is therefore the class data the centre must carry -- the rank, the sums
themselves, their centrality as one equality of endomorphisms, and the
category of the inclusion -- which is what a repaired route has to keep; the
route itself is stated where it is taken, at ``_finite_group_algebra_center``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _symmetric_three():
    r"""\(QQ[S_3]\) with the conjugacy classes of \(S_3\) and its centre.

    \(S_3\) is the smallest group whose group-algebra centre is a proper
    subalgebra: its three classes have sizes 1, 3 and 2, so a class sum is a
    sum of more than one group element.
    """
    group = Groups.S(3)
    algebra = QQ[group]
    return group, algebra, algebra.center()


def test_the_centre_has_one_basis_element_per_conjugacy_class() -> None:
    r"""\(\dim Z(QQ[S_3])\) is the number of conjugacy classes of \(S_3\), three."""
    group, algebra, center = _symmetric_three()
    assert center.dimension() == group.conjugacy_classes().cardinality()


def test_each_group_conjugacy_class_has_its_class_sum_in_the_centre_basis() -> None:
    r"""\(\sum_{h\in C} h\) is a basis element of \(Z(QQ[S_3])\) for every class \(C\).

    The class is read from the group's conjugation orbit, and the class sum is
    the centre's basis element that the centre's inclusion carries into
    \(QQ[S_3]\) as that sum: coefficient one on the orbit and zero off it,
    compared as elements of the group algebra.
    """
    group, algebra, center = _symmetric_three()
    inclusion = algebra.center_inclusion()
    class_sums = tuple(center.module_generators())
    for conjugacy_class in group.conjugacy_classes():
        class_sum = algebra.linear_combination(
            {
                group_element: QQ.one()
                for group_element in conjugacy_class.points()
            }
        )
        assert any(class_sum == inclusion(element) for element in class_sums)


def test_each_basis_element_of_the_centre_is_central() -> None:
    r"""\(g\sum_{h\in C} h = \sum_{h\in C} h\, g\) for every \(g\in S_3\).

    Centrality of \(c\) is the equality, in the endomorphism ring of
    \(QQ[S_3]\), of the two endomorphisms \(x\mapsto xc\) and \(x\mapsto cx\):
    one equality of arrows rather than a comparison of images over a listed
    family of group elements.  The transposition is the negative control, so
    the equality is not one that holds of any element.
    """
    group, algebra, center = _symmetric_three()
    inclusion = algebra.center_inclusion()
    endomorphisms = algebra.module_category().Mor(algebra, algebra)

    def is_central(element):
        r"""Whether left and right multiplication by ``element`` are one arrow."""
        return endomorphisms.elementwise(
            lambda other: other * element
        ) == endomorphisms.elementwise(lambda other: element * other)

    assert all(
        is_central(inclusion(element)) for element in center.module_generators()
    )
    assert not is_central(algebra(group((1, 2))))


def test_the_centre_inclusion_is_a_map_of_unital_algebras() -> None:
    r"""\(Z(QQ[S_3])\hookrightarrow QQ[S_3]\) preserves the product and the unit.

    The centre's product is the ambient product read back along the inclusion
    and its unit is that inclusion's lift of \(1\), so the inclusion is an
    algebra map by construction: it sends \(1\) to \(1\), and the product of
    two basis elements to the product of their images (Isaacs, *Character
    Theory of Finite Groups*, Theorem 2.4).  Both endpoints are unital
    associative \(QQ\)-algebras, so the arrow is one of that category's Mor
    and carries the unit law; a linear map into the group algebra that merely
    happens to send the centre's sum to the right element is not what is
    asserted here.
    """
    group, algebra, center = _symmetric_three()
    inclusion = algebra.center_inclusion()
    first, second = tuple(center.module_generators())[:2]
    unital = Algebras(QQ).Associative().Unital()

    assert inclusion in unital.Mor(center, algebra)
    assert inclusion.domain() is center
    assert inclusion.codomain() is algebra
    assert inclusion.preserves_unit()
    assert inclusion(center.one()) == algebra.one()
    assert inclusion(first * second) == inclusion(first) * inclusion(second)
