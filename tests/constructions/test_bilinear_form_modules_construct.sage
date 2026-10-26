r"""Bilinear-form modules retain their quadratic specialization and correlation.

On ``ZZ^2`` with Gram matrix ``[[2,1],[1,2]]``, the associated quadratic value
is ``q(e_0)=2`` and the correlation ``b^flat`` sends ``e_0`` to the functional
whose value on ``e_1`` is one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_bilinear_module():
    module = ZZ.free_module(2)
    return FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[2, 1], [1, 2]]))


def test_bilinear_module_exposes_q_and_the_algebraic_correlation() -> None:
    form = _a2_bilinear_module()
    e0, e1 = form.module_generator(0), form.module_generator(1)
    correlation = form.algebraic_correlation_morphism()

    assert form in BilinearFormModules(ZZ)
    assert form.q(e0) == ZZ(2)
    assert correlation.domain() is form
    assert correlation.codomain() == form.dual_module()
    assert correlation(e0)(e1) == ZZ.one()
    assert isinstance(e0, form.ElementType)


def test_bilinear_form_module_morphisms_have_identity() -> None:
    form = _a2_bilinear_module()
    identity = form.Mor(form).identity()

    assert identity(form.module_generator(0)) == form.module_generator(0)
    assert identity * identity == identity
