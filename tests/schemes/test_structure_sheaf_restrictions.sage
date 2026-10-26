r"""Covers and containments of distinguished opens.

Derivation: `D(f_1), \dots, D(f_n)` cover `\operatorname{Spec} A` iff
`(f_1, \dots, f_n) = A`, and `D(g) \subseteq D(f)` iff `g` lies in the radical of
`(f)`; both follow from `V(I) = \emptyset \iff I = A`.  The origin lies in neither
`D(x)` nor `D(y)`.
"""

from sage_extensions.all import *


def test_d_x_and_d_y_miss_the_origin_while_d_x_and_d_1_minus_x_cover_the_line() -> None:
    plane_ring = QQ.polynomial_ring(("x", "y"))
    x, y = plane_ring.algebra_generator("x"), plane_ring.algebra_generator("y")
    plane = plane_ring.affine_spectrum()
    line_ring = QQ.polynomial_ring("t")
    t = line_ring.algebra_generator("t")
    line = line_ring.affine_spectrum()

    assert not plane.is_covered_by((plane.distinguished_open(x), plane.distinguished_open(y)))
    assert line.is_covered_by((line.distinguished_open(t), line.distinguished_open(1 - t)))


def test_d_xy_lies_in_d_x_but_d_y_does_not() -> None:
    plane_ring = QQ.polynomial_ring(("x", "y"))
    x, y = plane_ring.algebra_generator("x"), plane_ring.algebra_generator("y")
    plane = plane_ring.affine_spectrum()
    open_x = plane.distinguished_open(x)

    assert plane.distinguished_open(x * y).is_contained_in(open_x)
    assert not plane.distinguished_open(y).is_contained_in(open_x)
