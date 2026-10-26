r"""The centre of the exterior algebra on ``QQ^2`` and maps factoring through it."""

from sage_extensions.all import *  # noqa: F401,F403


def _exterior_plane():
    exterior = Modules(QQ).free_module(("e1", "e2")).exterior_algebra()
    return exterior, exterior.algebra_generator("e1"), exterior.algebra_generator("e2")


def test_center_of_the_exterior_algebra_of_the_plane_contains_e1e2_but_not_e1() -> None:
    r"""``Z(Λ(QQ^2)) = QQ ⊕ QQ e1e2``: ``e1 (e1e2) = 0 = (e1e2) e1``, while
    ``e1 e2 = -e2 e1 ≠ e2 e1``.  Derivation by the sign rule of Λ."""
    exterior, e1, e2 = _exterior_plane()
    center = exterior.ring_center()

    assert e1 * e2 in center
    assert exterior.one() + e1 * e2 in center
    assert e1 not in center
    assert e1 + e2 not in center


def test_the_map_t_to_e1e2_factors_through_the_center() -> None:
    r"""``QQ[t] -> Λ(QQ^2)``, ``t ↦ e1e2`` corestricts to the centre, and the
    corestriction followed by the inclusion is the original map; ``t^2 ↦ 0``."""
    exterior, e1, e2 = _exterior_plane()
    source = QQ["t"]
    t = source.gen()
    morphism = source.Mor(exterior)({t: e1 * e2})
    factor = morphism.corestrict_to_center()
    inclusion = exterior.ring_center().inclusion()

    assert inclusion(factor(t)) == e1 * e2
    assert inclusion(factor(1 + t)) == exterior.one() + e1 * e2
    assert factor(t**2) == factor(t).parent().zero()
