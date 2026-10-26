r"""The functors and adjunctions whose domain is Grp, asked of Grp.

Each row states the functor's domain and codomain, its action on a group
morphism rather than only on objects, and the construction's own content on a
small specimen.  The adjunction states the endpoints of its unit and counit
and one triangle identity at a group generator.
"""

from sage_extensions.all import *


def test_the_abelianization_functor_kills_the_derived_subgroup() -> None:
    functor = Groups().abelianization()
    assert functor.domain() == Groups()
    assert functor.codomain() == AbelianGroups()

    symmetric = Groups.S(3)
    abelian = functor(symmetric)
    assert abelian in AbelianGroups()
    assert abelian.order() == 2

    projection = functor.quotient_projection(symmetric)
    assert projection.domain() is symmetric
    assert projection.codomain() is abelian
    three_cycle = next(
        element for element in symmetric.group_generators() if element.order() == 3
    )
    transposition = next(
        element for element in symmetric.group_generators() if element.order() == 2
    )
    assert projection(three_cycle) == abelian.one()
    assert projection(transposition) != abelian.one()

    carried = functor(symmetric.Mor(symmetric).identity())
    assert carried.domain() is abelian
    assert carried.codomain() is abelian
    assert carried(projection(transposition)) == projection(transposition)


def test_the_abelianization_adjunction_has_the_quotient_for_its_unit() -> None:
    adjunction = Groups().abelianization_adjunction()
    assert adjunction.left_adjoint().domain() == Groups()
    assert adjunction.left_adjoint().codomain() == AbelianGroups()
    assert adjunction.right_adjoint().domain() == AbelianGroups()
    assert adjunction.right_adjoint().codomain() == Groups()

    symmetric = Groups.S(3)
    unit = adjunction.unit(symmetric)
    assert unit.domain() is symmetric
    assert unit.codomain() is adjunction.left_adjoint()(symmetric)
    three_cycle = next(
        element for element in symmetric.group_generators() if element.order() == 3
    )
    assert unit(three_cycle) == unit.codomain().one()

    cyclic = Groups.C(2)
    counit = adjunction.counit(cyclic)
    assert counit.codomain() is cyclic
    assert counit.domain() is adjunction.left_adjoint()(cyclic)
    generator = cyclic.group_generators()[0]
    assert counit(adjunction.unit(cyclic)(generator)) == generator


