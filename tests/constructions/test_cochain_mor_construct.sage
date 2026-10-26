r"""Cochain Mor categories contain chain maps between fixed complexes.

The identity chain map on a two-term cochain complex fixes every component and
is the identity object of its fixed-endpoint Mor category.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _two_term_complex():
    source = ZZ.free_module(1)
    target = ZZ.free_module(1)
    differential = source.Mor(target)({0: 2 * target.module_generator(0)})
    return CochainComplexes(ZZ)({0: source, 1: target}, {0: differential})


def test_cochain_mor_fixed_endpoints_and_identity() -> None:
    complex_ = _two_term_complex()
    hom = complex_.Mor(complex_)
    identity = hom.identity()

    assert hom in Cat()
    assert hom.domain_object() is complex_
    assert hom.codomain_object() is complex_
    assert identity.domain() is complex_
    assert identity.codomain() is complex_
    assert identity * identity == identity
