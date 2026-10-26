r"""Exact field morphisms restrict and extend along explicit number-field embeddings."""

from sage_extensions.all import *  # noqa: F401,F403


def _gaussian_inside_twelfth_cyclotomic():
    x = QQ.polynomial_ring("x").algebra_generator("x")
    cyclotomic = (x**4 - x**2 + 1).number_field("z")
    zeta = cyclotomic.primitive_element()
    gaussian = QuadraticField(-1, "i")
    i = gaussian.primitive_element()
    embedding = next(e for e in gaussian.exact_embeddings(cyclotomic) if e(i) == zeta**3)
    conjugation = next(e for e in gaussian.exact_embeddings(gaussian) if e(i) == -i)
    return gaussian, i, cyclotomic, zeta, embedding, conjugation


def test_gaussian_conjugation_is_an_injective_involution() -> None:
    gaussian, i, _, _, _, conjugation = _gaussian_inside_twelfth_cyclotomic()
    inverse = conjugation.inverse()

    assert conjugation.is_injective()
    assert conjugation.agrees_on_field(conjugation)
    assert conjugation(i) == -i
    assert inverse(i) == -i
    assert inverse * conjugation == gaussian.Mor(gaussian).identity()


def test_conjugation_has_exactly_two_extensions_to_twelfth_cyclotomic_field() -> None:
    _, _, cyclotomic, zeta, embedding, conjugation = _gaussian_inside_twelfth_cyclotomic()
    group = QQ.absolute_galois_group()
    quotient = group.finite_quotient(group.extension_data(cyclotomic))
    candidates = [sigma.action() for sigma in quotient]
    extensions = conjugation.extensions_along(embedding, candidates)

    assert extensions.cardinality() == cardinal(2)
    assert {
        a
        for a in (1, 5, 7, 11)
        if any(extension(zeta) == zeta**a for extension in extensions)
    } == {7, 11}


def test_sigma_seven_restricts_to_gaussian_conjugation() -> None:
    _, i, cyclotomic, zeta, embedding, conjugation = _gaussian_inside_twelfth_cyclotomic()
    group = QQ.absolute_galois_group()
    quotient = group.finite_quotient(group.extension_data(cyclotomic))
    sigma_seven = next(sigma.action() for sigma in quotient if sigma.action()(zeta) == zeta**7)
    restriction = sigma_seven.restrict_along(embedding)

    assert restriction(i) == -i
    assert restriction.agrees_on_field(conjugation)

