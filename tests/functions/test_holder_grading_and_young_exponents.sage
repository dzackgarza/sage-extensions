r"""Hölder degrees add under pointwise products; Young's exponent rule for convolution.

Hölder: ``f in L^p``, ``g in L^q`` give ``f g in L^r`` with ``1/r = 1/p + 1/q``,
so grading ``L^p`` in degree ``1/p`` makes pointwise multiplication additive in
degree, with the constants of ``L^oo`` in degree 0.  Young: for ``1/p + 1/q =
1 + 1/r`` with ``p, q, r >= 1``, convolution is ``L^p x L^q -> L^r``; the pair
must satisfy ``1/p + 1/q >= 1``.  Convolution on ``L^1`` is associative and
commutative, with no unit (Riemann--Lebesgue: ``\hat f`` vanishes at infinity).
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def test_the_square_of_the_gaussian_in_L2_is_its_double_exponent_in_L1() -> None:
    r"""``e^{-x^2}`` sits in degree ``1/2``; its pointwise square ``e^{-2x^2}`` sits in degree ``1``."""
    algebra = GradedLebesgueAlgebra
    square_integrable = Lp(2, RR, RR)
    f1(x) = exp(-x * x)
    gaussian = algebra(square_integrable(f1))
    square = gaussian * gaussian

    assert algebra in Algebras(RR).Associative().Unital().Commutative()
    assert algebra.degree_projection(QQ(1) / 2)(gaussian)(0) == 1
    assert algebra.degree_projection(1)(square)(1) == exp(-2)


def test_a_homogeneous_element_projects_to_zero_off_its_degree() -> None:
    r"""``pi_1(e^{-x^2}) = 0`` for ``e^{-x^2}`` in degree ``1/2``, and ``pi_{1/2}(e^{-2x^2}) = 0``."""
    algebra = GradedLebesgueAlgebra
    square_integrable = Lp(2, RR, RR)
    f1(x) = exp(-x * x)
    gaussian = algebra(square_integrable(f1))

    assert algebra.degree_projection(1)(gaussian) == Lp(1, RR, RR).zero()
    assert algebra.degree_projection(QQ(1) / 2)(gaussian * gaussian) == square_integrable.zero()


def test_the_unit_of_the_pointwise_algebra_is_the_constant_one_in_degree_zero() -> None:
    r"""The constant ``1`` is essentially bounded and is the pointwise unit; it projects to ``1``."""
    algebra = GradedLebesgueAlgebra
    square_integrable = Lp(2, RR, RR)
    f1(x) = exp(-x * x)
    gaussian = algebra(square_integrable(f1))

    assert algebra.unit_piece_projection()(algebra.one())(5) == 1
    assert algebra.degree_projection(QQ(1) / 2)(algebra.one() * gaussian)(1) == exp(-1)


def test_the_constant_one_times_a_map_is_that_map() -> None:
    r"""``1 . f = f`` in the pointwise algebra, for ``f = e^{-x^2}``."""
    algebra = GradedLebesgueAlgebra
    f1(x) = exp(-x * x)
    gaussian = algebra(Lp(2, RR, RR)(f1))

    assert algebra.one() * gaussian == gaussian


def test_integration_of_the_degree_one_piece_is_the_integral_on_L1() -> None:
    r"""``int e^{-|x|} dx = 2`` on the degree-1 piece ``L^1``."""
    algebra = GradedLebesgueAlgebra
    f1(x) = exp(-abs(x))

    assert algebra.integration_of_degree_one()(Lp(1, RR, RR)(f1)) == 2


def test_the_integral_form_reads_the_degree_one_component() -> None:
    r"""``epsilon(e^{-x^2} . e^{-x^2}) = int e^{-2x^2} = sqrt(pi/2)``; ``epsilon`` vanishes off degree 1."""
    algebra = GradedLebesgueAlgebra
    f1(x) = exp(-x * x)
    gaussian = algebra(Lp(2, RR, RR)(f1))

    assert algebra.integral_form()(gaussian * gaussian) == sqrt(pi / 2)
    assert algebra.integral_form()(gaussian) == 0


def test_young_exponents_of_convolution_pairings() -> None:
    r"""``L^1 * L^oo -> L^oo``, ``L^2 * L^2 -> L^oo``, ``L^1 * L^2 -> L^2``: ``1/r = 1/p + 1/q - 1``."""
    integrable = Lp(1, RR, RR).quotient_by_null_functions()
    square = Lp(2, RR, RR).quotient_by_null_functions()
    bounded = Lp(oo, RR, RR).quotient_by_null_functions()

    assert integrable.convolution_pairing(bounded).codomain() is bounded
    assert square.convolution_pairing(square).codomain() is bounded
    assert integrable.convolution_pairing(square).codomain() is square


def test_a_pair_below_the_young_line_has_no_convolution_pairing() -> None:
    r"""``1/2 + 1/3 = 5/6 < 1``: no ``r >= 1`` solves Young's relation for ``(p, q) = (2, 3)``."""
    square = Lp(2, RR, RR).quotient_by_null_functions()
    cube = Lp(3, RR, RR).quotient_by_null_functions()

    with pytest.raises(ValueError):
        square.convolution_pairing(cube)


def test_L1_convolution_is_a_commutative_nonunital_algebra() -> None:
    r"""``(L^1, *)`` is associative and commutative and has no unit."""
    algebra = LebesgueConvolutionAlgebra

    assert algebra in Algebras(RR).Associative()
    assert algebra in Algebras(RR).Commutative()
    assert algebra not in Algebras(RR).Unital()


def test_the_gaussian_convolved_with_itself_is_a_wider_gaussian() -> None:
    r"""``(e^{-x^2} * e^{-x^2})(y) = int e^{-t^2 - (y-t)^2} dt = sqrt(pi/2) e^{-y^2/2}``.

    Complete the square: ``t^2 + (y-t)^2 = 2(t - y/2)^2 + y^2/2``.
    """
    algebra = LebesgueConvolutionAlgebra
    f1(x) = exp(-x * x)
    gaussian = algebra(Lp(1, RR, RR)(f1))

    assert (gaussian * gaussian).representative()(0) == sqrt(pi / 2)
