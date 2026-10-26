r"""Q[[t]] is complete for (t) and exposes its chosen formal parameter."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rational_formal_power_series_ring_has_one_formal_parameter() -> None:
    series = QQ.power_series_ring("t")
    t = series.power_series_variable()
    parameters = series.formal_parameter_set()

    assert series in FormalPowerSeriesRings(QQ)
    assert series.cardinality() == continuum
    assert parameters.cardinality() == cardinal(1)
    assert series.formal_parameter("t") == t
    assert parameters.an_element() == t
    assert t.coefficient(0) == QQ.zero()
    assert t.coefficient(1) == QQ.one()
    geometric = (series.one() - t).inverse_of_unit()
    assert geometric.coefficient(0) == QQ.one()
    assert geometric.coefficient(7) == QQ.one()

