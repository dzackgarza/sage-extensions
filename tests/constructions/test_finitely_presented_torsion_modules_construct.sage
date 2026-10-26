r"""Finite presented torsion modules enumerate their elements and invariant factors.

The cyclic module ``ZZ/6`` has six elements, invariant factor ``6``, and zero
generic fibre.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _z_mod_six():
    line = ZZ.free_module(1)
    relations = ZZ.free_module(1)
    return relations.Mor(line)({0: 6 * line.module_generator(0)}).cokernel()


def test_z_mod_six_has_six_elements_one_invariant_factor_and_is_torsion() -> None:
    module = _z_mod_six()

    assert module in FinitelyPresentedTorsionModules(ZZ)
    assert module.is_torsion()
    assert module.elements().cardinality() == cardinal(6)
    assert tuple(module.invariants()) == (ZZ(6),)
