r"""Finite-rank free modules lie in the finitely-generated framed-free refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integer_plane_lies_in_the_finitely_generated_framed_free_refinement() -> None:
    module = ZZ.free_module(2)
    category = FramedFreeModules(ZZ).FinitelyGenerated()

    assert module in category
    assert module.module_rank() == 2
    assert module.module_generators().cardinality() == 2
