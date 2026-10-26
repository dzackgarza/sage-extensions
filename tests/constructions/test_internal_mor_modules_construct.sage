r"""Internal Hom modules retain their presentation inside generator maps.

For ``Hom_ZZ(ZZ^2,ZZ)``, a linear map is determined by the images of the two
source generators.  The canonical presentation therefore includes the Hom
module into a rank-two module of generator images.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _hom_from_plane_to_line():
    source = ZZ.free_module(2)
    target = ZZ.free_module(1)
    return source, target, source.Mor(target)


def test_internal_hom_includes_into_the_module_of_generator_maps() -> None:
    source, target, homs = _hom_from_plane_to_line()
    inclusion = homs.inclusion_into_generator_maps()

    assert homs in InternalMorModules(ZZ)
    assert homs in LinearMorModules(ZZ)
    assert homs.source_module() is source
    assert homs.target_module() is target
    assert inclusion.domain() is homs
    assert inclusion.codomain().module_rank() == 2
    assert inclusion.is_injective()
    assert inclusion(homs.zero()) == inclusion.codomain().zero()
    assert isinstance(homs.zero(), homs.ElementType)


def test_internal_hom_module_morphisms_have_identity() -> None:
    _source, _target, homs = _hom_from_plane_to_line()
    identity = Modules(ZZ).Mor(homs, homs).identity()

    assert identity(homs.zero()) == homs.zero()
    assert identity * identity == identity
