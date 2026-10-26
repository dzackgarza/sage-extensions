r"""Archived standard-cardinality facts not already covered by live catalogues."""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/sets/cardinals.py",
    "live_owner": "sage_extensions/categories/sets/cardinals.py",
    "disposition": "reconciled-live-owner",
}


def test_matrix_ring_cardinality_tracks_the_coefficient_ring() -> None:
    rational_matrices = QQ.matrix_space(2)
    real_matrices = RR.matrix_space(2)

    assert rational_matrices.cardinality() == aleph0
    assert real_matrices.cardinality() == continuum


def test_rational_power_series_have_continuum_cardinality() -> None:
    power_series = QQ.power_series_ring("t")

    assert power_series.cardinality() == continuum
    # A finitely generated QQ-algebra is a quotient of some QQ[x_1, ..., x_n], hence
    # countable, so the continuum-sized QQ[[t]] is not finitely generated.
    assert not power_series.is_finitely_generated()
    assert tuple(power_series.formal_parameter_set()) == ("t",)


def test_rational_polynomial_ring_is_countable() -> None:
    polynomial = QQ.polynomial_ring("x")

    assert polynomial.cardinality() == aleph0
