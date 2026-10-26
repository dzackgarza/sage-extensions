r"""Convex polytopes expose their ambient space, lattice points, support functions, normal fan, and 3D view."""

from sage_extensions.all import *  # noqa: F401,F403


def test_triangle_lattice_points_containment_and_normal_support() -> None:
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (0, 3), (6, 0)))
    inner = lattice((1, 1))
    edge = lattice((0, 1))
    normal = lattice.dual_module()((1, 0))

    assert triangle.ambient_space().base_ring() is QQ
    assert triangle.ambient_space().module_rank() == 2
    assert triangle.is_compact()
    assert triangle.integral_points().cardinality() == cardinal(16)
    assert triangle.interior_integral_points().cardinality() == cardinal(4)
    assert triangle.boundary_integral_points().cardinality() == cardinal(12)
    assert triangle.contains_point(edge)
    assert triangle.interior_contains_point(inner)
    assert not triangle.interior_contains_point(edge)
    assert triangle.normal_value(normal, edge) == 0
    assert triangle.normal_value(normal, inner) == 1
    assert triangle.normal_supports_point(normal, edge)
    assert not triangle.normal_supports_point(normal, inner)
    assert triangle.normal_fan().rays().cardinality() == cardinal(3)


def test_tetrahedron_has_local_threejs_html_view() -> None:
    lattice = ZZ.free_module(3)
    tetrahedron = ConvexPolytopes(lattice)(
        ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    )
    html = tetrahedron.threejs_html()

    assert isinstance(html, str)
    assert "<script" in html
