r"""Coxeter edge weights distinguish intersecting, parallel, and divergent mirrors."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_edge_weight_is_the_simple_bond_weight() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])
    left, right = tuple(diagram.vertices())

    assert diagram.edge_weight(left, right) == 1
    assert not diagram.mirrors_are_parallel(left, right)
    assert not diagram.mirrors_are_divergent(left, right)


def test_affine_a1_mirrors_are_parallel() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 1, 1])
    left, right = tuple(diagram.vertices())

    assert diagram.mirrors_are_parallel(left, right)
    assert not diagram.mirrors_are_divergent(left, right)
