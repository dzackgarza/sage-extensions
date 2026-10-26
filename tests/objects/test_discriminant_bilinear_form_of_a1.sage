from sage_extensions.all import *


def values():
    return FractionFieldQuotients(ZZ)(1)


def from_data():
    r"""$\mathbb Z/2$ with $b(x, x) = 1/2 \bmod \mathbb Z$."""
    return TorsionBilinearFormModules(ZZ).from_relations_and_gram([[2]], [[1/2]], values())


def test_the_data_and_the_lattice_constructions_agree() -> None:
    r"""$A_1 = \langle -2\rangle$: $b(e/2, e/2) = -1/2 \equiv 1/2 \bmod \mathbb Z$."""
    assert from_data().is_isometric_to(Lattices(ZZ)("A1").discriminant_bilinear_form())


def test_the_quadratic_refinement_construction_agrees() -> None:
    quadratic = TorsionQuadraticFormModules(ZZ).from_relations_and_gram([[2]], [[-1/2]], FractionFieldQuotients(ZZ)(2))
    assert from_data().is_isometric_to(quadratic.associated_bilinear_form())


def test_the_categories_of_b_a1() -> None:
    form = from_data()
    assert form in TorsionBilinearFormModules(ZZ)
    assert form in Modules(ZZ)


def test_the_values_of_b_a1() -> None:
    form = from_data()
    generator = form.module_generator(0)
    assert form.cardinality() == 2
    assert form.b(generator, generator) == values()(1/2)
    assert form.b(2 * generator, generator) == values().zero()
    assert form.twist(-1).is_isometric_to(form)


def test_the_isometries_of_b_a1() -> None:
    assert from_data().O().order() == 1
