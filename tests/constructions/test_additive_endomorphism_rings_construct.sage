r"""Endomorphisms of a finite-dimensional vector space form the composition algebra."""

from sage_extensions.all import *  # noqa: F401,F403


def test_endomorphism_ring_has_identity_composition_and_scalar_center() -> None:
    module = QQ.free_module(2)
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)
    endomorphisms = module.End()
    identity = endomorphisms.identity()
    swap = endomorphisms({0: e1, 1: e0})
    double_identity = endomorphisms.scalar_multiple(QQ(2), identity)
    multiplication = endomorphisms.multiplication()
    classifier = endomorphisms.multiplication_morphism()

    assert endomorphisms.associativity_decision() is True
    assert endomorphisms.unit_laws_decision() is True
    assert endomorphisms.one() == identity
    assert not endomorphisms.is_commutative()
    assert endomorphisms.is_central(double_identity)
    assert double_identity(e0) == 2 * e0
    assert multiplication(identity, swap) == swap
    assert multiplication(swap, identity) == swap
    assert classifier.codomain() is endomorphisms
    assert endomorphisms.unformed_module() is module.Mor(module)
    assert isinstance(identity, endomorphisms.ElementType)

