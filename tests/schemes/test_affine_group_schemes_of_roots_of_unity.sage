r"""The affine group schemes ``mu_n``, ``G_a`` and ``G_m`` over ``Q``.

``mu_n = Spec Q[t]/(t^n - 1)`` with comultiplication ``t -> t (x) t``, counit ``t -> 1`` and
antipode ``t -> t^{-1} = t^{n-1}``; ``G_a = Spec Q[t]`` with ``t -> t (x) 1 + 1 (x) t``;
``G_m = Spec Q[t, t^{-1}]`` with ``t -> t (x) t``.  Each claim below reads off these Hopf
algebra structure maps.
"""

from sage_extensions.all import *


def _generator(scheme):
    algebra = scheme.coordinate_algebra()
    return algebra.algebra_generator(next(iter(algebra.algebra_generating_set())))


def test_mu_2_is_two_reduced_points_with_t_squared_equal_to_one() -> None:
    r"""``Q[t]/(t^2 - 1) = Q x Q``: zero-dimensional, ``t^2 = 1`` while ``t != ±1``."""
    mu = AffineGroupSchemes(QQ).roots_of_unity(2)
    algebra = mu.scheme().coordinate_algebra()
    t = _generator(mu.scheme())

    assert mu in AffineGroupSchemes(QQ)
    assert mu.scheme().dimension() == 0
    assert t**2 == algebra.one()
    assert t != algebra.one()
    assert t != -algebra.one()


def test_the_structure_maps_of_mu_2() -> None:
    r"""The unit pulls ``t`` back to ``1``, the inverse fixes ``t`` (``t^{-1} = t``), and the
    multiplication pulls ``t`` back to the product of its two pullbacks along the projections."""
    mu = AffineGroupSchemes(QQ).roots_of_unity(2)
    t = _generator(mu.scheme())
    multiplication = mu.multiplication()
    first, second = multiplication.domain().projections()

    assert mu.unit_morphism().coordinate_algebra_morphism()(t) == 1
    assert mu.inverse_morphism().coordinate_algebra_morphism()(t) == t
    assert multiplication.coordinate_algebra_morphism()(t) == (
        first.coordinate_algebra_morphism()(t) * second.coordinate_algebra_morphism()(t)
    )
    assert mu.unit_morphism().domain() is mu.base_scheme()


def test_mu_3_is_finite() -> None:
    r"""``Q[t]/(t^3 - 1)`` is a three-dimensional ``Q``-algebra, so ``mu_3`` has dimension zero."""
    assert AffineGroupSchemes(QQ).roots_of_unity(3).scheme().dimension() == 0


def test_the_identity_of_mu_2_is_a_group_scheme_morphism() -> None:
    r"""``id: mu_2 -> mu_2`` composes with itself to itself."""
    mu = AffineGroupSchemes(QQ).roots_of_unity(2)
    identity = mu.Mor(mu).identity()

    assert identity * identity == identity


def test_mu_2_acts_on_an_affine_scheme() -> None:
    r"""The category of ``mu_2``-actions on affine schemes has an object."""
    mu = AffineGroupSchemes(QQ).roots_of_unity(2)
    acted = AffineGroupSchemeActions(mu).an_object()

    assert acted.group_scheme() is mu


def test_the_additive_group_is_the_affine_line() -> None:
    r"""``G_a = Spec Q[t]`` is one-dimensional with ``t -> 0`` as unit."""
    additive = AffineGroupSchemes(QQ).additive_group()

    assert additive.scheme().dimension() == 1
    assert additive.unit_morphism().coordinate_algebra_morphism()(_generator(additive.scheme())) == 0


def test_the_multiplicative_group_is_the_punctured_line() -> None:
    r"""``G_m = Spec Q[t, t^{-1}]`` is one-dimensional and ``t`` is a unit on it."""
    multiplicative = AffineGroupSchemes(QQ).multiplicative_group()

    assert multiplicative.scheme().dimension() == 1
    assert _generator(multiplicative.scheme()).is_unit()
