r"""The class sums of a group ring are the sums over the group's conjugacy classes.

For a finite group \(G\), the centre \(Z(R[G])\) has the class sums
\(\sum_{h\in C} h\) over the conjugacy classes \(C\) of \(G\) as an
\(R\)-basis, so it is spanned by them and its rank is the number of classes
(Isaacs, *Character Theory of Finite Groups*, Theorem 2.4).  A conjugacy class
is an orbit of the group's conjugation action \(g.x = g\,x\,g^{-1}\), which
``G.conjugacy_classes()`` presents as its orbit set, and the class sum is the
group algebra's ``class_sum`` of that orbit: the module's linear combination
with coefficient one on the orbit's points.  The orbit is the argument, so a
set of group elements closed up beside the group's operation is not a
conjugacy class and has no class sum.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def _symmetric_three():
    r"""\(QQ[S_3]\) with the conjugacy classes of \(S_3\) and its centre.

    \(S_3\) is the smallest group whose group-algebra centre is a proper
    subalgebra: its three classes have sizes 1, 3 and 2, so a class sum is a
    sum of more than one group element.
    """
    group = Groups.S(3)
    algebra = QQ[group]
    return group, algebra, algebra.center()


def _three_element_class(group):
    r"""The class of the transpositions, the class of \(S_3\) that is closed up nontrivially."""
    return next(
        conjugacy_class
        for conjugacy_class in group.conjugacy_classes()
        if conjugacy_class.cardinality() == 3
    )


def test_the_centre_has_one_basis_element_per_conjugacy_class() -> None:
    r"""\(\dim Z(QQ[S_3])\) is the number of conjugacy classes of \(S_3\), three."""
    group, algebra, center = _symmetric_three()
    assert center.dimension() == group.conjugacy_classes().cardinality()


def test_the_class_sums_of_the_conjugacy_classes_are_a_basis_of_the_centre() -> None:
    r"""The class sums \(\sum_{h\in C} h\) are the centre's basis.

    Each class sum is the inclusion of a basis element of the centre and
    distinct classes have distinct class sums, so the three of them span a
    three-dimensional centre: the class sums are the basis whose existence
    Isaacs, *Character Theory of Finite Groups*, Theorem 2.4 states, not merely
    three central elements.
    """
    group, algebra, center = _symmetric_three()
    inclusion = algebra.center_inclusion()
    class_sums = tuple(
        algebra.class_sum(conjugacy_class)
        for conjugacy_class in group.conjugacy_classes()
    )
    images = tuple(inclusion(element) for element in center.module_generators())

    assert all(class_sum in images for class_sum in class_sums)
    assert all(
        earlier != later
        for index, earlier in enumerate(class_sums)
        for other_index, later in enumerate(class_sums)
        if index < other_index
    )
    assert sum(class_sums) == algebra.linear_combination(
        {group_element: QQ.one() for group_element in group}
    )


def test_a_class_closed_up_by_hand_is_not_a_class_sum() -> None:
    r"""A class is the group's conjugation orbit, not a set with the same members.

    \(\{(1\,2)^{g} : g\in S_3\}\) has the three transpositions as members, and
    the group's orbit of \((1\,2)\) has the same three; the class sum is the
    orbit's, because the orbit is what the group's conjugation action gives.
    A set closed up beside that action is refused as the argument of
    ``class_sum``: the two are the same set of elements and only one of them is
    the group's class, so the operation cannot decide it by comparing members.
    """
    group, algebra, center = _symmetric_three()
    conjugacy_class = _three_element_class(group)
    closed_by_hand = frozenset(
        group_element * conjugacy_class.representative() * group_element.inverse()
        for group_element in group
    )

    assert closed_by_hand == frozenset(conjugacy_class.points())
    with pytest.raises(ValueError):
        algebra.class_sum(closed_by_hand)


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
    associative \(QQ\)-algebras, so the arrow is one of that category's Mor --
    the Hom of its own endpoints, which is where an arrow between two algebras
    lives -- and it carries the unit law; a linear map into the group algebra
    that merely happens to send the centre's sum to the right element is not
    what is asserted here.
    """
    group, algebra, center = _symmetric_three()
    inclusion = algebra.center_inclusion()
    first, second = tuple(center.module_generators())[:2]
    unital = Algebras(QQ).Associative().Unital()

    assert inclusion.parent() is center.Mor(algebra)
    assert inclusion in unital.Mor(center, algebra)
    assert inclusion.domain() is center
    assert inclusion.codomain() is algebra
    assert inclusion.preserves_unit()
    assert inclusion(center.one()) == algebra.one()
    assert inclusion(first * second) == inclusion(first) * inclusion(second)
