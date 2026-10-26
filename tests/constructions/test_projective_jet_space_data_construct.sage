r"""Projective jet spaces retain their chart, stalk, quotient, and coordinate data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_second_order_conic_jet_retains_local_data() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(2)
    point = plane.point_morphism((1, 2, 3))
    jets = bundle.jet_evaluation(point, 2).codomain()

    assert jets.jet_homogeneous_degree() == 2
    assert jets.jet_affine_chart() is plane.standard_affine_chart(0)
    assert jets.jet_spectrum_point().local_ring() is jets.jet_stalk()
    assert jets.jet_local_quotient().quotient_source() is jets.jet_stalk()
    assert jets.jet_maximal_ideal() is jets.jet_stalk().maximal_ideal()


def test_coordinate_point_records_standard_chart_index() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((0, 1, 0))
    jets = plane.O(3).jet_evaluation(point, 1).codomain()

    assert jets.jet_coordinate_index() == 1
    assert jets.jet_affine_chart() is plane.standard_affine_chart(1)
    assert jets.jet_homogeneous_degree() == 3
