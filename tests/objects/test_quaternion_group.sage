from sage_extensions.all import *


def q8():
    return Groups.Q()


def test_the_presentation_of_q8() -> None:
    r"""$Q_8 = \langle i, j \mid i^4, i^2j^{-2}, jij^{-1}i\rangle$ (Dummit--Foote §6.3)."""
    free = Groups.Free(2)
    i, j = free.group_generators()
    presented = free.quotient_by_relators([i ^ 4, i ^ 2 * j ^ -2, j * i * j ^ -1 * i])
    assert presented.order() == 8
    assert presented.is_isomorphic_to(q8())


def test_the_categories_of_q8() -> None:
    group = q8()
    assert group in Groups()
    assert group in FiniteGroups()
    assert group not in AbelianGroups()


def test_the_invariants_of_q8() -> None:
    r"""$Z(Q_8) = \{\pm1\} = [Q_8, Q_8]$; five conjugacy classes; six subgroups."""
    group = q8()
    assert group.order() == 8
    assert not group.is_abelian()
    assert group.center().order() == 2
    assert group.commutator_subgroup().order() == 2
    assert group.conjugacy_classes_representatives().cardinality() == 5
    assert Groups().Subobjects(group).cardinality() == 6


def test_q8_is_not_the_dihedral_group() -> None:
    r"""$Q_8$ has one element of order two, $D_4$ has five."""
    assert not q8().is_isomorphic_to(Groups.D(4))


def test_the_abelianization_of_q8() -> None:
    r"""$Q_8/\{\pm1\} \cong V_4$."""
    abelianization = Groups().abelianization()(q8())
    assert abelianization.order() == 4
    assert abelianization.is_isomorphic_to(Groups.V4())
    assert q8().Mor(Groups.C(2)).cardinality() == 4


def test_the_automorphism_group_of_q8() -> None:
    r"""$\operatorname{Aut}(Q_8) \cong S_4$."""
    group = q8()
    automorphisms = group.Aut()
    identity = automorphisms.one()
    assert automorphisms in Groups()
    assert automorphisms.order() == 24
    assert automorphisms.is_isomorphic_to(Groups.S(4))
    assert identity(group.an_element()) == group.an_element()


def test_q8_has_one_endomorphism_category() -> None:
    group = q8()
    endomorphisms = group.Mor(group)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert group.Mor(group) is endomorphisms
    assert identity * identity == identity
