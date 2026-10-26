r"""A chosen volume trivialization on (mathbf Z^2) induces the standard degree-one Poincaré duality."""

from sage_extensions.all import *  # noqa: F401,F403


def test_explicit_volume_trivialization_recovers_the_framing_volume() -> None:
    module = ZZ.free_module(2)
    framing = module.framing_volume_trivialization()
    volume = module.volume_trivialization(
        framing.forward(),
        framing.inverse(),
    )

    assert volume.forward() == framing.forward()
    assert volume.inverse() == framing.inverse()


def test_poincare_duality_on_integer_plane_has_standard_signs() -> None:
    module = ZZ.free_module(2)
    e, f = module.module_generators()
    dual = module.dual_module()
    e_dual, f_dual = dual.module_generators()
    framing = module.framing_volume_trivialization()
    volume = module.volume_trivialization(
        framing.forward(),
        framing.inverse(),
    )
    duality = module.poincare_duality(volume, 1)

    assert duality(e) == f_dual
    assert duality(f) == -e_dual
    assert duality.inverse()(f_dual) == e
