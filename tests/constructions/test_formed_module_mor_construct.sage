r"""Formed-module Mor categories contain the form-preserving maps at fixed scalars.

The identity isometry of the hyperbolic plane is the identity arrow of its
fixed-endpoint formed Mor category and preserves the form exactly.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_formed_module_mor_fixed_endpoints_and_identity() -> None:
    form = NamedLattices.U
    hom = form.Mor(form)
    identity = hom.identity()

    assert hom in Cat()
    assert hom.domain_object() is form
    assert hom.codomain_object() is form
    assert identity.domain() is form
    assert identity.codomain() is form
    assert identity.preserves_form_exactly()
    assert identity * identity == identity
