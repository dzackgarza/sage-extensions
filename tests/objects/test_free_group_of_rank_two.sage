from sage_extensions.all import *


def f2():
    return Groups.Free(2)


def test_the_free_group_functor_agrees() -> None:
    assert Sets().free_group()(Sets.Δ[1]).is_isomorphic_to(f2())


def test_the_categories_of_f2() -> None:
    group = f2()
    assert group in Groups()
    assert group in FinitelyGeneratedGroups()
    assert group in FinitelyPresentedGroups()
    assert group not in FiniteGroups()


def test_the_invariants_of_f2() -> None:
    group = f2()
    a, b = group.group_generators()
    assert group.group_generators().cardinality() == 2
    assert not group.is_finite()
    assert group.cardinality() == aleph0
    assert not group.is_abelian()
    assert a * b != b * a
    assert a * a.inverse() == group.one()


def test_the_abelianization_of_f2() -> None:
    r"""$F_2^{ab} = \mathbb Z^2$."""
    abelianization = Groups().abelianization()(f2())
    assert not abelianization.is_finite()
    assert abelianization.is_isomorphic_to(Groups.Abelian([0, 0]))


def test_homomorphisms_out_of_f2_are_pairs_of_elements() -> None:
    r"""$\operatorname{Hom}(F_2, G) = G^2$: $2^2 = 4$ into $C_2$ and $6^2 = 36$ into $S_3$."""
    assert f2().Mor(Groups.C(2)).cardinality() == 4
    assert f2().Mor(Groups.S(3)).cardinality() == 36


def test_the_automorphism_group_of_f2() -> None:
    r"""$\operatorname{Aut}(F_2)$ contains the Nielsen maps $a \mapsto ab^k$, one for each $k$."""
    automorphisms = f2().Aut()
    assert automorphisms in Groups()
    assert not automorphisms.is_finite()


def test_f2_has_one_endomorphism_category() -> None:
    group = f2()
    endomorphisms = group.Mor(group)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert group.Mor(group) is endomorphisms
    assert identity * identity == identity
