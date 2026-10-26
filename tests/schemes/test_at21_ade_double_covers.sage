r"""The ADE double covers of Alexeev--Thompson: deck involution and singularity."""

from sage_extensions.all import *


def test_the_deck_involution_of_the_d4_double_cover_squares_to_the_identity_and_preserves_the_cover_map() -> None:
    r"""On each chart of the \(D_4\) double cover \(\pi\colon X\to Y\), the deck involution \(\sigma\) satisfies
    \(\sigma^2 = \mathrm{id}\) and \(\pi\circ\sigma = \pi\).

    Source: Alexeev--Thompson, *ADE surfaces and their moduli*, §4 (double covers of toric surfaces).
    """
    pair = LogPairs(QQ).at21("D", 4)
    cover = pair.double_cover(pair.source_normal_form_section(constant=1))

    for cone in cover.scheme().gluing_datum().chart_indices():
        deck = cover.local_deck_involution(cone)
        assert deck * deck == deck.domain().categorical_identity_morphism()
        assert deck != deck.domain().categorical_identity_morphism()
        assert cover.local_cover_map(cone) * deck == cover.local_cover_map(cone)


def test_the_singular_e8_double_cover_has_an_e8_point_with_milnor_and_tjurina_number_eight() -> None:
    r"""The singular \(E_8\) specialization acquires an \(E_8\) singularity \(x^2+y^3+z^5=0\):
    Milnor number \(\mu = 8\), and \(\tau = \mu\) since the singularity is quasi-homogeneous.

    Source: Arnold--Gusein-Zade--Varchenko, *Singularities of Differentiable Maps* I, §15 (simple singularities);
    K. Saito, *Quasihomogene isolierte Singularitäten von Hyperflächen* (1971) (\(\mu = \tau\)).
    """
    pair = LogPairs(QQ).at21("E", 8)
    cover = pair.double_cover(pair.source_normal_form_section(constant=0))
    comparison = dict(cover.local_global_singularity_comparison())

    assert cover.dynkin_diagram().cardinality() == 8
    assert comparison["global_dynkin_rank"] == 8
    assert comparison["local_milnor_number"] == 8
    assert comparison["local_tjurina_number"] == 8
