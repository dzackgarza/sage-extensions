import pytest

from sage_extensions.all import *


def test_poincare_duality_on_zz2_sends_e_to_f_dual_and_f_to_minus_e_dual() -> None:
    r"""For the volume ``e ^ f -> 1``, Poincare duality ``x -> (y -> vol(x ^ y))``
    sends ``e`` to ``f^*`` and ``f`` to ``-e^*``, since ``f ^ e = -e ^ f``.
    """
    module = Modules(ZZ)(2)
    e, f = module.module_generators()
    dual = module.dual_module()
    e_dual, f_dual = dual.module_generators()
    pd = module.poincare_duality(module.framing_volume_trivialization(), 1)

    assert pd(e) == f_dual
    assert pd(f) == -e_dual
    assert pd.inverse()(f_dual) == e


def test_hodge_star_is_the_metric_poincare_composite_and_has_expected_square() -> None:
    euclidean = Lattices(ZZ)(2)
    volume = euclidean.framing_volume_trivialization()
    star = euclidean.hodge_star(volume, 1)
    forms = euclidean.exterior_forms(1)
    first = forms.module_generator(next(iter(forms.module_generating_set())))
    square = euclidean.hodge_star(volume, 1).forward() * star.forward()

    assert star.domain() is forms
    assert star.codomain() is forms
    assert euclidean.hodge_discriminant(volume) == 1
    assert square(first) == -first

    hyperbolic = Lattices(ZZ)("U")
    hyperbolic_volume = hyperbolic.framing_volume_trivialization()
    hyperbolic_star = hyperbolic.hodge_star(hyperbolic_volume, 1)
    hyperbolic_forms = hyperbolic.exterior_forms(1)
    generator = hyperbolic_forms.module_generator(
        next(iter(hyperbolic_forms.module_generating_set()))
    )
    assert hyperbolic.hodge_discriminant(hyperbolic_volume) == -1
    assert (hyperbolic_star.forward() * hyperbolic_star.forward())(generator) == generator


def test_nonunimodular_metric_does_not_invent_an_integral_form_hodge_star() -> None:
    lattice = Lattices(ZZ)("A2")
    volume = lattice.framing_volume_trivialization()

    assert lattice.is_nondegenerate()
    assert not lattice.is_unimodular()
    with pytest.raises(ValueError):
        lattice.hodge_star(volume, 1)

    vector_star = lattice.multivector_hodge_star(volume, 1)
    generator = vector_star.domain().module_generator(
        next(iter(vector_star.domain().module_generating_set()))
    )
    assert (vector_star * vector_star)(generator) == -3 * generator

    rational_star = lattice.hodge_star_over_fraction_field(volume, 1)
    assert rational_star.domain().base_ring() is QQ
    rational_generator = rational_star.domain().module_generator(
        next(iter(rational_star.domain().module_generating_set()))
    )
    assert (rational_star.forward() * rational_star.forward())(
        rational_generator
    ) == QQ(-1) / 3 * rational_generator
    assert lattice.hodge_star_over_fraction_field(volume, 1).domain().base_ring() is QQ
