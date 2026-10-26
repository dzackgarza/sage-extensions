from sage_extensions.all import *


def test_exact_embeddings_are_an_owned_ordered_finite_set() -> None:
    x = QQ.polynomial_ring("x").algebra_generator("x")
    quadratic = QuadraticField(2, "s")
    quartic = (x**4 - 2).number_field("t")
    embeddings = quadratic.exact_embeddings(quartic)

    assert embeddings.cardinality() == 2
    assert embeddings[0].domain() is quadratic
    assert embeddings[0].codomain() is quartic


def test_galois_group_of_gaussian_rationals_is_generated_by_complex_conjugation() -> None:
    r"""$\operatorname{Gal}(\mathbf{Q}(i)/\mathbf{Q}) = \{1, \sigma\}$ with $\sigma(i) = -i$."""
    field = QuadraticField(-1, "i")
    i = field.gen()

    assert field.galois_group().order() == 2
    assert {sigma(i) for sigma in field.automorphisms()} == {i, -i}
