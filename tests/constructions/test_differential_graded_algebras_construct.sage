r"""The algebraic de Rham complex is a differential graded algebra."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_de_rham_algebra_exposes_the_dga_structure() -> None:
    line = QQ.polynomial_ring("x")
    x = line.algebra_generator("x")
    dga = line.de_rham_algebra()
    element = dga(x)
    differential = dga.differential()
    component = dga.differential_component(0)
    underlying = dga.underlying_graded_algebra()

    assert dga in DifferentialGradedAlgebras(QQ)
    assert dga.d(element) == differential(element)
    assert differential(differential(element)) == dga.zero()
    assert differential.square_zero_decision() is True
    assert 0 in dga.degree_index_set()
    assert 1 in dga.degree_index_set()
    assert component.domain() is dga.graded_piece(0)
    assert component.codomain() is dga.graded_piece(1)
    assert underlying in GradedAlgebras(QQ)
    assert dga.graded_algebra() is underlying
    assert dga.dga() is dga
    assert dga.is_differential_graded_module()
    assert dga.cohomology_algebra() in CohomologyAlgebras(QQ)


def test_de_rham_algebra_regular_action_is_multiplication() -> None:
    dga = QQ.polynomial_ring("x").de_rham_algebra()
    regular = dga.regular_dg_module()
    x = dga(dga.de_rham_source_algebra().algebra_generator("x"))
    action = dga.right_action()

    assert regular in DifferentialGradedModules(dga)
    assert regular.dga() is dga
    assert dga.act(dga.one(), x) == x
    assert action(dga.one(), x) == x

