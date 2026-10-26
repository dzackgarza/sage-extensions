r"""Every nonzero rational number is a unit."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rationals_form_a_division_ring() -> None:
    element = QQ(7) / 3

    assert QQ in DivisionRings()
    assert element != QQ.zero()
    assert element * element.inverse() == QQ.one()

