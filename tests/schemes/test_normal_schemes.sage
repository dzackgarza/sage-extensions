r"""Normality of affine and projective space, read off the base ring.

Affine and projective `n`-space over `R` are covered by polynomial rings over `R`,
which are unique factorization domains when `R` is (Gauss's lemma), hence
integrally closed; `\mathbb{Z}` and `\mathbb{Q}` are such.  Over
`\mathbb{Z}/12`, where `6^2 = 0`, the coordinate ring has a nilpotent, so the scheme
is not even reduced.
"""

from sage_extensions.all import *


def test_affine_space_over_a_normal_domain_is_normal_and_over_z_mod_12_is_not() -> None:
    assert AffineSpaces(ZZ)(1).is_normal()
    assert AffineSpaces(QQ)(2).is_normal()

    line = AffineSpaces(Zmod(12))(1)
    assert not line.is_reduced()
    assert not line.is_normal()


def test_projective_space_over_a_normal_domain_is_normal() -> None:
    assert ProjectiveSpaces(QQ)(1).is_normal()
    assert ProjectiveSpaces(ZZ)(2).is_normal()
    assert ZZ.affine_spectrum().is_normal()
