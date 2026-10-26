r"""Noetherian quotient/completion comparison through the canonical maps."""

from sage_extensions.all import *


def _nodal_plane_comparison(precision=6):
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    node = plane.quotient_ring(plane.ideal(x * y))
    comparison = node.completion_comparison(
        plane.ideal(x, y),
        precision=precision,
    )
    return plane, x, y, node, comparison


def test_complete_nodal_quotient_agrees_with_quotient_of_completion() -> None:
    plane, x, y, node, comparison = _nodal_plane_comparison()
    direct = comparison.completed_quotient()
    quotient_after = comparison.quotient_after_completion()
    source_completion = comparison.source_completion()
    node_map = node.quotient_map()
    direct_map = direct.completion_map()
    quotient_map = quotient_after.quotient_map()
    source_map = source_completion.completion_map()

    for generator in (x, y):
        left = comparison.forward()(direct_map(node_map(generator)))
        right = quotient_map(source_map(generator))
        assert left == right
        assert comparison.inverse()(right) == direct_map(node_map(generator))

    assert direct_map(node_map(x * y)) == direct.zero()
    assert quotient_map(source_map(x * y)) == quotient_after.zero()
