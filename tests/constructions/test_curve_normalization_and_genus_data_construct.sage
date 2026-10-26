r"""A rational singular plane quintic retains its normalization and local delta data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rational_quintic_normalization_and_genus_comparison() -> None:
    plane = Schemes(QQ).projective_space(2, names=("X", "Y", "Z"))
    X = plane.coordinate_ring().algebra_generator("X")
    Y = plane.coordinate_ring().algebra_generator("Y")
    Z = plane.coordinate_ring().algebra_generator("Z")
    curve = plane.closed_subscheme(
        Y**2 * Z**3 - X * (X - Z) ** 2 * (X - 4 * Z) ** 2
    )
    normalization = curve.normalization_curve()
    morphism = curve.normalization_morphism()
    contributions = curve.local_delta_contributions()
    comparison = curve.genus_comparison()

    assert curve.curve() is curve
    assert curve.normalization_data() is curve
    assert normalization.arithmetic_genus() == 0
    assert morphism.domain() is normalization
    assert morphism.codomain() is curve
    assert contributions is curve.local_contributions()
    assert contributions.cardinality() == cardinal(3)
    assert curve.total_delta_contribution() == 6
    assert curve.is_geometrically_integral()
    assert curve.normalization_is_connected()
    assert comparison.arithmetic_genus() == 6
    assert comparison.geometric_genus() == 0
    assert comparison.total_delta_contribution() == 6
    assert comparison.holds()
