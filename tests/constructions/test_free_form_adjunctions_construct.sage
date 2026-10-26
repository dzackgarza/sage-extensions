r"""Free bilinear and quadratic forms are left adjoint to forgetting the form."""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_bilinear_form_adjunction_has_the_expected_categories() -> None:
    modules = Modules(ZZ).FinitelyPresented()
    adjunction = Modules(ZZ).bilinear_free_form_adjunction()
    line = ZZ.free_module(1)
    formed = adjunction.left_adjoint()(line)

    assert adjunction.left_adjoint().domain() is modules
    assert adjunction.right_adjoint().codomain() is modules
    assert formed in BilinearFormModules(ZZ).FinitelyPresented()
    assert adjunction.right_adjoint()(formed) is formed


def test_free_quadratic_form_adjunction_has_the_expected_categories() -> None:
    modules = Modules(ZZ).FinitelyPresented()
    adjunction = Modules(ZZ).quadratic_free_form_adjunction()
    line = ZZ.free_module(1)
    formed = adjunction.left_adjoint()(line)

    assert adjunction.left_adjoint().domain() is modules
    assert adjunction.right_adjoint().codomain() is modules
    assert formed in QuadraticFormModules(ZZ).FinitelyPresented()
    assert adjunction.right_adjoint()(formed) is formed
