r"""Extensions of complex conjugation from $\mathbb{Q}(i)$ to $\mathbb{Q}(\zeta_{12})$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_complex_conjugation_of_q_i_extends_to_sigma_7_and_sigma_11() -> None:
    r"""With $i = \zeta^3$, $\sigma_a(\zeta) = \zeta^a$ sends $i \mapsto i^a$.

    So $\sigma_a$ fixes $i$ iff $a \equiv 1 \bmod 4$ ($a = 1, 5$) and sends
    $i \mapsto -i$ iff $a \equiv 3 \bmod 4$ ($a = 7, 11$): the extensions of
    conjugation are the coset $\sigma_7 \operatorname{Gal}(\mathbb{Q}(\zeta_{12})/\mathbb{Q}(i))$.
    """
    x = QQ.polynomial_ring("x").algebra_generator("x")
    cyclotomic = (x**4 - x**2 + 1).number_field("z")
    zeta = cyclotomic.primitive_element()
    gaussian = QuadraticField(-1, "i")
    i = gaussian.primitive_element()
    embedding = next(e for e in gaussian.exact_embeddings(cyclotomic) if e(i) == zeta**3)
    conjugation = next(s for s in gaussian.exact_embeddings(gaussian) if s(i) == -i)

    group = QQ.absolute_galois_group()
    quotient = group.finite_quotient(group.extension_data(cyclotomic))
    extensions = conjugation.extensions_along(embedding, [sigma.action() for sigma in quotient])

    assert quotient.order() == 4
    assert extensions.cardinality() == 2
    assert {a for a in (1, 5, 7, 11) if any(e(zeta) == zeta**a for e in extensions)} == {7, 11}
    assert {a for a in (1, 5, 7, 11) if any(s(zeta) == zeta**a and s(zeta**3) == zeta**3 for s in quotient)} == {1, 5}
