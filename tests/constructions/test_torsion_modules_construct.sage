r"""Torsion modules are exactly modules with zero generic fibre."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_six_is_a_torsion_module_and_free_integer_line_is_not() -> None:
    torsion = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((6,))
    free = ZZ.free_module(1)

    assert torsion in TorsionModules(ZZ)
    assert torsion.is_torsion()
    assert free not in TorsionModules(ZZ)
    assert not free.is_torsion()
