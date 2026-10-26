r"""Mor objects are sets of morphisms and recognize endomorphism sets."""

from sage_extensions.all import *  # noqa: F401,F403


def test_set_mor_objects_classify_endomorphism_sets() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    endomorphisms = Sets().Mor(two, two)
    arrows = Sets().Mor(two, three)

    assert endomorphisms in Sets().Mors()
    assert arrows in Sets().Mors()
    assert endomorphisms.is_endomorphism_set()
    assert not arrows.is_endomorphism_set()
