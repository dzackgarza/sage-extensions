r"""A DGA differential component is the selected degree-one map on homogeneous pieces."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_degree_zero_differential_component_is_the_actual_derivative() -> None:
    dga = QQ.polynomial_ring("x").de_rham_algebra()
    x = dga(dga.de_rham_source_algebra().algebra_generator("x"))
    component = dga.differential_component(0)
    degree_zero_part = x.homogeneous_component(0)
    degree_one_derivative = dga.d(x).homogeneous_component(1)

    assert isinstance(component, DifferentialComponentMorphism)
    assert component.domain() is dga.graded_piece(0)
    assert component.codomain() is dga.graded_piece(1)
    assert component(degree_zero_part) == degree_one_derivative


def test_negative_differential_component_is_the_zero_map_into_degree_zero() -> None:
    dga = QQ.polynomial_ring("x").de_rham_algebra()
    component = dga.differential_component(-1)
    source = component.domain()
    target = component.codomain()

    assert isinstance(component, DifferentialComponentMorphism)
    assert source.module_rank() == cardinal(0)
    assert target is dga.graded_piece(0)
    assert component(source.zero()) == target.zero()
