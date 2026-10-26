r"""Complex conjugation is the nontrivial automorphism of Q(i)/Q."""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_conjugation_has_order_two_and_sends_i_to_minus_i() -> None:
    gaussian = QuadraticField(-1, "i")
    galois = gaussian.galois_group()
    conjugation = next(g for g in galois if g != galois.one())
    i = gaussian.primitive_element()
    action = conjugation.action()
    morphism = conjugation.as_morphism()

    assert conjugation.multiplicative_order() == 2
    assert conjugation.inverse() == conjugation
    assert action(i) == -i
    assert morphism(i) == -i

