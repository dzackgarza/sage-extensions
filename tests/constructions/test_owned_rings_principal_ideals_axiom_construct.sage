r"""Every ideal of the integers is principal."""

from sage_extensions.all import *  # noqa: F401,F403


def test_integers_are_a_principal_ideal_domain() -> None:
    ideal = ZZ.ideal(12)

    assert ZZ in PrincipalIdealDomains()
    assert ideal.ideal_generators().cardinality() == cardinal(1)

