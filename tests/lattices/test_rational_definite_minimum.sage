r"""The minimum algorithm is the minimum of an integral lattice, not a rational space.

For the positive line over QQ, the nonzero vectors e/n have squares 1/n^2.
Their infimum is zero and is not attained, so the integral-span minimum one is
not the answer for that quadratic space.
"""

import pytest

from sage_extensions.all import *


def test_minimum_is_computed_for_the_integral_line() -> None:
    assert Lattices(ZZ)(1).minimum() == 1


def test_the_rational_line_does_not_report_its_integral_span_minimum() -> None:
    line = Lattices(QQ)(1)
    (e,) = line.module_generators()

    assert all(line(QQ(1) / n * e).q() == QQ(1) / (n * n) for n in (2, 3, 5))
    with pytest.raises(AssertionError):
        line.minimum()
    with pytest.raises(AssertionError):
        line.shortest_vectors()
    with pytest.raises(AssertionError):
        line.is_voronoi_perfect()
