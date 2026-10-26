r"""Free formed modules combine a free framing with a scalar-valued form.

The rank-two form with Gram matrix ``[[2,1],[1,2]]`` has determinant three: it
is nondegenerate over ``ZZ`` but not unimodular.  Its correlation, formed
subobjects, and scalar extension are all determined by the same selected form.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_free_form():
    module = ZZ.free_module(2)
    return FormModules(ZZ)(module.bilinear_hom_space(ZZ)([[2, 1], [1, 2]]))


def test_free_form_module_exposes_correlation_and_nondegeneracy() -> None:
    form = _a2_free_form()
    correlation = form.correlation_morphism()

    assert form in FreeFormModules(ZZ)
    assert form.is_nondegenerate()
    assert not form.is_unimodular()
    assert correlation.domain() is form
    assert correlation.codomain() == form.dual_module()
    assert isinstance(form.module_generator(0), form.ElementType)


def test_free_form_subobject_retains_the_restricted_form() -> None:
    form = _a2_free_form()
    root = form.module_generator(0)
    line = form.subobject_on((root,))

    assert line.module_rank() == 1
    assert line.inclusion().codomain() is form
    assert line.b(line.module_generator(0), line.module_generator(0)) == ZZ(2)


def test_free_form_base_change_preserves_rank_and_gram_values() -> None:
    form = _a2_free_form()
    inclusion = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    changed = form.base_change(inclusion)

    assert changed in FreeFormModules(QQ)
    assert changed.module_rank() == 2
    assert changed.b(changed.module_generator(0), changed.module_generator(1)) == QQ.one()


def test_free_form_module_morphisms_have_identity() -> None:
    form = _a2_free_form()
    identity = form.Mor(form).identity()

    assert identity(form.module_generator(0)) == form.module_generator(0)
    assert identity * identity == identity
