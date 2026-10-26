r"""A semilinear map exposes its adjoint scalar-extended linearization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_two_semilinear_map_linearizes_over_the_target_ring() -> None:
    source = ZZ.free_module(2)
    target = QQ.free_module(2)
    w0, w1 = target.module_generator(0), target.module_generator(1)
    hom = ModulesOverCommutativeRings().Mor(source, target)
    scalar_map = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    semilinear = hom(
        scalar_map,
        hom.compatible_mor(scalar_map)({0: w0, 1: 2 * w1}),
    )
    linear = semilinear.linearization()
    extended = semilinear.extended_source()

    assert linear.domain() is extended
    assert linear.codomain() is target
    assert extended.base_ring() is QQ
    assert linear(extended.module_generator(0)) == w0
    assert linear(extended.module_generator(1)) == 2 * w1
