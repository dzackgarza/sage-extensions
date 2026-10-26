r"""Chart changes between the standard affine charts `U_i = D_+(x_i)` of projective space."""

from sage_extensions.all import *


def test_the_projective_line_transition_inverts_the_ratio() -> None:
    r"""On `U_0 \cap U_1`, `x_0/x_1 = (x_1/x_0)^{-1}`: the chart change is `t \mapsto 1/t`."""
    line = ProjectiveSpaces(QQ)(1)
    forward = line.standard_chart_transition(0, 1).forward()
    to_source = line.standard_chart_overlap(0, 1).inclusion().coordinate_algebra_morphism()
    to_target = line.standard_chart_overlap(1, 0).inclusion().coordinate_algebra_morphism()
    one_over_zero = to_source(
        line.standard_affine_chart(0).coordinate_algebra().algebra_generator("x1_over_x0")
    )
    zero_over_one = to_target(
        line.standard_affine_chart(1).coordinate_algebra().algebra_generator("x0_over_x1")
    )

    assert forward.coordinate_algebra_morphism()(zero_over_one) == one_over_zero.inverse_of_unit()


def test_a_projective_plane_chart_change_divides_the_two_ratios() -> None:
    r"""On `U_0 \cap U_2`, `x_1/x_2 = (x_1/x_0)(x_2/x_0)^{-1}`."""
    plane = ProjectiveSpaces(QQ)(2)
    forward = plane.standard_chart_transition(0, 2).forward()
    to_source = plane.standard_chart_overlap(0, 2).inclusion().coordinate_algebra_morphism()
    to_target = plane.standard_chart_overlap(2, 0).inclusion().coordinate_algebra_morphism()
    chart_zero = plane.standard_affine_chart(0).coordinate_algebra()
    chart_two = plane.standard_affine_chart(2).coordinate_algebra()

    one_over_two = to_target(chart_two.algebra_generator("x1_over_x2"))
    one_over_zero = to_source(chart_zero.algebra_generator("x1_over_x0"))
    two_over_zero = to_source(chart_zero.algebra_generator("x2_over_x0"))

    assert forward.coordinate_algebra_morphism()(one_over_two) == (
        one_over_zero * two_over_zero.inverse_of_unit()
    )
