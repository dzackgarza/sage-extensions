r"""Projectivity of finitely presented abelian groups from Fitting ideals.

A finitely presented module over a domain is projective of rank $r$ exactly when
$\operatorname{Fitt}_{r-1}(M) = 0$ and $\operatorname{Fitt}_r(M) = R$
(Eisenbud, *Commutative Algebra*, Proposition 20.8).
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_z2_modulo_a_basis_vector_is_projective_with_fitting_ideals_0_and_z() -> None:
    r"""$\mathbb Z^2/(g) \cong \mathbb Z$: $\operatorname{Fitt}_0 = 0$, $\operatorname{Fitt}_1 = \mathbb Z$.

    Source: Eisenbud 20.8; by hand from the relation matrix (1, 0).
    """
    F = ZZ**2
    M = F / F.submodule([F.module_generator(0)])
    assert M.fitting_ideal(0) == ZZ.ideal(0)
    assert M.fitting_ideal(1) == ZZ.ideal(1)
    assert M.is_projective()


def test_z_mod_6_plus_z_is_not_projective_since_its_first_fitting_ideal_is_6z() -> None:
    r"""$\mathbb Z^2/(6g) \cong \mathbb Z/6 \oplus \mathbb Z$: $\operatorname{Fitt}_0 = 0$,
    $\operatorname{Fitt}_1 = (6) \ne \mathbb Z$, $\operatorname{Fitt}_2 = \mathbb Z$.

    Source: Eisenbud 20.8; by hand from the relation matrix (6, 0).
    """
    F = ZZ**2
    M = F / F.submodule([6 * F.module_generator(0)])
    assert M.fitting_ideal(0) == ZZ.ideal(0)
    assert M.fitting_ideal(1) == ZZ.ideal(6)
    assert M.fitting_ideal(2) == ZZ.ideal(1)
    assert not M.is_projective()
