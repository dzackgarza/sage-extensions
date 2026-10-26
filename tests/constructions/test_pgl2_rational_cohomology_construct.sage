r"""Rational coefficient change kills the degree-two torsion of PGL2(C)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pgl2_rational_cohomology_has_the_expected_ranks() -> None:
    topology = PGL2IntegralTopology()

    assert topology.rational_cohomology(0).module_rank() == cardinal(1)
    assert topology.rational_cohomology(2).module_rank() == cardinal(0)
    assert topology.rational_cohomology(3).module_rank() == cardinal(1)


def test_pgl2_degree_two_coefficient_change_kills_integral_torsion() -> None:
    topology = PGL2IntegralTopology()
    change = topology.coefficient_change_to_rationals(2)

    assert change.domain() is topology.integral_cohomology(2)
    assert change.codomain() is topology.rational_cohomology(2)
    assert change.is_zero()
