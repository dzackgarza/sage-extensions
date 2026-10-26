r"""Polynomial algebras retain their total grading, graded derivations, and standard charts."""

from sage_extensions.all import *  # noqa: F401,F403


def _graded_plane():
    return QQ.free_module(("x", "y")).symmetric_algebra()


def test_polynomial_plane_exposes_its_grading_and_homogeneous_elements() -> None:
    algebra = _graded_plane()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    mixed = x + y * y

    assert algebra in GradedAlgebras(QQ)
    assert algebra.grading_compatibility_decision() is True
    assert algebra.homogeneous_degree(x * y) == 2
    assert x.degree() == 1
    assert x.is_homogeneous()
    assert not mixed.is_homogeneous()


def test_polynomial_plane_has_the_expected_degree_minus_one_derivation() -> None:
    algebra = _graded_plane()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    derivations = algebra.graded_derivations(shift=-1)
    partial_x = derivations({"x": algebra.one(), "y": algebra.zero()})

    assert partial_x(x) == algebra.one()
    assert partial_x(y) == algebra.zero()
    assert partial_x(x * y) == y
    assert partial_x.degree_shift() == -1


def test_restricting_scalars_retains_the_grading() -> None:
    algebra = _graded_plane()
    inclusion = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    restricted = algebra.restrict_scalars(inclusion)
    x = restricted.algebra_generator("x")

    assert restricted in GradedAlgebras(ZZ)
    assert restricted.homogeneous_degree(x) == 1


def test_standard_degree_zero_chart_of_the_projective_line_has_dimension_one() -> None:
    algebra = _graded_plane()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    at_x = algebra.localization(x)
    at_xy = algebra.localization(x * y)
    algebra = CommutativeGradedIntegralDomains(QQ)(algebra)
    chart = algebra.degree_zero_chart(at_x)
    overlap = algebra.degree_zero_chart(at_xy)
    restriction = algebra.degree_zero_chart_restriction(at_x, at_xy)

    assert chart in Algebras(QQ).Associative().Unital().Commutative()
    assert chart.krull_dimension() == 1
    assert restriction.domain() is chart
    assert restriction.codomain() is overlap
