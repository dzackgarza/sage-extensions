r"""A Cox monomial has the divisor-class degree of its toric divisor sum."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_cox_monomial_has_sum_of_generator_degrees() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cox = plane.cox_ring()
    labels = tuple(cox.algebra_generating_set())
    first = cox.algebra_generator(labels[0])
    second = cox.algebra_generator(labels[1])

    assert cox.homogeneous_degree(first * second) == (
        cox.generator_degree(labels[0]) + cox.generator_degree(labels[1])
    )
