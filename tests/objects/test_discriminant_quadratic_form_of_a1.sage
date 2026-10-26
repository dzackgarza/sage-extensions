from sage_extensions.all import *


def values():
    return FractionFieldQuotients(ZZ)(2)


def from_data():
    r"""$\mathbb Z/2$ with $q(x) = -1/2 \bmod 2\mathbb Z$."""
    return TorsionQuadraticFormModules(ZZ).from_relations_and_gram([[2]], [[-1/2]], values())


def test_the_data_and_the_lattice_constructions_agree() -> None:
    r"""$A_1 = \langle -2\rangle$ has $A_1^\vee = \tfrac12 A_1$ and $q(e/2) = -2/4 = -1/2$."""
    assert from_data().is_isometric_to(Lattices(ZZ)("A1").discriminant_quadratic_form())


def test_the_categories_of_q_a1() -> None:
    form = from_data()
    assert form in TorsionQuadraticFormModules(ZZ)
    assert form in Modules(ZZ)


def test_the_values_of_q_a1() -> None:
    form = from_data()
    generator = form.module_generator(0)
    assert form.cardinality() == 2
    assert form.q(generator) == values()(-1/2)
    assert form.q(2 * generator) == values().zero()
    assert 2 * generator == form.zero()


def test_q_a1_is_anisotropic() -> None:
    form = from_data()
    assert form.is_anisotropic()
    assert not form.is_metabolic()
    assert form.isotropic_elements().cardinality() == 1


def test_the_isometries_of_q_a1() -> None:
    r"""$\operatorname{Aut}(\mathbb Z/2)$ is trivial."""
    assert from_data().O().order() == 1


def test_the_brown_invariant_of_q_a1() -> None:
    r"""Milgram: the Brown invariant of $q_L$ is the signature of $L$ mod $8$; $\operatorname{sign} A_1 = -1 \equiv 7$."""
    assert from_data().brown_invariant() == 7


def test_the_associated_bilinear_form() -> None:
    r"""$2b(x, y) = q(x + y) - q(x) - q(y) \bmod 2\mathbb Z$, so $b(x, x) \equiv q(x) \bmod \mathbb Z$: $b(g, g) = -1/2 \equiv 1/2$."""
    bilinear = from_data().associated_bilinear_form()
    generator = bilinear.module_generator(0)
    assert bilinear.b(generator, generator) == FractionFieldQuotients(ZZ)(1)(1/2)
