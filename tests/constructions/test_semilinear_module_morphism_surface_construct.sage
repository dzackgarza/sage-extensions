r"""A semilinear module map exposes its equivalent linear and additive views."""

from sage_extensions.all import *  # noqa: F401,F403


def _rank_two_semilinear_map():
    source = ZZ.free_module(2)
    target = QQ.free_module(2)
    w0, w1 = target.module_generator(0), target.module_generator(1)
    hom = ModulesOverCommutativeRings().Mor(source, target)
    scalar_map = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    semilinear = hom(
        scalar_map,
        hom.compatible_mor(scalar_map)({0: w0, 1: 2 * w1}),
    )
    return source, target, w0, w1, scalar_map, semilinear


def test_semilinear_map_retains_endpoints_and_restricted_linear_map() -> None:
    source, target, w0, _w1, _scalar_map, semilinear = (
        _rank_two_semilinear_map()
    )
    e0 = source.module_generator(0)
    restricted = semilinear.restricted_codomain()
    linear = semilinear.restricted_morphism()

    assert semilinear.source() is source
    assert semilinear.target() is target
    assert restricted.base_ring() is ZZ
    assert linear.domain() is source
    assert linear.codomain() is restricted
    assert linear(e0).underlying_element() == w0


def test_semilinear_map_exposes_underlying_additive_map_and_extended_source() -> None:
    source, target, _w0, w1, _scalar_map, semilinear = (
        _rank_two_semilinear_map()
    )
    e1 = source.module_generator(1)
    additive = semilinear.additive_map()
    extended = semilinear.extended_source()

    assert additive.domain() is source
    assert additive.codomain() is target
    assert additive(e1) == 2 * w1
    assert extended.base_ring() is QQ
    assert extended.module_rank() == source.module_rank()


def test_linear_map_embeds_as_semilinear_over_the_identity_ring_map() -> None:
    module = ZZ.free_module(1)
    linear_identity = Modules(ZZ).Mor(module, module).identity()
    semilinear = SemilinearModuleMorphism.from_linear(linear_identity)
    generator = module.module_generator(0)

    assert semilinear.scalar_map() == ZZ.Mor(ZZ).identity()
    assert semilinear(generator) == generator
    assert SemilinearModuleMorphism.identity(module)(generator) == generator
