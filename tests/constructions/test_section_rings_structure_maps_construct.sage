r"""Section rings expose their grading, multiplication, and homogeneous inclusions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_divisor_section_ring_generator_degrees() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    ring = plane.section_ring(plane.hyperplane_divisor())
    labels = tuple(ring.algebra_generating_set())

    assert ring.section_semigroup_generators().cardinality() == cardinal(3)
    assert all(ring.generator_degree(label) == 1 for label in labels)
    assert ring.homogeneous_degree(ring.algebra_generator(labels[0]) ** 2) == 2


def test_line_bundle_section_ring_multiplication_and_component_maps() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    bundle = plane.O(1)
    ring = bundle.section_ring()
    degree_one = ring.graded_piece(1)
    degree_two = ring.graded_piece(2)
    labels = tuple(degree_one.module_generating_set())
    first = degree_one.module_generator(labels[0])
    second = degree_one.module_generator(labels[1])
    product = ring.section_multiplication(1, 1)(first, second)
    included_first = ring.homogeneous_component_element(1, first)
    included_second = ring.homogeneous_component_element(1, second)

    assert ring.section_line_bundle() is bundle
    assert product in degree_two
    assert ring.homogeneous_component_map(1).domain() is degree_one
    assert ring.homogeneous_degree(included_first) == 1
    assert ring.homogeneous_degree(included_second) == 1
    assert ring.homogeneous_degree(included_first * included_second) == 2
