r"""Finitely presented modules expose projective dimension, Tor, and Ext.

Over ``ZZ``, ``ZZ/6`` has projective dimension one,
``Tor_1(ZZ/6,ZZ/4)=ZZ/2``, and ``Ext^1(ZZ/6,ZZ)=ZZ/6``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _cyclic(order):
    line = ZZ.free_module(1)
    relations = ZZ.free_module(1)
    return relations.Mor(line)({0: order * line.module_generator(0)}).cokernel()


def test_z_mod_six_is_finitely_presented_of_projective_dimension_one() -> None:
    six = _cyclic(6)

    assert six in FinitelyPresentedModules(ZZ)
    assert six.is_finitely_presented()
    assert six.projective_dimension() == 1


def test_finitely_presented_cyclic_modules_have_the_standard_tor_and_ext() -> None:
    six = _cyclic(6)
    four = _cyclic(4)

    assert six.tor(four, degree=1).cardinality() == 2
    assert six.ext(ZZ.regular_module(), degree=1).cardinality() == 6
