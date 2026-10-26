r"""Subobject Mor objects are the canonical factor maps between inclusions."""

from sage_extensions.all import *  # noqa: F401,F403


def test_singleton_factors_through_a_larger_subset() -> None:
    three = Sets.Δ[2]
    subobjects = Sets().Subobjects(three)
    singleton = three.power_set()((three(0),))
    pair = three.power_set()((three(0), three(1)))
    morphisms = subobjects.Mor(singleton, pair)
    factor = morphisms(singleton.inclusion().factor_through(pair.inclusion()))

    assert factor.parent() is morphisms
    assert factor.domain() is singleton
    assert factor.codomain() is pair
    assert factor.left().domain() is singleton.underlying_set()
    assert pair.inclusion() * factor.left() == singleton.inclusion()


def test_subobject_identity_has_identity_factor() -> None:
    three = Sets.Δ[2]
    singleton = three.power_set()((three(0),))
    morphisms = Sets().Subobjects(three).Mor(singleton, singleton)
    identity = morphisms.identity()

    assert identity.domain() is singleton
    assert identity.codomain() is singleton
    assert identity.left() == Sets().Mor(
        singleton.underlying_set(),
        singleton.underlying_set(),
    ).identity()
