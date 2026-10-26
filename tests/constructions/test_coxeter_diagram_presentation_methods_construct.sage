r"""Coxeter diagrams expose vertex-complete drawing and TikZ presentation data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_preferred_and_equivariant_positions_cover_every_vertex() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])
    positions = diagram.preferred_positions()
    equivariant = diagram.equivariant_positions(diagram.Aut().one())

    for vertex in diagram.vertices():
        assert vertex in positions
        assert vertex in equivariant


def test_rooted_a2_node_colors_are_declared_drawing_labels() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2], rooted=True)
    conventions = diagram.drawing_conventions()

    assert conventions is not None
    for vertex in diagram.vertices():
        assert isinstance(diagram.node_color(vertex), str)


def test_a2_tikz_and_plot_expose_live_presentations() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])

    assert isinstance(diagram.tikz_picture(), str)
    assert isinstance(diagram.tikz(), str)
    assert diagram.plot() is not None
