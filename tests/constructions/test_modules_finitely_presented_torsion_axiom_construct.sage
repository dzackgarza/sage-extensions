r"""Finite presented torsion modules refine both finite presentation and torsion."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_six_lies_in_the_finitely_presented_torsion_refinement() -> None:
    line = ZZ.free_module(1)
    module = line.End()({0: 6 * line.module_generator(0)}).cokernel()
    category = Modules(ZZ).FinitelyPresented().Torsion()

    assert module in category
    assert module.is_finitely_presented()
    assert module.is_torsion()
