r"""Ring maps, and moving modules, algebras, forms and lattices along them.

Extension and restriction of scalars along the ring maps a mathematician
reaches for first, the base-change adjunction and its Hom bijection,
localization of modules, twisting by Frobenius, and the tensor–Hom
adjunction over every commutative ring.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

RING_MAPS = {
    "ZZ->QQ": (lambda: ZZ, lambda: QQ, True, 0),
    "ZZ->GF(5)": (lambda: ZZ, lambda: GF(5), False, 5),
    "ZZ->ZZ_3": (lambda: ZZ, lambda: Zp(3), True, 0),
    "ZZ->ZZ[i]": (lambda: ZZ, lambda: QuadraticField(-1, "i").ring_of_integers(), True, 0),
    "QQ->QQ(i)": (lambda: QQ, lambda: QuadraticField(-1, "i"), True, 0),
    "ZZ->ZZ[x]": (lambda: ZZ, lambda: ZZ.polynomial_ring("x"), True, 0),
    "GF(5)->GF(25)": (lambda: GF(5), lambda: GF(25), True, 0),
}


@pytest.fixture(params=sorted(RING_MAPS), ids=str)
def ring_map(request):
    source, target, injective, kernel_generator = RING_MAPS[request.param]
    source, target = source(), target()
    return source.Mor(target)(lambda element: target(element)), injective, kernel_generator


def test_a_ring_map_is_a_ring_morphism(ring_map) -> None:
    phi, injective, kernel_generator = ring_map
    source, target = phi.domain(), phi.codomain()
    assert phi in source.Mor(target)
    assert phi(source.one()) == target.one()
    assert phi(source(2) + source(3)) == phi(source(2)) + phi(source(3))
    assert phi(source(2) * source(3)) == phi(source(2)) * phi(source(3))
    assert phi.is_injective() == injective
    assert phi.kernel() == source.ideal(source(kernel_generator))


def test_extension_of_scalars_of_a_free_module(ring_map) -> None:
    phi, _, _ = ring_map
    source, target = phi.domain(), phi.codomain()
    module = source.free_module(3)
    extended = module.base_change(phi)
    functorial = Modules(source).scalar_extension(phi)(module)

    assert extended in Modules(target)
    assert extended in FinitelyGeneratedModules(target)
    assert extended.module_rank() == cardinal(3)
    assert extended.base_ring() is target
    assert functorial == extended
    if target in Fields():
        assert extended in VectorSpaces(target)


def test_extension_of_scalars_of_a_torsion_module_over_the_integers() -> None:
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((6,))
    for name, size in (("ZZ->QQ", 1), ("ZZ->GF(5)", 1), ("ZZ->ZZ_3", 3), ("ZZ->ZZ[i]", 36)):
        source, target, _, _ = RING_MAPS[name]
        target = target()
        phi = ZZ.Mor(target)(lambda element, target=target: target(element))
        extended = torsion.base_change(phi)
        assert extended in Modules(target)
        assert extended.cardinality() == cardinal(size)
    two = ZZ.Mor(GF(2))(lambda element: GF(2)(element))
    assert torsion.base_change(two).cardinality() == cardinal(2)
    assert torsion.base_change(two).module_rank() == cardinal(1)


def test_scalar_extension_distinguishes_surviving_and_vanishing_torsion_and_maps() -> None:
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((2,))
    mod_two = ZZ.Mor(GF(2))(lambda element: GF(2)(element))
    rational = ZZ.Mor(QQ)(lambda element: QQ(element))

    over_f2 = Modules(ZZ).scalar_extension(mod_two)(torsion)
    over_q = Modules(ZZ).scalar_extension(rational)(torsion)

    assert over_f2.is_zero() is False
    assert over_f2.module_generator(0) != over_f2.zero()
    assert over_q.is_zero() is True

    line = ZZ.free_module(("e",))
    e = line.module_generator("e")
    doubling = line.Mor(line)({"e": 2 * e})
    changed_doubling = Modules(ZZ).scalar_extension(mod_two)(doubling)
    zero_map = changed_doubling.domain().module_category().Mor(
        changed_doubling.domain(), changed_doubling.codomain()
    ).zero()

    assert doubling.base_change(mod_two) is changed_doubling
    assert changed_doubling == zero_map
    assert changed_doubling(
        changed_doubling.domain().module_generator("e")
    ) == changed_doubling.codomain().zero()


def test_scalar_extension_identity_and_composition_have_explicit_comparisons() -> None:
    module = ZZ.free_module(("e", "f"))

    identity_extension = Modules(ZZ).scalar_extension(ZZ.Mor(ZZ).identity())
    identity_comparison = identity_extension.identity_comparison(module)
    identity = module.module_category().Mor(module, module).identity()
    assert identity_comparison.domain() is module
    assert identity_comparison.codomain() is module
    assert identity_comparison.forward() == identity
    assert identity_comparison.inverse() == identity

    middle = GF(5)
    target = GF(25)
    first_map = ZZ.Mor(middle)(lambda scalar: middle(scalar))
    second_map = middle.Mor(target)(lambda scalar: target(scalar))
    first_extension = Modules(ZZ).scalar_extension(first_map)
    comparison = first_extension.composition_comparison(second_map, module)
    composite_map = first_extension.composite_ring_map(second_map)
    direct = Modules(ZZ).scalar_extension(composite_map)(module)
    iterated = Modules(middle).scalar_extension(second_map)(first_extension(module))

    assert first_extension.composite_ring_map(second_map) is composite_map
    assert composite_map.domain() is ZZ
    assert composite_map.codomain() is target
    assert comparison.domain() is direct
    assert comparison.codomain() is iterated
    for label in module.module_generating_set():
        direct_generator = direct.module_generator(label)
        iterated_generator = iterated.module_generator(label)
        assert comparison.forward()(direct_generator) == iterated_generator
        assert comparison.inverse()(iterated_generator) == direct_generator


def test_restriction_of_scalars(ring_map) -> None:
    phi, _, _ = ring_map
    source, target = phi.domain(), phi.codomain()
    module = target.free_module(2)
    restricted = Modules(target).restriction_of_scalars(phi)(module)
    also = module.restrict_scalars(phi)

    assert restricted in Modules(source)
    assert also in Modules(source)
    assert restricted.cardinality() == module.cardinality()
    if target.cardinality().is_finite():
        assert restricted.cardinality() == cardinal(target.cardinality() ** 2)


def test_restriction_of_scalars_of_the_gaussian_integers_to_the_integers() -> None:
    gaussian = QuadraticField(-1, "i").ring_of_integers()
    phi = ZZ.Mor(gaussian)(lambda element: gaussian(element))
    restricted = gaussian.free_module(1).restrict_scalars(phi)
    assert restricted in Modules(ZZ)
    assert restricted.module_rank() == cardinal(2)
    assert restricted in FinitelyGeneratedModules(ZZ)
    rationals = QQ.free_module(1).restrict_scalars(ZZ.Mor(QQ)(lambda element: QQ(element)))
    assert rationals in Modules(ZZ)
    assert rationals not in FinitelyGeneratedModules(ZZ)


def test_the_base_change_adjunction(ring_map) -> None:
    phi, _, _ = ring_map
    source, target = phi.domain(), phi.codomain()
    adjunction = Modules(source).base_change_adjunction(phi)
    module = source.free_module(2)
    target_module = target.free_module(1)
    extended = adjunction.left_adjoint()(module)
    restricted = adjunction.right_adjoint()(target_module)

    assert extended in Modules(target)
    assert restricted in Modules(source)
    unit = adjunction.unit(module)
    assert unit.domain() is module
    assert unit.codomain() == adjunction.right_adjoint()(extended)
    counit = adjunction.counit(target_module)
    assert counit.codomain() is target_module
    assert counit.is_surjective()
    forward = extended.Mor(target_module)(
        {0: target_module.module_generator(0), 1: 2 * target_module.module_generator(0)}
    )
    transposed = adjunction.hom_set_isomorphism_forward(forward, module)
    assert transposed.domain() is module
    assert transposed(module.module_generator(1)) == restricted(2 * target_module.module_generator(0))
    assert adjunction.hom_set_isomorphism_inverse(transposed, target_module) == forward


def test_extension_of_scalars_of_an_algebra(ring_map) -> None:
    phi, _, _ = ring_map
    source, target = phi.domain(), phi.codomain()
    polynomials = source.polynomial_ring("x")
    extended = Algebras(source).Associative().Unital().Commutative().scalar_extension(phi)(polynomials)
    assert extended in Algebras(target).Associative().Unital().Commutative()
    assert extended.algebra_generators().cardinality() == cardinal(1)
    assert (extended in IntegralDomains()) == (target in IntegralDomains())
    adjunction = Algebras(source).Associative().Unital().Commutative().base_change_adjunction(phi)
    assert adjunction.left_adjoint()(polynomials) == extended
    assert adjunction.unit(polynomials).domain() is polynomials


def test_base_change_of_a_lattice_and_of_a_form(ring_map) -> None:
    phi, _, _ = ring_map
    source, target = phi.domain(), phi.codomain()
    lattice = Lattices(source)([[2, 1], [1, 2]])
    changed = lattice.base_change(phi)
    assert changed in Lattices(target)
    assert changed in BilinearFormModules(target)
    assert changed.module_rank() == cardinal(2)
    assert changed.determinant() == 3 * target.one()
    assert changed.is_nondegenerate() == (3 * target.one() != target.zero())


def test_localization_of_modules_at_a_prime_of_the_integers() -> None:
    local = ZZ.localize_at_prime(5)
    localize = local.localization_functor()
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((6, 25))
    free = ZZ.free_module(2)

    assert localize(torsion) in Modules(local)
    assert localize(torsion).cardinality() == cardinal(25)
    assert localize(free).module_rank() == cardinal(2)
    assert localize(free).base_ring() is local
    doubling = free.Mor(free)({0: 2 * free.module_generator(0), 1: free.module_generator(1)})
    assert localize(doubling).is_surjective()
    assert not doubling.is_surjective()


def test_twisting_a_module_by_frobenius() -> None:
    field = GF(4)
    frobenius = field.Mor(field)(lambda element: element**2)
    module = field.free_module(2)
    twisted = module.twist_scalar_action(frobenius)
    generator = field.multiplicative_generator()
    assert twisted in Modules(field)
    assert twisted.module_rank() == cardinal(2)
    assert twisted.scalar_multiple(generator, twisted.module_generator(0)) == generator**2 * twisted.module_generator(0)
    assert frobenius * frobenius == field.Mor(field).identity()


def test_the_tensor_hom_adjunction_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    fixed = ring.free_module(2)
    adjunction = fixed.tensor_hom_adjunction()
    module = ring.free_module(3)
    other = ring.free_module(1)

    tensored = adjunction.left_adjoint()(module)
    homs = adjunction.right_adjoint()(other)
    assert tensored == module.tensor_product(fixed)
    assert homs == fixed.Mor(other)
    assert tensored.module_rank() == cardinal(6)
    assert homs.module_rank() == cardinal(2)
    assert adjunction.unit(module).domain() is module
    assert adjunction.counit(other).codomain() is other
    evaluation = tensored.Mor(other)({label: other.zero() for label in range(6)})
    transposed = adjunction.hom_set_isomorphism_forward(evaluation, module)
    assert transposed.domain() is module
    assert adjunction.hom_set_isomorphism_inverse(transposed, other) == evaluation
