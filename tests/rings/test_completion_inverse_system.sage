r"""Completion is the represented inverse limit, not a selected finite stage."""

from sage_extensions.all import *


def test_power_series_constructor_retains_the_same_adic_completion_data() -> None:
    series = QQ.power_series_ring("t")
    assert series in AdicallyCompleteRings()
    source = series.completion_source()
    t = source.algebra_generator("t")
    assert series.completion_ideal().ring() is source
    assert series.ideal_of_definition().ring() is series
    assert series.completion_map().domain() is source
    assert series.completion_map().codomain() is series
    assert series.adic_projection(3)(series.completion_map()(t**3)) == series.adic_truncation(3).zero()
    assert series.adic_projection(4)(series.completion_map()(t**3)) != series.adic_truncation(4).zero()

