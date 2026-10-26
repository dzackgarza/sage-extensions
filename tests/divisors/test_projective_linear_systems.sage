r"""Linear systems on the projective plane: base loci, dimensions, restrictions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pencil_of_lines_through_a_point_has_that_point_as_base_locus() -> None:
    r"""``<x0, x1> subset H^0(P^2, O(1))`` is a pencil with base locus ``(0:0:1)``.

    Its rational map is the projection ``P^2 --> P^1`` from ``(0:0:1)``,
    defined exactly on the complement of the base point.
    """
    plane = ProjectiveSpaces(QQ)(2, names=("x0", "x1", "x2"))
    ring = plane.homogeneous_coordinate_ring()
    bundle = plane.O(1)
    sections = bundle.global_sections()
    x0 = sections.section_from_homogeneous_polynomial(ring("x0"))
    x1 = sections.section_from_homogeneous_polynomial(ring("x1"))

    system = bundle.linear_system((x0, x1))
    base_locus = system.base_locus()

    assert system.projective_dimension() == 1
    assert not system.is_basepoint_free()
    assert base_locus.dimension() == 0
    assert base_locus.contains_point(plane.point((0, 0, 1)))
    assert not base_locus.contains_point(plane.point((1, 0, 0)))
    assert system.domain_of_definition().contains_point(plane.point((1, 0, 0)))
    assert not system.domain_of_definition().contains_point(plane.point((0, 0, 1)))


def test_complete_hyperplane_system_has_empty_base_locus_and_everywhere_defined_map() -> None:
    r"""``|O(1)|`` on ``P^2`` is basepoint free of dimension 2; its map is the identity of ``P^2``."""
    plane = ProjectiveSpaces(QQ)(2)
    system = plane.O(1).linear_system()

    assert system.is_basepoint_free()
    assert system.base_locus().is_empty()
    assert system.projective_dimension() == 2
    assert system.associated_morphism().is_isomorphism()


def test_complete_quadrics_and_restriction_to_a_line_keep_expected_dimensions() -> None:
    r"""``|O(2)|`` on ``P^2`` has dimension 5; ``H^0(P^2, O(2)) -> H^0(L, O(2))`` for ``L = V(x)``.

    The restriction is onto the 3-dimensional ``H^0(P^1, O(2))`` with kernel
    ``x * H^0(O(1))``, of dimension 3.
    """
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    bundle = plane.O(2)
    ring = plane.homogeneous_coordinate_ring()
    line = plane.closed_subscheme(ring("x"))
    restriction = bundle.restriction_map(line)

    assert bundle.linear_system().is_basepoint_free()
    assert bundle.linear_system().projective_dimension() == 5
    assert restriction.domain().dimension() == 6
    assert restriction.codomain().dimension() == 3
    assert restriction.kernel().dimension() == 3
    assert restriction.cokernel().dimension() == 0
