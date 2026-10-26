r"""A quadratic-form morphism exposes its classifier, bilinear lift, and polarization."""

from sage_extensions.all import *  # noqa: F401,F403


def _binary_quadratic_morphism():
    module = ZZ.free_module(2)
    quadratic = module.equip_quadratic_form(ZZ, [[1, 1], [0, 1]])
    return module, quadratic.form()


def test_quadratic_form_morphism_retains_module_and_classifier() -> None:
    module, morphism = _binary_quadratic_morphism()

    assert morphism.module() is module
    assert morphism.classifying_morphism() is morphism
    assert morphism.has_selected_bilinear_lift()


def test_quadratic_form_morphism_retains_selected_bilinear_lift() -> None:
    module, morphism = _binary_quadratic_morphism()
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)

    assert morphism.lift_pairing(e0, e0) == ZZ.one()
    assert morphism.lift_pairing(e0, e1) == ZZ.one()
    assert morphism.b(e0, e1) == ZZ.one()


def test_quadratic_form_morphism_exposes_polar_form_and_gram_tensor() -> None:
    module, morphism = _binary_quadratic_morphism()
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)
    polar = morphism.polar_form()
    gram = morphism.gram_tensor()

    assert polar(e0, e1) == ZZ.one()
    assert gram[0, 0] == ZZ.one()
    assert gram[0, 1] == ZZ.one()
