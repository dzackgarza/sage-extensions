r"""An ADE log pair exposes the retained Dynkin, toric, polygon-order, and rendering metadata."""

from sage_extensions.all import *  # noqa: F401,F403


def test_e6_log_pair_metadata_aliases_are_the_retained_base_data() -> None:
    pair = ADELogPairs(QQ)("E", 6)

    assert pair.toric_scheme() is pair.log_scheme()
    assert pair.is_base()
    assert not pair.is_cover()
    assert pair.codimension_in_toric_scheme() == 0
    assert pair.letter() == pair.dynkin_letter() == "E"
    assert pair.variant() == pair.dynkin_variant()
    assert pair.p_star() == pair.distinguished_point()
    ordered_vertices = tuple(pair.polygon_vertex_order())
    assert len(ordered_vertices) == int(pair.polygon().vertices().cardinality())
    assert all(vertex in pair.polygon().vertices() for vertex in ordered_vertices)
    assert pair.side_decorations().cardinality() == cardinal(2)


def test_e6_log_pair_integral_invariants_and_svg_are_views_of_the_live_polygon() -> None:
    pair = ADELogPairs(QQ)("E", 6)
    polygon = pair.polygon()
    invariants = pair.integral_invariants()
    svg = pair.ade_svg()

    assert invariants["dimension"] == pair.toric_scheme().relative_dimension()
    assert invariants["volume"] == polygon.volume()
    assert invariants["normalized_volume"] == polygon.normalized_volume()
    assert invariants["n_integral_points"] == polygon.n_integral_points()
    assert 'data-role="ade-polygon"' in svg
    assert 'data-ade-type="E6"' in svg
