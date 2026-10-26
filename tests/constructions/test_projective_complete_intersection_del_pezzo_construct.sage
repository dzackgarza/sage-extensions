r"""A smooth cubic surface is a degree-three del Pezzo complete intersection."""

from sage_extensions.all import *  # noqa: F401,F403


def test_fermat_cubic_surface_has_anticanonical_hyperplane_class_and_degree_three() -> None:
    space = ProjectiveSpaces(QQ)(3)
    x0, x1, x2, x3 = space.homogeneous_coordinate_generators()
    surface = space.closed_subscheme(x0**3 + x1**3 + x2**3 + x3**3)

    assert surface.is_complete_intersection()
    assert surface in ProperSurfaces(QQ)
    assert surface in ProjectiveSurfaces(QQ)
    assert surface.expected_dimension() == 2
    assert surface.canonical_bundle() == surface.canonical_line_bundle()
    assert surface.anticanonical_bundle() == surface.anticanonical_line_bundle()
    assert surface.canonical_line_bundle().degree() == -1
    assert surface.anticanonical_line_bundle().degree() == 1
    assert surface.is_del_pezzo()
    assert DelPezzoSurfaces(surface.scheme_base_ring())(surface).del_pezzo_degree() == 3
    assert surface.is_normal()
