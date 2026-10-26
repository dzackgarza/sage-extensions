r"""Finite quadratic-form modules lie in the finitely-presented refinement."""

from sage_extensions.all import *  # noqa: F401,F403


def test_binary_quadratic_form_lies_in_the_finitely_presented_refinement() -> None:
    form = ZZ.free_module(2).equip_quadratic_form(ZZ, [[1, 1], [0, 1]])
    category = QuadraticFormModules(ZZ).FinitelyPresented()

    assert form in category
    assert form.is_finitely_presented()
    assert form.q(form.module_generator(0)) == 1
