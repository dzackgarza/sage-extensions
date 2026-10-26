r"""Fibrewise formed morphisms also retain the coefficient-ring map.

Over the identity of ``ZZ``, the identity linear map of the hyperbolic plane and
the identity on its value module define the identity fibrewise formed morphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_fibered_formed_identity_has_fixed_endpoints_and_form_compatibility() -> None:
    form = NamedLattices.U
    module = form.unformed_module()
    values = form.value_module()
    fibered = form.fibered_formed_mor(
        form,
        ZZ.Mor(ZZ).identity(),
        Modules(ZZ).Mor(module, module).identity(),
        values.Mor(values).identity(),
    )
    hom = fibered.parent()

    assert hom in Cat()
    assert hom.domain_object() is form
    assert hom.codomain_object() is form
    assert fibered.domain() is form
    assert fibered.codomain() is form
    assert fibered.preserves_form_exactly()
    assert hom.identity() * fibered == fibered
