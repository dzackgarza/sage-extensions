r"""Section rings of the Veronese conic and the Segre quadric."""

from sage_extensions.all import *  # noqa: F401,F403


def test_section_ring_of_O_2_on_P1_is_the_coordinate_ring_of_the_conic() -> None:
    r"""``R(P^1, O(2)) = Q[u, v, w]/(uw - v^2)``: pieces of rank ``2d + 1``.

    With ``u = x0^2``, ``v = x0 x1``, ``w = x1^2``: ``u w = v^2`` in degree 2,
    while ``u^2 != v w``.
    """
    line = ProjectiveSpaces(QQ)(1, names=("x0", "x1"))
    coordinates = line.homogeneous_coordinate_ring()
    x0, x1 = coordinates("x0"), coordinates("x1")
    bundle = line.O(2)
    ring = bundle.section_ring()
    sections = bundle.global_sections()

    def degree_one(form):
        return ring.homogeneous_component_element(1, sections.section_from_homogeneous_polynomial(form))

    u, v, w = degree_one(x0**2), degree_one(x0 * x1), degree_one(x1**2)

    assert ring.graded_piece(1).module_rank() == 3
    assert ring.graded_piece(2).module_rank() == 5
    assert ring.graded_piece(3).module_rank() == 7
    assert u * w == v * v
    assert u * u != v * w
    assert ring.homogeneous_degree(u * w) == 2


def test_the_two_roads_of_the_section_ring_constructor_record_one_ambient_category() -> None:
    r"""``R(P^1, O(2))`` and ``R(P^2, O(1))`` are both objects of ``SectionRings(QQ)``.

    One constructor asks for both: ``SectionRings(base)(L)`` builds the
    semigroup algebra of a line bundle whose degree-one sections are linearly
    independent, and ``SectionRings(base)(X, D)`` builds the ring of the cone
    over a divisor polytope.  The category that asked is defining construction
    data (``OWN-15``), and ``Mor`` is stated over the ambient category, so the
    two roads have to record the same one.
    """
    line = ProjectiveSpaces(QQ)(1, names=("x0", "x1"))
    from_bundle = line.O(2).section_ring()
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    plane = fans.projective_space_fan().toric_variety(QQ)
    from_divisor = plane.section_ring(plane.hyperplane_divisor())

    assert from_bundle.ambient_category() == SectionRings(QQ)
    assert from_divisor.ambient_category() == SectionRings(QQ)
    assert from_bundle.ambient_category() == from_divisor.ambient_category()


def test_section_ring_of_O_1_1_on_P1_x_P1_is_the_coordinate_ring_of_the_segre_quadric() -> None:
    r"""``R(P^1 x P^1, O(1,1))`` has pieces of rank ``(d + 1)^2``: 4, 9.

    The Segre relation ``(x0 y0)(x1 y1) = (x0 y1)(x1 y0)`` holds in degree 2.
    """
    first = ProjectiveSpaces(QQ)(1, names=("x0", "x1"))
    second = ProjectiveSpaces(QQ)(1, names=("y0", "y1"))
    quadric = first * second
    coordinates = quadric.homogeneous_coordinate_ring()
    x0, x1, y0, y1 = coordinates("x0"), coordinates("x1"), coordinates("y0"), coordinates("y1")
    bundle = quadric.O(1, 1)
    ring = bundle.section_ring()
    sections = bundle.global_sections()

    def degree_one(form):
        return ring.homogeneous_component_element(1, sections.section_from_homogeneous_polynomial(form))

    assert ring.graded_piece(1).module_rank() == 4
    assert ring.graded_piece(2).module_rank() == 9
    assert degree_one(x0 * y0) * degree_one(x1 * y1) == degree_one(x0 * y1) * degree_one(x1 * y0)
    assert degree_one(x0 * y0) * degree_one(x0 * y0) != degree_one(x0 * y1) * degree_one(x1 * y0)
