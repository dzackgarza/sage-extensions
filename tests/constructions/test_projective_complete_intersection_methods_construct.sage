r"""Projective complete intersections expose adjunction, family/base-change, and topology data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_quadric_cubic_curve_adjunction_data() -> None:
    space = ProjectiveSpaces(QQ)(3, names=("x0", "x1", "x2", "x3"))
    x0, x1, x2, x3 = space.homogeneous_coordinate_generators()
    curve = space.closed_subscheme(
        x0 * x1 - x2**2,
        x0**3 + x1**3 + x3**3,
    )
    adjunction = curve.adjunction_isomorphism()

    assert curve.complete_intersection_ambient() is space
    assert tuple(curve.defining_degrees()) == (2, 3)
    assert curve.projective_degree() == 6
    assert curve.adjunction_twist_degree() == 1
    assert curve.anticanonical_twist_degree() == -1
    assert curve.is_gorenstein()
    assert curve.restricted_ambient_canonical_bundle().degree() == -4
    assert curve.normal_determinant_line_bundle().degree() == 5
    assert adjunction.domain() is curve.canonical_line_bundle()
    assert adjunction.codomain() is curve.adjunction_target()


def test_hesse_family_retains_family_and_base_change_maps() -> None:
    parameter = QQ["t"]
    plane = ProjectiveSpaces(parameter)(2, names=("x", "y", "z"))
    t = parameter.algebra_generator("t")
    x, y, z = plane.homogeneous_coordinate_generators()
    family = plane.closed_subscheme(x**3 + y**3 + z**3 - 3 * t * x * y * z)
    specialize = parameter.Mor(QQ)({"t": QQ.zero()})
    changed = family.base_change(specialize)
    projection = changed.base_change_projection()

    assert family.family_base_scheme() is family.base_scheme()
    assert family.family_morphism() == family.structure_morphism()
    assert changed.base_change_source_complete_intersection() is family
    assert projection.domain() is changed
    assert projection.codomain() is family


def test_fermat_quartic_exposes_k3_topology_and_hodge_structure() -> None:
    space = ProjectiveSpaces(QQ)(3)
    x0, x1, x2, x3 = space.homogeneous_coordinate_generators()
    quartic = space.closed_subscheme(x0**4 + x1**4 + x2**4 + x3**4)
    k3 = SmoothQuarticK3CompleteIntersections(QQ)(quartic)
    topology = k3.integral_topology()
    hodge = k3.hodge_structure()

    assert topology.integral_cohomology(2).module_rank() == 22
    assert hodge.hodge_number(2, 0) == 1
    assert hodge.hodge_number(1, 1) == 20
    assert hodge.hodge_number(0, 2) == 1
