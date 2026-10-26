r"""A degreewise linear map exposes the finite module-map realization when framed."""

from sage_extensions.all import *  # noqa: F401,F403


def _degreewise_identity():
    module = ZZ.free_module(2)
    morphism = DegreewiseLinearMorphism(module, module, lambda element: element)
    return module, morphism


def test_degreewise_linear_identity_has_the_expected_action() -> None:
    module, morphism = _degreewise_identity()
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)

    assert morphism.domain() is module
    assert morphism.codomain() is module
    assert morphism(e0 + 2 * e1) == e0 + 2 * e1


def test_degreewise_linear_identity_exposes_its_module_morphism() -> None:
    module, morphism = _degreewise_identity()
    represented = morphism.represented_module_morphism()
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)

    assert represented.domain() is module
    assert represented.codomain() is module
    assert represented(e0 + e1) == e0 + e1


def test_degreewise_linear_identity_has_zero_kernel_and_full_image() -> None:
    module, morphism = _degreewise_identity()

    assert morphism.kernel().module_rank() == cardinal(0)
    assert morphism.image().module_rank() == module.module_rank()
