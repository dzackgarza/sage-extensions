r"""Symmetric bilinear forms expose metric duality and Hodge-star constructions.

The hyperbolic plane ``U`` is symmetric, even, and unimodular.  Its Hodge star
in degree one squares to the identity, its Hodge discriminant is ``-1``, and its
even pairing defines an integral quadratic module.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_has_correlation_isomorphism_and_integral_quadratic_refinement() -> None:
    form = NamedLattices.U
    correlation = form.correlation_isomorphism()
    quadratic = form.to_quadratic_module()

    assert form in SymmetricBilinearFormModules(ZZ)
    assert correlation.is_isomorphism()
    assert quadratic in QuadraticFormModules(ZZ)
    assert quadratic.q(quadratic.module_generator(0)) == ZZ.zero()


def test_hyperbolic_hodge_stars_have_the_expected_discriminant_and_square() -> None:
    form = NamedLattices.U
    volume = form.framing_volume_trivialization()
    star = form.hodge_star(volume, 1)
    rational = form.hodge_star_over_fraction_field(volume, 1)
    multivector = form.multivector_hodge_star(volume, 1)
    generator = star.domain().module_generator(next(iter(star.domain().module_generating_set())))

    assert form.hodge_discriminant(volume) == -1
    assert (star.forward() * star.forward())(generator) == generator
    assert rational.domain().base_ring() is QQ
    assert multivector.domain() == form.exterior_power(1)
