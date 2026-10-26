r"""The Hesse pencil has good locus D(t^3-1) and exceptional locus V(t^3-1)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hesse_parameter_line_retains_its_coordinate() -> None:
    hesse = HesseBertiniFamily()
    parameter_ring = hesse.parameter_ring()
    parameter_scheme = hesse.parameter_scheme()
    t = hesse.parameter()

    assert parameter_scheme.coordinate_algebra() is parameter_ring
    assert t in parameter_ring


def test_hesse_good_and_exceptional_parameter_loci_are_complementary() -> None:
    hesse = HesseBertiniFamily()
    parameter_scheme = hesse.parameter_scheme()
    t = hesse.parameter()
    discriminant_factor = t**3 - 1

    assert hesse.exceptional_parameter_locus() == parameter_scheme.closed_subscheme(
        discriminant_factor
    )
    assert hesse.good_parameter_locus() == parameter_scheme.distinguished_open(
        discriminant_factor
    )
    assert hesse.parameter_is_good(QQ(0))
    assert not hesse.parameter_is_good(QQ(1))


def test_hesse_bertini_statement_records_exact_characteristic_zero_hypotheses() -> None:
    hesse = HesseBertiniFamily()

    assert hesse.theorem_hypotheses()
    assert hesse.theorem_conclusion_is_exact()
