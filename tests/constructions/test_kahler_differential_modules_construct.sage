r"""Kähler differentials represent derivations and control tangent spaces.

For the node ``A=QQ[x,y]/(xy)``, the conormal relation is
``y dx + x dy``.  The cotangent space has dimension two at the origin and one
at a smooth point, so the nonsmooth locus is exactly the origin.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _axes_differentials():
    plane = QQ["x,y"]
    x, y = plane.algebra_generator("x"), plane.algebra_generator("y")
    axes = plane.quotient(plane.ideal(x * y))
    return axes, axes(x), axes(y), axes.kahler_differentials()


def test_kahler_module_retains_source_generators_and_universal_derivation() -> None:
    axes, x, y, omega = _axes_differentials()
    d = omega.universal_derivation()
    dx = omega.differential_generator("x")
    dy = omega.differential_generator("y")

    assert omega in KahlerDifferentialModules(axes)
    assert omega.source_algebra() is axes
    assert isinstance(dx, omega.ElementType)
    assert d(x) == dx
    assert d(y) == dy
    assert y * dx + x * dy == omega.zero()


def test_kahler_conormal_sequence_retains_relation_and_projection() -> None:
    axes, x, y, omega = _axes_differentials()
    conormal = omega.conormal_module()
    ambient = omega.ambient_differentials()
    conormal_map = omega.conormal_morphism()
    projection = omega.differential_projection()
    relation = conormal.module_generator(0)

    assert conormal_map.domain() is conormal
    assert conormal_map.codomain() is ambient
    assert conormal_map(relation) == y * ambient.module_generator(0) + x * ambient.module_generator(1)
    assert projection.domain() is ambient
    assert projection.codomain() is omega
    assert projection(conormal_map(relation)) == omega.zero()


def test_kahler_tangent_and_cotangent_spaces_detect_the_node() -> None:
    axes, x, y, omega = _axes_differentials()
    spectrum = axes.spectrum()
    origin = spectrum(axes.ideal(x, y))
    smooth = spectrum(axes.ideal(x - axes.one(), y))
    conormal_at_origin = omega.conormal_morphism_at(origin)

    assert omega.cotangent_space(origin).dimension() == 2
    assert omega.tangent_space(origin).dimension() == 2
    assert omega.tangent_dimension(origin) == 2
    assert omega.cotangent_space(smooth).dimension() == 1
    assert omega.tangent_dimension(smooth) == 1
    assert conormal_at_origin.domain().base_ring() is origin.residue_field()
    singular = omega.non_smooth_locus(1)
    assert origin in singular
    assert smooth not in singular


def test_kahler_derivation_classifiers_are_isomorphisms_and_factor_derivations() -> None:
    axes, x, y, omega = _axes_differentials()
    derivation = axes.derivations()({x: x, y: -y})
    classifier = omega.from_derivation(derivation)
    target = axes.regular_module()
    representing = omega.representing_isomorphism(target)
    derivation_iso = omega.derivation_classifier_isomorphism(target)

    assert representing.is_isomorphism()
    assert derivation_iso.is_isomorphism()
    assert classifier(omega.universal_derivation()(x + y)) == x - y

