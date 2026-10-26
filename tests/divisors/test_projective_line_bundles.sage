r"""The line bundles ``O(d)`` on projective spaces."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sections_of_O_d_on_P1_and_positivity_of_O_1() -> None:
    r"""``h^0(P^1, O(d)) = d + 1`` for ``d >= 0`` and ``0`` for ``d < 0``; ``O(1)`` is ample and basepoint free.

    Hartshorne, *Algebraic Geometry*, III.5.1.  The transition unit of
    ``O(1)^2`` is the square of that of ``O(1)``.
    """
    line = ProjectiveSpaces(QQ)(1)
    bundle = line.O(1)

    assert bundle.degree() == 1
    assert [line.O(d).global_sections().module_rank() for d in (-2, -1, 0, 1, 2, 3)] == [0, 0, 1, 2, 3, 4]
    assert bundle.is_ample()
    assert bundle.is_basepoint_free()
    assert bundle.tensor_power(2).transition_unit(0, 1) == bundle.transition_unit(0, 1) ** 2
    assert bundle.transition_unit(0, 1) != bundle.transition_unit(0, 1).parent().one()


def test_projective_line_bundle_tensor_dual_and_canonical_degrees_are_exact() -> None:
    r"""On ``P^2``: ``O(1)^2 = O(2)``, ``O(1)^dual = O(-1)``, ``K = O(-3)``, ``-K = O(3)``."""
    plane = ProjectiveSpaces(QQ)(2)
    hyperplane = plane.O(1)
    dual = hyperplane.dual_sheaf()

    assert hyperplane.tensor_product(hyperplane).is_isomorphic(plane.O(2))
    assert hyperplane.tensor_power(2).degree() == 2
    assert dual.is_isomorphic(plane.O(-1))
    assert hyperplane.tensor_product(dual).degree() == 0
    assert not dual.is_ample()
    assert not dual.is_basepoint_free()
    assert plane.canonical_line_bundle().is_isomorphic(plane.O(-3))
    assert plane.anticanonical_line_bundle().degree() == 3


def test_multiplication_of_sections_is_multiplication_of_forms() -> None:
    r"""``H^0(O(1)) x H^0(O(1)) -> H^0(O(2))`` sends ``(x0, x1)`` to ``x0 x1`` on ``P^1``."""
    line = ProjectiveSpaces(QQ)(1, names=("x0", "x1"))
    ring = line.homogeneous_coordinate_ring()
    x0, x1 = ring("x0"), ring("x1")
    linear = line.O(1).global_sections()
    quadratic = line.O(2).global_sections()
    multiplication = line.O(1).section_multiplication(line.O(1))

    product = multiplication(
        linear.section_from_homogeneous_polynomial(x0),
        linear.section_from_homogeneous_polynomial(x1),
    )

    assert product == quadratic.section_from_homogeneous_polynomial(x0 * x1)
    assert product != quadratic.section_from_homogeneous_polynomial(x0**2)


def test_projection_pullback_places_degree_in_the_selected_product_factor() -> None:
    r"""``pr_1^* O(2) = O(2, 0)`` on ``P^1 x P^1``; pullback of sections is injective of rank 3.

    ``h^0(O(2, 0)) = 3 * 1`` by Kuenneth, so the pullback is an isomorphism on sections.
    """
    line = ProjectiveSpaces(QQ)(1)
    product = line * line
    projection = product.left_projection()
    bundle = line.O(2)

    pulled = bundle.pullback(projection)
    section_pullback = bundle.global_sections().pullback(projection)

    assert pulled.is_isomorphic(product.O(2, 0))
    assert section_pullback.is_injective()
    assert section_pullback.domain().module_rank() == 3
    assert section_pullback.codomain().module_rank() == 3
