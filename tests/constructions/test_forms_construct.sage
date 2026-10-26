r"""Bilinear and quadratic forms a mathematician expects, over every named ring.

Forms on free modules from a Gram matrix, pairings between two modules, the
form as a morphism out of the tensor or divided square, torsion forms with
values in $K/R$, the free-form adjunctions, base change of forms, and form
embeddings.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

A2_GRAM = [[2, 1], [1, 2]]


def test_a_symmetric_bilinear_form_from_a_gram_matrix(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    form = FormModules(ring)(module.bilinear_hom_space(ring)(A2_GRAM))
    e0, e1 = form.module_generator(0), form.module_generator(1)

    assert form in BilinearFormModules(ring)
    assert form in SymmetricBilinearFormModules(ring)
    assert form in FormModules(ring)
    assert form in Modules(ring)
    assert form.unformed_module() is module
    assert form.value_module() == ring.regular_module()
    assert form.b(e0, e1) == ring.one()
    assert form.b(e0, e0) == 2 * ring.one()
    assert form.b(e0, e1) == form.b(e1, e0)
    assert form.b(e0 + e1, e0 - e1) == ring.zero()
    assert e0.b(e1) == form.b(e0, e1)
    assert form.determinant() == 3 * ring.one()
    assert form.is_nondegenerate() == (3 * ring.one() != ring.zero())
    assert form.correlation_morphism().is_injective() == (3 * ring.one() != ring.zero())
    assert form.dual_module().module_rank() == cardinal(2)
    assert form.twist(2).determinant() == 12 * ring.one()
    assert ring.one() in form.scale_submodule()


def test_a_covariant_two_tensor_is_gram_data_for_a_bilinear_form(commutative_ring) -> None:
    r"""A type-$(0,2)$ tensor supplies $b(e_i,e_j)$; its variance is not erased when the form is constructed."""
    ring = commutative_ring
    module = ring.free_module(2)
    gram = tensor(ring, (), (2, 2), A2_GRAM)
    form = FormModules(ring)(module.bilinear_hom_space(ring)(gram))
    e0, e1 = form.module_generator(0), form.module_generator(1)

    assert form.gram_tensor() == gram
    assert form.b(e0, e0) == 2 * ring.one()
    assert form.b(e0, e1) == ring.one()


def test_the_form_is_a_morphism_out_of_the_tensor_square(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    form = FormModules(ring)(module.bilinear_hom_space(ring)(A2_GRAM))
    morphism = form.form()
    square = Modules(ring).tensor_product((module, module))

    assert morphism.domain() is square
    assert morphism.codomain() == form.value_module()
    assert morphism in module.bilinear_forms(ring)
    e0, e1 = module.module_generator(0), module.module_generator(1)
    assert morphism(square.pure_tensor(e0, e1)) == form.value_module().module_generator(0)
    assert morphism(square.pure_tensor(e0, e0)) == 2 * form.value_module().module_generator(0)
    assert module.bilinear_forms(ring)(A2_GRAM) == morphism


def test_a_quadratic_form_from_its_gram_matrix(commutative_ring) -> None:
    r"""$q(x, y) = x^2 + xy + y^2$ with polar form $b(e_0, e_1) = 1$."""
    ring = commutative_ring
    module = ring.free_module(2)
    quadratic = module.equip_quadratic_form(ring, [[1, 1], [0, 1]])
    e0, e1 = quadratic.module_generator(0), quadratic.module_generator(1)

    assert quadratic in QuadraticFormModules(ring)
    assert quadratic in FormModules(ring)
    assert quadratic.q(e0) == ring.one()
    assert quadratic.q(e1) == ring.one()
    assert quadratic.q(e0 + e1) == 3 * ring.one()
    assert quadratic.q(2 * e0) == 4 * ring.one()
    assert quadratic.b(e0, e1) == ring.one()
    assert e0.q() == ring.one()
    assert quadratic.form().domain() is module.divided_square()
    assert module.quadratic_forms(ring)([[1, 1], [0, 1]]) == quadratic.form()


def test_a_pairing_between_two_modules(commutative_ring) -> None:
    ring = commutative_ring
    left = ring.free_module(2)
    right = ring.free_module(3)
    pairing = left.pairings_with(right, ring)([[1, 0, 2], [0, 1, 0]])
    assert pairing.domain().tensor_factors().cardinality() == cardinal(2)
    assert pairing(pairing.domain().pure_tensor(left.module_generator(0), right.module_generator(2))) == 2 * ring.one()
    assert pairing(pairing.domain().pure_tensor(left.module_generator(1), right.module_generator(0))) == ring.zero()


def test_a_form_module_from_a_form_morphism(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    morphism = module.bilinear_forms(ring)(A2_GRAM)
    formed = FormModules(ring)(morphism)
    assert formed in FormModules(ring)
    assert formed.unformed_module() is module
    assert formed.form() == morphism
    assert formed.b(formed.module_generator(0), formed.module_generator(1)) == ring.one()


def test_the_free_form_adjunctions_over_every_commutative_ring(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    for adjunction, category in (
        (Modules(ring).free_bilinear_form_adjunction(), BilinearFormModules(ring)),
        (Modules(ring).free_quadratic_form_adjunction(), QuadraticFormModules(ring)),
    ):
        free = adjunction.left_adjoint()(module)
        assert free in category
        assert adjunction.right_adjoint()(free) in Modules(ring)
        assert adjunction.right_adjoint()(free).module_rank() == cardinal(2)
        unit = adjunction.unit(module)
        assert unit.domain() is module
        assert unit.codomain() == adjunction.right_adjoint()(free)
        counit = adjunction.counit(free)
        assert counit.codomain() is free


def test_base_change_of_a_form(build) -> None:
    module = ZZ.free_module(2)
    form = FormModules(ZZ)(module.bilinear_hom_space(ZZ)(A2_GRAM))
    rational = form.base_change(ZZ.Mor(QQ)(lambda n: QQ(n)))
    mod_three = form.base_change(ZZ.Mor(GF(3))(lambda n: GF(3)(n)))
    mod_five = form.base_change(ZZ.Mor(GF(5))(lambda n: GF(5)(n)))

    assert rational in BilinearFormModules(QQ)
    assert rational.determinant() == QQ(3)
    assert rational.is_nondegenerate()
    assert mod_three in BilinearFormModules(GF(3))
    assert not mod_three.is_nondegenerate()
    assert mod_five.is_nondegenerate()
    assert mod_five.determinant() == GF(5)(3)


@pytest.mark.parametrize(
    "name, modulus, size",
    [("ZZ", 2, aleph0), ("ZZ", 12, aleph0), ("ZZ", 1, aleph0), ("QQ[x]", None, aleph0), ("ZZ[i]", 3, aleph0), ("ZZ_3", 9, aleph0)],
)
def test_fraction_field_quotients(build, name, modulus, size) -> None:
    r"""For a domain $R$ with fraction field $K$, ``FractionFieldQuotients(R)(m)`` is $K/mR$.

    Each listed $K/mR$ is countably infinite: for number fields and rational
    function fields this follows because $K$ is countable and the quotient has
    elements of unbounded additive order; for $\mathbb Q_3/9\mathbb Z_3$ use
    $\mathbb Q_3=\bigcup_{k\ge0}3^{-k}\mathbb Z_3$, whose successive quotients
    by $9\mathbb Z_3$ are finite.
    """
    ring = build(name)
    element = ring.algebra_generator("x") ** 2 if modulus is None else ring(modulus)
    quotient = FractionFieldQuotients(ring)(element)

    assert quotient in FractionFieldQuotients(ring)
    assert quotient in Modules(ring)
    assert quotient.base_ring() is ring
    assert quotient.fraction_field() is ring.fraction_field()
    assert quotient.cardinality() == cardinal(size)
    assert quotient.modulus() == quotient.fraction_field()(element)
    assert quotient(element) == quotient.zero()


def test_discriminant_forms_from_relations_and_gram() -> None:
    r"""The discriminant form of $A_1 = \langle -2\rangle$ and the form $u(2)$."""
    values = FractionFieldQuotients(ZZ)(2)
    a1 = TorsionQuadraticFormModules(ZZ).from_relations_and_gram([[2]], [[-QQ(1) / QQ(2)]], values)
    u2 = TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        [[2, 0], [0, 2]], [[0, QQ(1) / QQ(2)], [QQ(1) / QQ(2), 0]], values
    )
    generator = a1.module_generator(0)

    assert a1 in TorsionQuadraticFormModules(ZZ)
    assert a1.cardinality() == cardinal(2)
    assert a1.q(generator) == values(-QQ(1) / QQ(2))
    assert a1.q(2 * generator) == values.zero()
    assert a1.is_anisotropic()
    assert not a1.is_metabolic()
    assert a1.O().order() == 1
    assert a1.brown_invariant() == 7
    assert a1.is_isometric_to(Lattices(ZZ)("A1").discriminant_quadratic_form())
    assert u2.cardinality() == cardinal(4)
    assert u2.is_metabolic()
    assert not u2.is_anisotropic()
    assert u2.lagrangian_subgroups().cardinality() == cardinal(2)
    assert u2.isotropic_elements().cardinality() == cardinal(3)
    assert u2.brown_invariant() == 0
    assert u2.O().order() == 2
    assert not u2.is_isometric_to(a1 + a1)


def test_a_torsion_bilinear_form() -> None:
    values = FractionFieldQuotients(ZZ)(1)
    form = TorsionBilinearFormModules(ZZ).from_relations_and_gram([[4]], [[QQ(1) / QQ(4)]], values)
    generator = form.module_generator(0)
    assert form in TorsionBilinearFormModules(ZZ)
    assert form.cardinality() == cardinal(4)
    assert form.b(generator, generator) == values(QQ(1) / QQ(4))
    assert form.b(2 * generator, 2 * generator) == values.zero()
    assert form.O().order() == 2
    assert form.is_isometric_to(form)
    assert form.is_anti_isometric(form.twist(-1))
    assert form.normal_form().codomain().cardinality() == cardinal(4)


def test_form_embeddings_between_lattices() -> None:
    a1 = Lattices(ZZ)("A1")
    a2 = Lattices(ZZ)("A2")
    embedding = a1.Mono(a2)([a2.module_generator(0)])
    assert embedding.domain() is a1
    assert embedding.codomain() is a2
    assert embedding.is_injective()
    assert embedding.is_primitive()
    assert embedding.orthogonal_complement().module_rank() == cardinal(1)
    assert embedding.orthogonal_complement().determinant() == 6
    assert embedding in a1.Emb(a2)


def test_determinant_lines_and_exterior_forms(commutative_ring) -> None:
    module = commutative_ring.free_module(3)
    assert module.determinant_line().module_rank() == cardinal(1)
    assert module.exterior_forms(0).module_rank() == cardinal(1)
    assert module.exterior_forms(1).module_rank() == cardinal(3)
    assert module.exterior_forms(2).module_rank() == cardinal(3)
    assert module.exterior_forms(3).module_rank() == cardinal(1)
    assert module.exterior_forms(4).module_rank() == cardinal(0)


def test_forms_over_a_polynomial_ring_and_over_a_field() -> None:
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    module = polynomials.free_module(2)
    form = FormModules(polynomials)(module.bilinear_hom_space(polynomials)([[x, 1], [1, x]]))
    e0, e1 = form.module_generator(0), form.module_generator(1)
    assert form.determinant() == x**2 - polynomials.one()
    assert form.is_nondegenerate()
    assert form.b(e0, e0) == x
    specialized = form.base_change(polynomials.Mor(QQ)({"x": QQ(1)}))
    assert specialized in BilinearFormModules(QQ)
    assert not specialized.is_nondegenerate()
    assert specialized.radical().module_rank() == cardinal(1)
