r"""Module constructions a mathematician expects, over every named ring.

Free modules, duals, Homs, tensor and direct sums, subobjects, quotients,
presented and torsion modules, localization and base change: each is asked of
every ring in the catalogue for which the mathematics defines it, and the
claims are the ones that hold for that class of rings.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _free(ring, rank):
    return ring.free_module(rank)


# ---------------------------------------------------------------------------
# Free modules of finite rank.
# ---------------------------------------------------------------------------


def test_free_module_of_rank_three_over_every_ring(ring) -> None:
    module = _free(ring, 3)
    e0 = module.module_generator(0)

    assert module in Modules(ring)
    assert module in FreeModules(ring)
    assert module in FinitelyGeneratedFreeModules(ring)
    assert module in FinitelyGeneratedModules(ring)
    assert module in FinitelyPresentedModules(ring)
    assert module in ProjectiveModules(ring)
    assert module.base_ring() is ring
    assert module.module_rank() == cardinal(3)
    assert module.module_generators().cardinality() == cardinal(3)
    assert e0 + e0 == 2 * e0
    assert e0 - e0 == module.zero()
    assert ring.one() * e0 == e0
    assert module.is_free()
    assert module.is_finitely_generated()


def test_power_notation_builds_the_free_module(commutative_ring) -> None:
    ring = commutative_ring
    cube = ring**3
    assert cube in FinitelyGeneratedFreeModules(ring)
    assert cube.module_rank() == cardinal(3)
    assert (ring**0).module_rank() == cardinal(0)
    assert (ring**0).cardinality() == cardinal(1)


def test_the_zero_module(commutative_ring) -> None:
    zero = _free(commutative_ring, 0)
    assert zero.module_rank() == cardinal(0)
    assert zero.cardinality() == cardinal(1)
    assert zero.zero() == zero.an_element()


def test_free_module_over_a_field_is_a_vector_space(field) -> None:
    space = _free(field, 2)
    assert space in VectorSpaces(field)
    assert space in Modules(field)
    assert space.dual_module() in VectorSpaces(field)
    assert space.dual_module().module_rank() == cardinal(2)


@pytest.mark.parametrize(
    "name, size",
    [("GF(5)", 125), ("GF(4)", 64), ("ZZ/12", 12**3), ("GF(2)[t]/(t^2)", 64)],
)
def test_free_module_over_a_finite_ring_is_finite(build, name, size) -> None:
    assert _free(build(name), 3).cardinality() == cardinal(size)


@pytest.mark.parametrize("name", ["ZZ", "QQ", "ZZ[i]", "QQ[x]"])
def test_free_module_over_a_countable_ring_is_countable(build, name) -> None:
    assert _free(build(name), 3).cardinality() == aleph0


@pytest.mark.parametrize("name", ["RR", "CC", "QQ_3"])
def test_free_module_over_an_uncountable_ring_has_the_continuum(build, name) -> None:
    assert _free(build(name), 3).cardinality() == continuum


def test_free_module_of_countably_infinite_rank(commutative_ring) -> None:
    module = commutative_ring.free_module(NN)
    assert module in FreeModules(commutative_ring)
    assert module not in FinitelyGeneratedModules(commutative_ring)
    assert module.module_rank() == aleph0
    generator = module.module_generator(NN(5))
    assert generator + generator == 2 * generator


def test_the_ring_as_a_module_over_itself(commutative_ring) -> None:
    ring = commutative_ring
    regular = ring.regular_module()
    assert regular in FreeModules(ring)
    assert regular.module_rank() == cardinal(1)
    assert regular.base_ring() is ring


# ---------------------------------------------------------------------------
# Duals, Homs, tensor products, direct sums.
# ---------------------------------------------------------------------------


def test_dual_of_a_free_module(commutative_ring) -> None:
    module = _free(commutative_ring, 3)
    dual = module.dual_module()
    assert dual in FinitelyGeneratedFreeModules(commutative_ring)
    assert dual.module_rank() == cardinal(3)
    assert dual.dual_module().module_rank() == cardinal(3)


def test_internal_hom_between_free_modules(commutative_ring) -> None:
    ring = commutative_ring
    homs = _free(ring, 2).Mor(_free(ring, 3))
    assert homs in Modules(ring)
    assert homs in FinitelyGeneratedFreeModules(ring)
    assert homs.module_rank() == cardinal(6)


def test_tensor_product_of_free_modules(commutative_ring) -> None:
    ring = commutative_ring
    left = _free(ring, 2)
    right = _free(ring, 3)
    product = left.tensor_product(right)
    assert product in TensorProductModules(ring)
    assert product in FinitelyGeneratedFreeModules(ring)
    assert product.module_rank() == cardinal(6)
    pure = product.pure_tensor(left.module_generator(0), right.module_generator(1))
    assert pure + pure == product.pure_tensor(2 * left.module_generator(0), right.module_generator(1))
    assert product.pure_tensor(left.zero(), right.module_generator(0)) == product.zero()


def test_tensor_and_divided_squares(commutative_ring) -> None:
    module = _free(commutative_ring, 3)
    assert Modules(commutative_ring).tensor_product((module, module)).module_rank() == cardinal(9)
    assert module.divided_square().module_rank() == cardinal(6)


def test_biproduct_of_free_modules(commutative_ring) -> None:
    ring = commutative_ring
    left = _free(ring, 2)
    right = _free(ring, 3)
    both = Modules(ring).biproduct((left, right))
    assert both.module_rank() == cardinal(5)
    assert both in FinitelyGeneratedFreeModules(ring)
    retraction = both.left_projection() * both.left_inclusion()
    assert retraction == left.Mor(left).identity()
    assert both.right_projection() * both.left_inclusion() == left.Mor(right).zero()


# ---------------------------------------------------------------------------
# Morphisms and their kernels, images, cokernels.
# ---------------------------------------------------------------------------


def test_a_projection_and_its_kernel(commutative_ring) -> None:
    ring = commutative_ring
    plane = _free(ring, 2)
    line = _free(ring, 1)
    projection = plane.Mor(line)({0: line.module_generator(0), 1: line.zero()})

    assert projection(plane.module_generator(0)) == line.module_generator(0)
    assert projection.is_surjective()
    assert not projection.is_injective()
    assert projection.kernel().module_rank() == cardinal(1)
    assert projection.kernel().module_rank() == cardinal(1)
    assert projection.image().module_rank() == cardinal(1)
    assert projection.cokernel().cardinality() == cardinal(1)
    assert projection.cokernel().cardinality() == cardinal(1)


def test_multiplication_by_two_on_the_regular_module(integral_domain) -> None:
    r"""$\operatorname{coker}(R \xrightarrow{2} R) = R/2R$, and $2$ is injective unless $2 = 0$."""
    ring = integral_domain
    line = _free(ring, 1)
    doubling = line.Mor(line)({0: 2 * line.module_generator(0)})

    assert doubling.is_injective() == (ring(2) != ring.zero())
    assert doubling.cokernel().cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert doubling.is_surjective() == ring(2).is_unit()


# ---------------------------------------------------------------------------
# Subobjects, quotients, saturation.
# ---------------------------------------------------------------------------


def test_a_submodule_and_its_quotient(commutative_ring) -> None:
    r"""$N = \langle 2e_0, e_1\rangle \le R^3$ has $R^3/N \cong R/2R \oplus R$."""
    ring = commutative_ring
    module = _free(ring, 3)
    e0, e1, e2 = (module.module_generator(index) for index in range(3))
    submodule = module.subobject_on([2 * e0, e1])

    assert submodule in ModuleSubobjects(ring)
    assert submodule in Modules(ring)
    assert submodule.inclusion().is_injective()
    assert submodule.inclusion().codomain() is module
    assert submodule.module_rank() == cardinal(2)
    quotient = submodule.inclusion().cokernel()
    assert quotient in Modules(ring)
    assert quotient in FinitelyPresentedModules(ring)
    assert quotient.cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality() * ring.cardinality()


def test_index_and_saturation_of_a_submodule(pid) -> None:
    ring = pid
    module = _free(ring, 2)
    e0, e1 = module.module_generator(0), module.module_generator(1)
    submodule = module.subobject_on([2 * e0, e1])

    assert submodule.index() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert submodule.is_saturated() == ring(2).is_unit()
    assert submodule.saturation().index() == cardinal(1)
    assert submodule.saturation().module_rank() == cardinal(2)


def test_sums_and_intersections_of_submodules(commutative_ring) -> None:
    ring = commutative_ring
    module = _free(ring, 3)
    e0, e1 = module.module_generator(0), module.module_generator(1)
    first = module.subobject_on([e0])
    second = module.subobject_on([e1])
    diagonal = module.subobject_on([e0 + e1])

    assert first.intersection(second).cardinality() == cardinal(1)
    assert first.sum(second).module_rank() == cardinal(2)
    assert first.sum(second) == module.subobject_on([e0, e1])
    assert diagonal.intersection(first.sum(second)) == diagonal
    assert first.sum(second).sum(diagonal) == first.sum(second)


# ---------------------------------------------------------------------------
# Presented and torsion modules.
# ---------------------------------------------------------------------------


def test_a_finitely_presented_module_over_every_commutative_ring(commutative_ring) -> None:
    r"""$\operatorname{coker}\big(\operatorname{diag}(2,6)\big) \cong R/2R \oplus R/6R$."""
    ring = commutative_ring
    relations = _free(ring, 2)
    generators = _free(ring, 2)
    presentation = relations.Mor(generators)(
        {0: 2 * generators.module_generator(0), 1: 6 * generators.module_generator(1)}
    )
    module = (presentation).cokernel()

    assert module in FinitelyPresentedModules(ring)
    assert module in Modules(ring)
    assert module.cardinality() == (
        ring.quotient_ring(ring.ideal(ring(2))).cardinality()
        * ring.quotient_ring(ring.ideal(ring(6))).cardinality()
    )
    assert module.annihilator() == ring.ideal(ring(6))


@pytest.mark.parametrize("name", ["ZZ", "ZZ[i]", "ZZ_3", "ZZ_(5)", "QQ[x]", "ZZ[sqrt-5]"])
def test_a_torsion_module_over_a_dedekind_domain(build, name) -> None:
    ring = build(name)
    torsion = FinitelyPresentedTorsionModules(ring).direct_sum_of_cyclics((ring(2), ring(6)))

    assert torsion in TorsionModules(ring)
    assert torsion in FinitelyPresentedModules(ring)
    assert torsion.is_torsion()
    assert torsion.cardinality() == (
        ring.quotient_ring(ring.ideal(ring(2))).cardinality()
        * ring.quotient_ring(ring.ideal(ring(6))).cardinality()
    )
    assert torsion.annihilator() == ring.ideal(ring(6))


def test_invariant_factors_over_the_integers() -> None:
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((4, 6))
    invariant_factors = torsion.invariant_factors()

    assert torsion.cardinality() == cardinal(24)
    assert invariant_factors.cardinality() == cardinal(2)
    assert 2 in invariant_factors
    assert 12 in invariant_factors
    assert torsion.annihilator() == ZZ.ideal(12)


def test_free_resolution_over_a_principal_ideal_domain(pid) -> None:
    ring = pid
    generators = _free(ring, 2)
    relations = _free(ring, 1)
    presentation = relations.Mor(generators)({0: 6 * generators.module_generator(0)})
    module = (presentation).cokernel()
    resolution = module.free_resolution()

    assert resolution.is_exact()
    assert resolution.term(0) is generators
    assert resolution.term(2).module_rank() == cardinal(0)
    assert resolution.differential(1).is_injective() == (ring(6) != ring.zero())


# ---------------------------------------------------------------------------
# Ideals as modules, fractional ideals.
# ---------------------------------------------------------------------------


def test_a_principal_ideal_as_a_module(dedekind_domain) -> None:
    ring = dedekind_domain
    ideal = ring.ideal(ring(3))
    assert ideal in Modules(ring)
    assert ideal in ModuleSubobjects(ring)
    assert ideal.inclusion().codomain() is ring.regular_module()
    assert ideal.index() == ring.quotient_ring(ring.ideal(ring(3))).cardinality()
    assert ideal.module_rank() == cardinal(0 if ring(3) == ring.zero() else 1)


def test_fractional_ideals_of_the_gaussian_integers(build) -> None:
    gaussian = build("ZZ[i]")
    fractions = gaussian.fraction_field()
    i = fractions.primitive_element()
    ideal = gaussian.fractional_ideal(gaussian(fractions.one() + i))
    inverse = ideal.inverse()

    assert ideal.is_principal()
    assert inverse.is_principal()
    assert ideal.sum(inverse) == inverse
    assert ideal.intersection(inverse) == ideal


def test_a_non_principal_ideal_in_a_class_number_two_field(build) -> None:
    ring = build("ZZ[sqrt-5]")
    fractions = ring.fraction_field()
    s = fractions.primitive_element()
    ideal = ring.fractional_ideal(ring(2), ring(fractions.one() + s))
    assert not ideal.is_principal()
    assert ideal.inverse().inverse() == ideal


# ---------------------------------------------------------------------------
# Localization and base change.
# ---------------------------------------------------------------------------


def test_localizing_a_free_module_at_a_prime_of_the_integers() -> None:
    module = _free(ZZ, 2)
    point = ZZ.spectrum()(ZZ.ideal(5))
    localized = module.localize_at_prime(point)

    assert localized in LocalizedModules(point.local_ring())
    assert localized in Modules(point.local_ring())
    assert localized.module_rank() == cardinal(2)


def test_base_change_of_a_free_module_to_the_fraction_field(integral_domain) -> None:
    ring = integral_domain
    fractions = ring.fraction_field()
    module = _free(ring, 3)
    extended = module.base_change(ring.Mor(fractions)(lambda element: fractions(element)))

    assert extended in VectorSpaces(fractions)
    assert extended in Modules(fractions)
    assert extended.module_rank() == cardinal(3)


def test_base_change_of_a_torsion_module_kills_it_over_the_fraction_field() -> None:
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((6,))
    rationalized = torsion.base_change(ZZ.Mor(QQ)(lambda element: QQ(element)))
    assert rationalized in Modules(QQ)
    assert rationalized.cardinality() == cardinal(1)


def test_modules_over_a_field_are_free(field) -> None:
    generators = _free(field, 2)
    relations = _free(field, 1)
    presentation = relations.Mor(generators)({0: generators.module_generator(0) + generators.module_generator(1)})
    quotient = (presentation).cokernel()

    assert quotient in VectorSpaces(field)
    assert quotient in FreeModules(field)
    assert quotient.module_rank() == cardinal(1)
    assert quotient not in TorsionModules(field)
