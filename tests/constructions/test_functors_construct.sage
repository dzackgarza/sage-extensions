r"""Functors and adjunctions a mathematician expects to apply.

Each functor with a resolved domain is applied to that domain's witness and
lands in its codomain; each adjunction has a unit and a counit with the right
endpoints and a hom-set bijection that round-trips.  Functors over a base ring
are taken over every commutative ring in the catalogue.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

NULLARY_FUNCTORS = {
}


@pytest.mark.parametrize("name", sorted(NULLARY_FUNCTORS))
def test_a_nullary_functor_sends_an_object_into_its_codomain(name) -> None:
    constructor, specimen, codomain = NULLARY_FUNCTORS[name]
    functor = constructor()
    source = specimen()
    image = functor(source)
    assert source in functor.domain()
    if codomain is not None:
        assert image in codomain()
    assert image in functor.codomain()
    identity = source.Mor(source).identity()
    image_of_identity = functor(identity)
    assert image_of_identity.domain() == image
    assert image_of_identity.codomain() == image


def test_known_values_of_the_nullary_functors() -> None:
    assert Groups().abelianization()(Groups.S(3)).order() == 2
    assert Sets().cardinality_functor()(Sets.Δ[2]) == cardinal(3)
    assert FiniteSets().power_set_functor()(Sets.Δ[2]).cardinality() == cardinal(8)
    assert Sets().free_group()(Sets.Δ[1]).is_isomorphic_to(Groups.Free(2))
    assert Groups().underlying_set()(Groups.S(3)).cardinality() == cardinal(6)
    assert NumberFields().ring_of_integers()(QQ) is ZZ
    assert IntegralDomains().fraction_field()(ZZ) is QQ
    gaussian = NumberFields().ring_of_integers()(QuadraticField(-1, "i"))
    assert gaussian in OwnedOrders()
    assert gaussian.is_maximal()
    assert gaussian.module_rank() == cardinal(2)


def test_functors_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    polynomials = ring.polynomial_ring("x")

    free = Sets().free_module(ring)(Sets.Δ[2])
    assert free in FreeModules(ring)
    assert free.module_rank() == cardinal(3)
    assert Modules(ring).underlying_set()(module) in Sets()
    assert Modules(ring).dualization()(module).module_rank() == cardinal(2)
    assert Modules(ring).symmetric_algebra()(module) in Algebras(ring).Associative().Unital().Commutative()
    assert Modules(ring).tensor_algebra()(module) in Algebras(ring)
    assert Modules(ring).exterior_algebra()(module).graded_piece(2).module_rank() == cardinal(1)
    assert Algebras(ring).Associative().Unital().Commutative().spectrum()(polynomials) in AffineSchemes(ring)
    assert Algebras(ring).Associative().Unital().Commutative().spectrum()(polynomials).relative_dimension() == 1
    assert Algebras(ring).Associative().Unital().Commutative().de_rham()(polynomials) in StrictlyCommutativeDifferentialGradedAlgebras(ring)


def test_free_forgetful_adjunction_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    adjunction = Sets().free_module_adjunction(ring)
    labels = Sets.Δ[1]
    free = adjunction.left_adjoint()(labels)
    module = ring.free_module(3)

    unit = adjunction.unit(labels)
    assert unit.domain() is labels
    assert unit.codomain() == adjunction.right_adjoint()(free)
    assert unit.is_injective()
    counit = adjunction.counit(module)
    assert counit.codomain() is module
    assert counit.is_surjective()

    phi = free.Mor(module)({0: module.module_generator(0), 1: 2 * module.module_generator(2)})
    transpose = adjunction.hom_set_isomorphism_forward(phi, labels)
    assert transpose(labels(1)) == 2 * module.module_generator(2)
    recovered = adjunction.hom_set_isomorphism_inverse(transpose, module)
    assert recovered == phi


def test_algebra_adjunctions_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    for adjunction in (Modules(ring).symmetric_algebra_adjunction(), Modules(ring).tensor_algebra_adjunction()):
        algebra = adjunction.left_adjoint()(module)
        unit = adjunction.unit(module)
        assert unit.domain() is module
        assert unit.codomain() == adjunction.right_adjoint()(algebra)
        assert unit.is_injective()
        counit = adjunction.counit(algebra)
        assert counit.codomain() is algebra


def test_de_rham_adjunction_over_every_field(field) -> None:
    adjunction = Algebras(field).Associative().Unital().Commutative().de_rham_adjunction()
    polynomials = field.polynomial_ring("x")
    de_rham = adjunction.left_adjoint()(polynomials)
    assert adjunction.right_adjoint()(de_rham) is polynomials
    assert adjunction.unit(polynomials).domain() is polynomials
    assert adjunction.counit(de_rham).codomain() is de_rham


def test_group_and_number_field_adjunctions() -> None:
    abelianization = Groups().abelianization_adjunction()
    symmetric = Groups.S(3)
    unit = abelianization.unit(symmetric)
    assert unit.domain() is symmetric
    assert unit.is_surjective()
    assert unit.codomain().order() == 2

    free = Sets().free_group_adjunction()
    letters = Sets.Δ[1]
    assert free.unit(letters).domain() is letters
    assert free.unit(letters).is_injective()
    assert free.counit(symmetric).is_surjective()

    orders = Orders().number_field_adjunction()
    assert orders.left_adjoint()(ZZ) is QQ
    assert orders.right_adjoint()(QQ) is ZZ
    assert orders.unit(ZZ).domain() is ZZ
    assert orders.counit(QQ).codomain() is QQ
    assert QQ in Fields()
