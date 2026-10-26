r"""Morphisms of the affine group schemes of roots of unity over QQ."""

from sage_extensions.all import *


def test_squaring_mu_four_onto_mu_two_is_a_homomorphism_with_kernel_mu_two() -> None:
    r"""Squaring `\mu_4 \to \mu_2`, `u \mapsto u^2`, is a group homomorphism with kernel `\mu_2`.

    Derivation: on `R`-points `\zeta \mapsto \zeta^2` is a homomorphism
    `\mu_4(R) \to \mu_2(R)` whose kernel is `\{\pm 1\} = \mu_2(R)`.
    """
    mu_four = AffineGroupSchemes(QQ).roots_of_unity(4)
    mu_two = AffineGroupSchemes(QQ).roots_of_unity(2)
    four_ring = mu_four.coordinate_ring()
    two_ring = mu_two.coordinate_ring()
    comorphism = two_ring.Mor(four_ring)({"u": four_ring.algebra_generator("u") ** 2})
    spec = Algebras(QQ).Associative().Unital().Commutative().spectrum()

    squaring = mu_four.Mor(mu_two)(spec(comorphism))

    assert mu_four.order() == 4
    assert mu_two.order() == 2
    assert squaring.kernel().order() == 2
    assert squaring * mu_four.unit_morphism() == mu_two.unit_morphism()


def test_negation_on_mu_two_is_a_scheme_involution_moving_the_unit() -> None:
    r"""`u \mapsto -u` is an involution of the scheme `\mu_2` sending `1` to `-1`,
    so it is not a homomorphism of group schemes.

    Derivation: a group homomorphism fixes the identity point `u = 1`.
    """
    mu_two = AffineGroupSchemes(QQ).roots_of_unity(2)
    ring = mu_two.coordinate_ring()
    u = ring.algebra_generator("u")
    spec = Algebras(QQ).Associative().Unital().Commutative().spectrum()
    negation = spec(ring.Mor(ring)({"u": -u}))

    assert negation * negation == spec(ring.Mor(ring).identity())
    assert negation * mu_two.unit_morphism() != mu_two.unit_morphism()
    assert negation not in mu_two.Mor(mu_two)
