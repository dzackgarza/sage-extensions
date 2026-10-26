r"""The torsion module refinement consists of modules with zero generic fibre."""

from sage_extensions.all import *  # noqa: F401,F403


def _z_mod_six():
    line = ZZ.free_module(1)
    return line.End()({0: 6 * line.module_generator(0)}).cokernel()


def test_z_mod_six_lies_in_the_torsion_refinement() -> None:
    module = _z_mod_six()
    category = Modules(ZZ).Torsion()

    assert module in category
    assert module.is_torsion()
    assert module.generic_rank() == 0
