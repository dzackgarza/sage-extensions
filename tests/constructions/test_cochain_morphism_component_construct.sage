r"""The identity cochain morphism has identity components in every degree."""

from sage_extensions.all import *  # noqa: F401,F403


def _coordinate_inclusion_complex():
    source = ZZ.free_module(1)
    target = ZZ.free_module(2)
    differential = source.Mor(target)({0: target.module_generator(0)})
    complex_ = CochainComplexes(ZZ)({0: source, 1: target}, {0: differential})
    return source, target, complex_


def test_identity_cochain_morphism_components_are_degreewise_identities() -> None:
    source, target, complex_ = _coordinate_inclusion_complex()
    identity = complex_.Mor(complex_).identity()

    assert identity.component(0) == source.Mor(source).identity()
    assert identity.component(1) == target.Mor(target).identity()
