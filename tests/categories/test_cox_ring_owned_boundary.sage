r"""The Cox ring of the projective plane."""

from sage_extensions.all import *  # noqa: F401,F403


def test_cox_ring_of_the_projective_plane_is_a_polynomial_ring_graded_by_zz() -> None:
    r"""For ``P^2`` with fan rays ``e1, e2, -e1 - e2``: ``Cl(P^2) ≅ ZZ^3 / ZZ^2 = ZZ``,
    the Cox ring is ``QQ[x0, x1, x2]`` with every variable of degree ``[H] = 1``,
    and its degree-``d`` piece is ``H^0(O(d))`` of dimension ``binom(d + 2, 2)``:
    3 for ``d = 1``, 6 for ``d = 2``."""
    plane = ProjectiveSpaces(QQ)(2)
    cox = plane.cox_ring()
    class_group = plane.class_group()

    assert class_group.module_rank() == 1
    assert class_group.invariant_factors().cardinality() == 0
    assert cox.algebra_generators().cardinality() == 3
    assert cox.graded_piece(class_group.module_generator(0)).module_rank() == 3
    assert cox.graded_piece(2 * class_group.module_generator(0)).module_rank() == 6
