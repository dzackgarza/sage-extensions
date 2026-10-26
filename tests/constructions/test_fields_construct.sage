r"""The rationals satisfy all field refinements at once."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rationals_are_a_field() -> None:
    element = QQ(7) / 3

    assert QQ in Fields()
    assert QQ in PrincipalIdealDomains()
    assert QQ in LocalRings()
    assert QQ in ArtinianRings()
    assert QQ.krull_dimension() == 0
    assert element * element.inverse() == QQ.one()

