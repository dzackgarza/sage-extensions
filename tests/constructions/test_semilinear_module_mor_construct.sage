r"""Semilinear Mor categories contain maps over varying scalar morphisms.

Along ``ZZ -> QQ``, sending the standard basis of ``ZZ^2`` to ``w_0,2w_1`` in
``QQ^2`` is semilinear; composing with the target identity changes nothing.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_semilinear_mor_retains_endpoints_scalar_map_and_composition() -> None:
    source = ZZ.free_module(2)
    target = QQ.free_module(2)
    e0, e1 = source.module_generator(0), source.module_generator(1)
    w0, w1 = target.module_generator(0), target.module_generator(1)
    hom = ModulesOverCommutativeRings().Mor(source, target)
    scalar_map = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    semilinear = hom(
        scalar_map,
        hom.compatible_mor(scalar_map)({0: w0, 1: 2 * w1}),
    )

    assert hom in Cat()
    assert hom.domain_object() is source
    assert hom.codomain_object() is target
    assert semilinear.scalar_map() is scalar_map
    assert semilinear(e0 - e1) == w0 - 2 * w1
    assert ModulesOverCommutativeRings().Mor(target, target).identity() * semilinear == semilinear
