r"""The finitely-presented refinement records finite generators and relations."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_six_lies_in_the_finitely_presented_refinement() -> None:
    line = ZZ.free_module(1)
    module = line.End()({0: 6 * line.module_generator(0)}).cokernel()
    category = Modules(ZZ).FinitelyPresented()

    assert module in category
    assert module.is_finitely_presented()
    assert module.projective_dimension() == 1
