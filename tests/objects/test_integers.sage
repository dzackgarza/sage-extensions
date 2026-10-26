from sage_extensions.all import *


def test_the_integers_are_the_initial_ring() -> None:
    r"""$\mathbb Z$ is initial in rings: there is exactly one ring map $\mathbb Z \to R$."""
    assert Rings().initial_object() is ZZ
    assert ZZ.Mor(GF(5)).cardinality() == 1
    assert ZZ.Mor(QQ).cardinality() == 1


def test_the_integers_are_the_ring_of_integers_of_the_rationals() -> None:
    assert NumberFields().ring_of_integers()(QQ) is ZZ


def test_the_categories_of_the_integers() -> None:
    assert ZZ in Rings()
    assert ZZ in CommutativeRings()
    assert ZZ in IntegralDomains()
    assert ZZ in PrincipalIdealDomains()
    assert ZZ in NoetherianRings()
    assert ZZ in Algebras(ZZ)
    assert ZZ in CountablyInfiniteSets()


def test_the_integers_as_an_algebra_over_themselves() -> None:
    r"""The structure morphism of $\mathbb Z$ over itself is $\mathrm{id}_{\mathbb Z}$."""
    assert ZZ.algebra_structure_morphism() == ZZ.Mor(ZZ).identity()
    assert ZZ.algebra_base_ring() is ZZ


def test_the_invariants_of_the_integers() -> None:
    assert ZZ.cardinality() == aleph0
    assert ZZ.krull_dimension() == 1
    assert ZZ.fraction_field() is QQ
    assert ZZ.regular_module().module_rank() == 1
    assert ZZ.quotient_ring(ZZ.ideal(6)).cardinality() == 6


def test_the_automorphisms_of_the_integers() -> None:
    assert ZZ.Aut().order() == 1
    assert ZZ.End().cardinality() == 1


def test_the_kahler_differentials_of_the_integers_over_themselves_vanish() -> None:
    assert ZZ.kahler_differentials().cardinality() == 1


def test_the_integers_have_one_endomorphism_category() -> None:
    endomorphisms = ZZ.Mor(ZZ)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert ZZ.Mor(ZZ) is endomorphisms
    assert identity * identity == identity
    assert identity.domain() is ZZ
