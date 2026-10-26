r"""The quadratic/norm value belongs to formed modules, above either form type."""

from sage_extensions.all import *  # noqa: F401,F403


def test_q_is_available_on_a_bilinear_form_outside_quadratic_forms() -> None:
    module = ZZ.free_module(2)
    formed = FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[0, 1], [1, 0]]))
    generator = formed.module_generator(0)

    assert formed in FormModules(ZZ)
    assert formed in BilinearFormModules(ZZ)
    assert formed not in QuadraticFormModules(ZZ)
    assert formed.q(generator) == formed.norm(generator)


def test_q_is_available_on_a_quadratic_form_outside_bilinear_forms() -> None:
    formed = ZZ.free_module(2).equip_quadratic_form(
        ZZ,
        [[1, 1], [0, 1]],
    )
    generator = formed.module_generator(0)

    assert formed in FormModules(ZZ)
    assert formed in QuadraticFormModules(ZZ)
    assert formed not in BilinearFormModules(ZZ)
    assert formed.q(generator) == formed.norm(generator)
