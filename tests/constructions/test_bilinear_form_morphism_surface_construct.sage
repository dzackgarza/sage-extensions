r"""A bilinear-form morphism retains its module data and standard form operations."""

from sage_extensions.all import *  # noqa: F401,F403


def _hyperbolic_bilinear_morphism():
    module = ZZ.free_module(2)
    form = FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[0, 1], [1, 0]]))
    return form, form.form()


def test_hyperbolic_bilinear_morphism_retains_its_modules() -> None:
    form, bilinear = _hyperbolic_bilinear_morphism()
    module = form.unformed_module()

    assert bilinear.left_module() is module
    assert bilinear.right_module() is module
    assert bilinear.module() is module


def test_hyperbolic_bilinear_morphism_norm_and_polar_form_have_standard_values() -> None:
    form, bilinear = _hyperbolic_bilinear_morphism()
    e, f = form.module_generator(0), form.module_generator(1)
    polar = bilinear.polar_form()

    assert bilinear.norm(e) == bilinear(e, e) == ZZ.zero()
    assert polar(e, f) == 2 * bilinear(e, f)


def test_hyperbolic_bilinear_morphism_pullback_along_identity_preserves_values() -> None:
    form, bilinear = _hyperbolic_bilinear_morphism()
    module = form.unformed_module()
    identity = Modules(ZZ).Mor(module, module).identity()
    pulled = bilinear.pullback(identity)
    e, f = form.module_generator(0), form.module_generator(1)

    assert pulled(e, f) == bilinear(e, f)
