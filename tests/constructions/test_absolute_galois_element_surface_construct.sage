r"""The identity of the absolute Galois group is a globally evaluable exact field automorphism."""

from sage_extensions.all import *  # noqa: F401,F403


def test_absolute_galois_identity_retains_exact_field_action() -> None:
    galois = AbsoluteGaloisGroup(QQ)
    identity = galois.one()

    assert identity.exact_action() is not None
    assert identity.underlying_field_morphism() == identity.as_morphism()
    assert identity.is_globally_evaluable()
    assert identity.fixes_base_field()
    assert identity.realized_stages().cardinality() == cardinal(0)
