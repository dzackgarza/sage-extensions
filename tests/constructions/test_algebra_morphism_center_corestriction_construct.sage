r"""An algebra map with central image factors through the codomain centre."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_map_to_even_exterior_element_corestricts_to_the_center() -> None:
    exterior = ZZ.free_module(("e1", "e2")).exterior_algebra()
    e1 = exterior.algebra_generator("e1")
    e2 = exterior.algebra_generator("e2")
    source = ZZ.polynomial_ring("t")
    t = source.algebra_generator("t")
    morphism = source.Mor(exterior)({"t": e1 * e2})
    factor = morphism.corestrict_to_center()
    center = exterior.ring_center()
    inclusion = center.inclusion()

    assert factor.domain() is source
    assert factor.codomain() is center
    assert inclusion(factor(t)) == morphism(t)
    assert inclusion(factor(source.one() + t)) == morphism(source.one() + t)
    assert factor(t * t) == center.zero()
