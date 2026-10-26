r"""Jets of sections of ``O(d)`` at a rational point of the projective plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_first_order_jets_of_conics_at_a_noncoordinate_point() -> None:
    r"""``O/m^2`` at ``(1:2:3)`` has dimension 3; conics with a double point there form a 3-dimensional space.

    Vanishing to order 2 imposes ``1 + 2 = 3`` independent conditions on the
    6-dimensional ``H^0(P^2, O(2))``.
    """
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(2)
    point = plane.point_morphism((1, 2, 3))

    evaluation = bundle.jet_evaluation(point, 2)

    assert evaluation.codomain().dimension() == 3
    assert evaluation.kernel().dimension() == 3
    assert evaluation.cokernel().dimension() == 0


def test_double_point_condition_is_nonreduced_and_stronger_than_value_evaluation() -> None:
    r"""Values at a point form a 1-dimensional space, first-order jets a 3-dimensional one."""
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(2)
    point = plane.point_morphism((1, 2, 3))

    values = bundle.jet_evaluation(point, 1)
    doubles = bundle.jet_evaluation(point, 2)

    assert values.codomain().dimension() == 1
    assert values.kernel().dimension() == 5
    assert doubles.codomain().dimension() == 3
    assert doubles.kernel().dimension() < values.kernel().dimension()


def test_plane_cubics_singular_at_a_point_form_a_seven_dimensional_space() -> None:
    r"""``h^0(O(3)) = 10``; singularity at ``(1:2:3)`` imposes 3 conditions, leaving 7.

    The linear system of such cubics has projective dimension 6.
    """
    plane = ProjectiveSpaces(QQ)(2)
    point = plane.point_morphism((1, 2, 3))
    cubics = plane.O(3)

    singular = cubics.jet_evaluation(point, 2).kernel()

    assert cubics.global_sections().dimension() == 10
    assert singular.dimension() == 7
