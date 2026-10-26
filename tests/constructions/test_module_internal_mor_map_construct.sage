r"""Identity maps induce the identity on a represented internal Hom module."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_pre_and_postcomposition_fix_internal_hom() -> None:
    source = ZZ.free_module(2)
    target = ZZ.free_module(1)
    source_identity = source.Mor(source).identity()
    target_identity = target.Mor(target).identity()
    homs = source.Mor(target)
    induced = source_identity.internal_mor_map(target_identity)

    assert induced.domain() is homs
    assert induced.codomain() is homs
    assert induced(homs.zero()) == homs.zero()
    assert induced == homs.module_category().Mor(homs, homs).identity()
