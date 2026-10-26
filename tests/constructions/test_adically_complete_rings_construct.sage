r"""The 3-adic integers are complete for their maximal ideal."""

from sage_extensions.all import *  # noqa: F401,F403


def test_three_adic_integers_are_adically_complete() -> None:
    integers = Zp(3)

    assert integers in AdicallyCompleteRings()
    assert integers.is_adically_complete()
    assert integers.ideal_of_definition() == integers.ideal(integers(3))

