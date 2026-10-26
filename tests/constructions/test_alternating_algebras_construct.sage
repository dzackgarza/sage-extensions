r"""Exterior algebras realize the alternating algebra on a module."""

from sage_extensions.all import *  # noqa: F401,F403


def test_exterior_algebra_has_the_expected_rank_two_wedge_relations() -> None:
    module = QQ.free_module(2)
    exterior = module.exterior_algebra()
    e0 = exterior.algebra_generator(0)
    e1 = exterior.algebra_generator(1)

    assert exterior in AlternatingAlgebras(QQ)
    assert e0 * e0 == exterior.zero()
    assert e1 * e1 == exterior.zero()
    assert e0 * e1 == -(e1 * e0)
    assert exterior.graded_piece(2).module_rank() == 1


def test_alternating_algebra_morphisms_have_identity() -> None:
    exterior = QQ.free_module(2).exterior_algebra()
    identity = exterior.Mor(exterior).identity()

    assert identity(exterior.algebra_generator(0)) == exterior.algebra_generator(0)
    assert identity * identity == identity

