r"""The degrees, the growth series and the growth rate of a Coxeter system.

The Coxeter system owns its word length, the degrees of the invariant ring of
its finite cases, the growth series as a rational function with its reciprocal
value at $1$, and the growth rate of its infinite cases.  Each item below is
decided by a specimen of the issue that asked for it -- $W(A_2)(t)=1+2t+2t^2+t^3$,
the affine $A_1$ series $(1+t)/(1-t)$, the eight degrees of $W(E_8)$ and its
$|W|=696729600$, and the growth rate of the $(2,3,7)$ triangle group -- or by a
computation the library answers independently of the one asserted:

- the product of the degrees of a finite group against the order the engine
  gives the same group, and $\sum_i(d_i-1)$ against the length of the longest
  element found by the Cayley graph search;
- $\chi(W)=1/W(1)$ against $1/|W|$ for a finite group, which is the same number
  by two formulae: Solomon's product and the engine's own coset enumeration;
- the denominator of the growth series of the $(2,3,7)$ group against Lehmer's
  polynomial, and the growth rate against its largest root, which is Lehmer's
  number $1.17628\ldots$, the Salem number Hironaka identifies as the minimal
  growth rate of a cocompact planar hyperbolic Coxeter group (as quoted by
  Kellerhals--Kolpakov, Canad. J. Math. 66 (2014) 354--372).

A growth series is asserted by cross-multiplication, $P(t)Q'(t)=P'(t)Q(t)$,
because a rational function is not the pair of its numerator and denominator.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest

LEHMER_COEFFICIENTS = (1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1)


def _polynomial(coefficients):
    r"""The owned polynomial with these coefficients, in the one variable ``t`` over the integers."""
    presentation = ZZ.polynomial_ring("t")
    variable = presentation.algebra_generator("t")
    return sum(
        (presentation(coefficient) * variable**degree for degree, coefficient in enumerate(coefficients)),
        presentation.zero(),
    )


def _product_of_the_degrees(group):
    r"""The product $\prod_i d_i$ of the degrees of ``group``, as an integer."""
    product = 1
    for degree in group.degrees():
        product = product * int(degree)
    return product


def _lehmer_value_at(number):
    r"""Lehmer's polynomial evaluated at ``number``, an element of the real algebraic numbers."""
    return sum(
        (ZZ(coefficient) * number**degree for degree, coefficient in enumerate(LEHMER_COEFFICIENTS)),
        ZZ(0),
    )


def test_the_degrees_of_the_classical_finite_coxeter_groups():
    r"""The degrees of $A_n$, $B_n$, $D_4$, $F_4$, $G_2$, $H_3$, $H_4$, $E_6$ and $E_7$."""
    expected = {
        ("A", 1): (2,),
        ("A", 2): (2, 3),
        ("A", 4): (2, 3, 4, 5),
        ("B", 2): (2, 4),
        ("B", 3): (2, 4, 6),
        ("D", 4): (2, 4, 4, 6),
        ("F", 4): (2, 6, 8, 12),
        ("G", 2): (2, 6),
        ("H", 3): (2, 6, 10),
        ("H", 4): (2, 12, 20, 30),
        ("E", 6): (2, 5, 6, 8, 9, 12),
        ("E", 7): (2, 6, 8, 10, 12, 14, 18),
    }
    for label, degrees in expected.items():
        assert tuple(int(degree) for degree in Groups.Coxeter(list(label)).degrees()) == degrees


def test_the_degrees_of_the_e8_reflection_group_are_the_eight_stated_degrees():
    r"""$W(E_8)$ has degrees $2,8,12,14,18,20,24,30$ and their product is $696729600$."""
    group = Groups.Coxeter(["E", 8])
    assert tuple(int(degree) for degree in group.degrees()) == (2, 8, 12, 14, 18, 20, 24, 30)
    assert _product_of_the_degrees(group) == 696729600


def test_the_product_of_the_degrees_is_the_order_of_the_group():
    r"""$\prod_i d_i=|W|$, against the order the engine gives the same group."""
    for label in ("A", 2), ("B", 2), ("G", 2), ("H", 3), ("F", 4), ("A", 4):
        group = Groups.Coxeter(list(label))
        assert _product_of_the_degrees(group) == int(group.order())


def test_the_degrees_of_a_finite_group_count_the_positive_roots_through_the_longest_element():
    r"""$\sum_i(d_i-1)$ is the length of the longest element, which the Cayley graph search finds."""
    for label in ("A", 2), ("B", 2), ("H", 3):
        group = Groups.Coxeter(list(label))
        positive_roots = sum((int(degree) - 1 for degree in group.degrees()), 0)
        longest = group.longest_element()
        assert int(group.word_length(longest)) == positive_roots
        assert longest * longest == group.one()


def test_the_growth_series_of_a_finite_group_is_its_solomon_polynomial():
    r"""$W(A_2)(t)=1+2t+2t^2+t^3$, a polynomial, and $W(B_2)(t)=1+2t+2t^2+2t^3+t^4$."""
    series = Groups.Coxeter(["A", 2]).poincare_series()
    assert series.numerator() * _polynomial((1,)) == _polynomial((1, 2, 2, 1)) * series.denominator()
    series = Groups.Coxeter(["B", 2]).poincare_series()
    assert series.numerator() * _polynomial((1,)) == _polynomial((1, 2, 2, 2, 1)) * series.denominator()


def test_the_growth_series_of_the_affine_a1_group_is_one_plus_t_over_one_minus_t():
    r"""The infinite dihedral Coxeter group has $W(t)=(1+t)/(1-t)$."""
    series = Groups.Coxeter([[1, -1], [-1, 1]]).poincare_series()
    assert series.numerator() * _polynomial((1, -1)) == _polynomial((1, 1)) * series.denominator()


def test_the_reciprocal_growth_series_at_one_is_the_reciprocal_of_the_order():
    r"""$\chi(W)=1/W(1)$ is $1/|W|$ for a finite group and $0$ for the affine $A_1$ group."""
    assert Groups.Coxeter(["A", 2]).euler_characteristic() == QQ(1) / QQ(6)
    assert Groups.Coxeter(["H", 3]).euler_characteristic() == QQ(1) / QQ(120)
    assert Groups.Coxeter([[1, -1], [-1, 1]]).euler_characteristic() == 0
    for label in ("A", 2), ("B", 2), ("H", 3):
        group = Groups.Coxeter(list(label))
        assert QQ(1) / group.euler_characteristic() == QQ(int(group.order()))


def test_the_degrees_and_the_longest_element_of_an_infinite_group_are_refused():
    r"""A growth series has a rational form for every Coxeter system; degrees and $w_0$ are finite only."""
    group = Groups.Coxeter([[1, -1], [-1, 1]])
    with pytest.raises(ValueError):
        group.degrees()
    with pytest.raises(ValueError):
        group.longest_element()
    assert group.poincare_series().denominator() == _polynomial((1, -1))


def test_the_growth_series_of_the_237_triangle_group_has_lehmer_polynomial_as_denominator():
    r"""The $(2,3,7)$ reflection triangle group's growth series is Lehmer's polynomial up to sign.

    The Coxeter matrix is the triangle with bonds $2,3,7$.
    """
    group = Groups.Coxeter([[1, 3, 2], [3, 1, 7], [2, 7, 1]])
    denominator = group.poincare_series().denominator()
    assert denominator == _polynomial(LEHMER_COEFFICIENTS) or denominator == -_polynomial(
        LEHMER_COEFFICIENTS
    )
    assert group.euler_characteristic() == -QQ(1) / QQ(84)


def test_the_growth_rate_of_the_237_triangle_group_is_lehmer_number():
    r"""The $(2,3,7)$ group grows at Lehmer's number, the largest root of Lehmer's polynomial.

    Lehmer's number is a Salem number, which is the growth rate Parry assigns to
    a cocompact hyperbolic Coxeter group and which Hironaka identifies as the
    minimal one among the planar cocompact reflection groups.
    """
    growth_rate = Groups.Coxeter([[1, 3, 2], [3, 1, 7], [2, 7, 1]]).growth_rate()
    assert _lehmer_value_at(growth_rate) == 0
    assert growth_rate > 1
    assert _lehmer_value_at(-growth_rate) != 0


def test_the_growth_rate_of_a_finite_group_and_of_the_affine_a1_group_is_one():
    r"""A finite group and an affine one grow polynomially or not at all: their rate is $1$."""
    assert Groups.Coxeter(["A", 2]).growth_rate() == 1
    assert Groups.Coxeter([[1, -1], [-1, 1]]).growth_rate() == 1


def test_a_reduced_word_of_an_element_has_its_length_and_its_product():
    r"""The word the Cayley graph search reads off has the length of the element and multiplies to it."""
    group = Groups.Coxeter(["A", 2])
    first, second = tuple(group.group_generators())
    element = first * second * first
    assert int(group.word_length(element)) == 3
    letters = tuple(group.reduced_word(element))
    assert letters[0] * letters[1] * letters[2] == element
    assert int(group.word_length(first * second)) == 2
    assert int(group.word_length(group.one())) == 0


def test_the_longest_element_of_a2_is_the_alternating_word():
    r"""$w_0$ of $A_2$ is $s_1s_2s_1$, of length the three positive roots."""
    group = Groups.Coxeter(["A", 2])
    first, second = tuple(group.group_generators())
    assert group.longest_element() == first * second * first



def _one_minus_power(degree):
    r"""The owned polynomial $1-t^{\text{degree}}$."""
    return _polynomial((1,)) - _polynomial(tuple(0 for _ in range(degree)) + (1,))


def test_the_simple_and_positive_roots_of_a_finite_system():
    r"""The rank counts the simple roots, and the positive roots number $\sum_i(d_i-1)$."""
    for label, expected in ((("A", 2), 3), (("B", 2), 4), (("G", 2), 6), (("H", 3), 15), (("A", 3), 6)):
        group = Groups.Coxeter(list(label))
        rank = sum(1 for _degree in group.degrees())
        positive = group.positive_roots()
        assert int(group.simple_roots().cardinality()) == rank
        assert int(positive.cardinality()) == expected
        assert int(positive.cardinality()) == sum(
            (int(degree) - 1 for degree in group.degrees()), 0
        )


def test_the_positive_roots_of_a2_are_the_simple_roots_and_their_sum():
    r"""The three positive roots of $A_2$ are $\alpha_1$, $\alpha_2$ and their sum."""
    first, second, third = tuple(Groups.Coxeter(["A", 2]).positive_roots())
    assert first + second == third or first + third == second or second + third == first


def test_the_fundamental_chamber_is_the_dual_cone_of_the_simple_roots():
    r"""$\alpha_1+\alpha_2$ is in the chamber of $A_2$, and $-(\alpha_1+\alpha_2)$ and $\alpha_1-\alpha_2$ are not."""
    group = Groups.Coxeter(["A", 2])
    chamber = group.fundamental_chamber()
    first, second = tuple(group.simple_roots())
    assert first + second in chamber
    assert -(first + second) not in chamber
    assert first - second not in chamber


def test_the_molien_series_of_the_invariant_ring_is_the_product_over_the_degrees():
    r"""$k[V]^{W(A_2)}$ has Molien series $1/((1-t^2)(1-t^3))$, and $W(H_3)$ the product over $2,6,10$."""
    series = Groups.Coxeter(["A", 2]).molien_series()
    expected = _one_minus_power(2) * _one_minus_power(3)
    assert series.numerator() == _polynomial((1,))
    assert series.denominator() == expected or series.denominator() == -expected
    series = Groups.Coxeter(["H", 3]).molien_series()
    expected = _one_minus_power(2) * _one_minus_power(6) * _one_minus_power(10)
    assert series.denominator() == expected or series.denominator() == -expected


def test_lehmer_number_is_in_the_owned_perron_and_salem_classes():
    r"""The $(2,3,7)$ growth rate is a Salem number, and the Salem numbers lie in the Perron numbers."""
    growth_rate = Groups.Coxeter([[1, 3, 2], [3, 1, 7], [2, 7, 1]]).growth_rate()
    assert growth_rate in PerronNumbers
    assert growth_rate in SalemNumbers


def test_the_two_classes_separate_what_their_definitions_separate():
    r"""$2$ and $3$ are Perron numbers, $\sqrt2$ and $1/2$ are not, and $3$ has no conjugate on the unit circle."""
    assert AA(2) in PerronNumbers
    assert AA(3) in PerronNumbers
    assert AA(3) not in SalemNumbers
    assert AA(2).sqrt() not in PerronNumbers
    assert (QQ(1) / QQ(2)) not in PerronNumbers
    assert AA(1) not in PerronNumbers
    assert AA(1) not in SalemNumbers


def test_the_growth_rate_of_a_finite_or_affine_group_is_not_a_perron_number():
    r"""The growth rate of a finite or affine system is $1$, which neither class contains."""
    assert Groups.Coxeter(["A", 2]).growth_rate() not in PerronNumbers
    assert Groups.Coxeter([[1, -1], [-1, 1]]).growth_rate() not in PerronNumbers


def test_the_growth_series_of_the_affine_a2_group_is_one_plus_t_plus_t2_over_one_minus_t_squared():
    r"""The affine $A_2$ system has $W(t)=(1+t+t^2)/(1-t)^2$, whose layers are $3k$ for $k\geq1$."""
    series = Groups.Coxeter(["A", 2, 1]).poincare_series()
    assert series.numerator() * (_one_minus_power(1) * _one_minus_power(1)) == _polynomial(
        (1, 1, 1)
    ) * series.denominator()
    assert Groups.Coxeter(["A", 2, 1]).euler_characteristic() == 0
