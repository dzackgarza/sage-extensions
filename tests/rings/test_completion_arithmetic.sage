r"""Precision-aware arithmetic on represented adic completions.

The completion is the inverse limit.  A private finite approximation may prove
inequality, but agreement at its selected precision is never promoted to exact
equality.  Exact source expressions and maintained exact/lazy series engines
retain stronger information when it is genuinely available.
"""

import pytest

from sage_extensions.all import *
from sage_extensions.logic import Unknown, ask


def test_exact_polynomial_images_survive_beyond_a_low_adic_stage() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    completion = plane.adic_completion(plane.ideal(x, y), precision=3)
    include = completion.completion_map()
    late = include(x**5)

    assert completion.adic_projection(3)(late) == completion.adic_truncation(3).zero()
    assert late != completion.zero()
    assert include(x + y) == include(x) + include(y)
    assert include(x * y) == include(x) * include(y)


def test_exact_zero_and_exact_lazy_inverse_are_decided_in_the_completion() -> None:
    line = QQ.polynomial_ring(("x",))
    x = line.algebra_generator("x")
    completion = line.adic_completion(line.ideal(x))
    x_hat = completion.completion_map()(x)
    zero = completion.completion_map()(line.zero())

    assert zero.is_zero()
    assert not zero
    with pytest.raises(TypeError):
        hash(zero)

    unit = completion.one() - x_hat
    inverse = unit.inverse_of_unit()
    assert unit * inverse == completion.one()




def test_finite_p_adic_products_retain_exact_source_expressions() -> None:
    coarse = Zp(5, 4, type="fixed-mod")
    product = coarse(-1) * coarse(1)

    assert product.exact_source_expression() == ZZ(-1)
    assert product == -coarse.one()


def test_presented_completion_preserves_genuine_nilpotence_not_truncation_nilpotence() -> None:
    fat_plane = (QQ.free_module(("x", "y")).symmetric_algebra()).quotient_by_relations(("x^2",),
    )
    x = fat_plane.algebra_generator("x")
    y = fat_plane.algebra_generator("y")
    maximal = fat_plane.ideal(x, y)
    completion = fat_plane.adic_completion(maximal, precision=4)
    include = completion.completion_map()
    x_hat = include(x)
    y_hat = include(y)

    assert x_hat != completion.zero()
    assert (x_hat**2).is_zero()
    assert x_hat**2 == completion.zero()

    # y^4 is nonzero in the completion, although the selected A/m^4
    # approximation agrees with zero. The current equality procedure retains
    # that undecided proposition; the next exact source quotient witnesses
    # nonvanishing without changing the selected computation precision.
    zero_statement = (y_hat**4).is_zero()
    assert ask(zero_statement) is Unknown
    with pytest.raises(TypeError):
        bool(zero_statement)
    assert completion.adic_projection(5)(y_hat**4) != completion.adic_truncation(5).zero()

    assert completion.adic_projection(4)(y_hat**4) == completion.adic_truncation(4).zero()
    assert completion.adic_projection(3)(y_hat**2) != completion.adic_truncation(3).zero()
