r"""Line bundles ``O(a, b)`` on ``P^1 x P^1``."""

from sage_extensions.all import *  # noqa: F401,F403


def quadric():
    r"""``P^1 x P^1`` over ``Q``."""
    line = ProjectiveSpaces(QQ)(1)
    return line * line


def test_O_1_2_on_P1_x_P1_has_six_sections_and_is_very_positive() -> None:
    r"""``h^0(O(a, b)) = (a + 1)(b + 1)`` for ``a, b >= 0`` (Kuenneth); ``O(1, 2)`` is ample and basepoint free.

    ``O(a, b)`` with ``a, b > 0`` is very ample through the Segre--Veronese
    embedding; ``O(1, 0)`` is trivial on the fibres ``{p} x P^1``, so not ample.
    """
    surface = quadric()
    bundle = surface.O(1, 2)

    assert bundle.global_sections().module_rank() == 6
    assert surface.O(2, 2).global_sections().module_rank() == 9
    assert bundle.is_ample()
    assert bundle.is_basepoint_free()
    assert not surface.O(1, 0).is_ample()
    assert surface.O(1, 0).is_basepoint_free()


def test_multiprojective_tensor_dual_and_canonical_degrees_are_componentwise() -> None:
    r"""On ``P^1 x P^1``: ``O(1,2) (x) O(2,1) = O(3,3)``, ``O(1,2)^dual = O(-1,-2)``, ``K = O(-2,-2)``."""
    surface = quadric()
    bundle = surface.O(1, 2)

    assert bundle.tensor_product(surface.O(2, 1)).is_isomorphic(surface.O(3, 3))
    assert bundle.dual_sheaf().is_isomorphic(surface.O(-1, -2))
    assert surface.canonical_line_bundle().is_isomorphic(surface.O(-2, -2))
    assert surface.anticanonical_line_bundle().is_isomorphic(surface.O(2, 2))
    assert not surface.O(1, 2).is_isomorphic(surface.O(2, 1))


def test_multiplication_of_sections_of_O_1_0_and_O_0_1_is_the_segre_isomorphism() -> None:
    r"""``H^0(O(1,0)) (x) H^0(O(0,1)) -> H^0(O(1,1))`` is an isomorphism, ``2 * 2 = 4``.

    Its image is spanned by the four products ``x_i y_j``, a basis of the
    bihomogeneous forms of bidegree ``(1, 1)``.
    """
    surface = quadric()
    left = surface.O(1, 0)
    right = surface.O(0, 1)
    multiplication = left.section_multiplication(right)
    products = tuple(
        multiplication(s, t)
        for s in left.global_sections().basis()
        for t in right.global_sections().basis()
    )

    assert surface.O(1, 1).global_sections().module_rank() == 4
    assert multiplication.codomain().span(products).inclusion().index() == 1
