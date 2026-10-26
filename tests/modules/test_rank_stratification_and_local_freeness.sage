r"""The fibre dimension of $\mathbb Q[x]/(x) \oplus \mathbb Q[x]$ over the affine line.

$M = R/(x) \oplus R$ with $R = \mathbb Q[x]$ has $\dim_{\kappa(\mathfrak p)} M \otimes \kappa(\mathfrak p)$
equal to $1$ at the generic point and $2$ at the origin; it is free of rank one
away from the origin and not free at it.  The fibre dimension is at least $d$
exactly on $V(\operatorname{Fitt}_{d-1} M)$ (Eisenbud, *Commutative Algebra*, 20.6).
"""

from sage_extensions.all import *  # noqa: F401,F403


def torsion_plus_free():
    R = QQ["x"]
    x = R.gen()
    F = R**2
    M = F / F.submodule([x * F.module_generator(0)])
    spectrum = R.spectrum()
    return R, x, M, spectrum.generic_point(), spectrum(R.ideal(x))


def test_the_fibre_dimension_is_1_generically_and_2_at_the_origin() -> None:
    R, x, M, generic, origin = torsion_plus_free()
    rank = M.rank_function()
    assert rank(generic) == 1
    assert rank(origin) == 2
    assert rank(R.spectrum()(R.ideal(x - 1))) == 1


def test_the_rank_strata_separate_the_generic_point_from_the_origin() -> None:
    """Fitt_0 = 0, Fitt_1 = (x): the rank-2 stratum is V(x). Source: Eisenbud 20.6."""
    R, x, M, generic, origin = torsion_plus_free()
    assert M.fitting_ideal(1) == R.ideal(x)
    assert generic in M.rank_stratum(1)
    assert origin not in M.rank_stratum(1)
    assert origin in M.rank_stratum(2)
    assert generic not in M.rank_stratum(2)


def test_the_module_is_locally_free_generically_and_not_at_the_origin() -> None:
    R, x, M, generic, origin = torsion_plus_free()
    locus = M.local_freeness_locus()
    assert generic in locus
    assert origin not in locus
    assert not M.localize_at_prime(origin).is_free()


def test_the_local_trivialization_at_the_generic_point_has_rank_one() -> None:
    R, x, M, generic, origin = torsion_plus_free()
    trivialization = M.local_free_trivialization_at(generic)
    assert trivialization.domain().module_rank() == 1
    assert trivialization.is_isomorphism()


def test_the_annihilator_of_q_x_y_mod_x_plus_q_x_y_mod_y_is_xy() -> None:
    r"""$\operatorname{Ann}(R/(x) \oplus R/(y)) = (x) \cap (y) = (xy)$ over $\mathbb Q[x,y]$.

    Source: by hand; x and y are coprime in the UFD QQ[x,y].
    """
    R = QQ["x,y"]
    x, y = R.algebra_generator("x"), R.algebra_generator("y")
    F = R**2
    M = F / F.submodule([x * F.module_generator(0), y * F.module_generator(1)])
    assert M.annihilator() == R.ideal(x * y)
    assert M.annihilator() != R.ideal(x)
