r"""Second-order jets on P^2 at a rational point form a three-dimensional space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_second_order_jets_of_conics_at_a_rational_point() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(2)
    point = plane.point_morphism((1, 2, 3))
    jets = bundle.jet_evaluation(point, 2).codomain()

    assert jets in ProjectiveJetSpaces(QQ)
    assert jets.jet_line_bundle() is bundle
    assert jets.jet_point() is point
    assert jets.jet_order() == 2
    assert jets.jet_projective_space() is plane
    assert jets.jet_residue_field() == QQ
    assert jets.dimension() == 3
