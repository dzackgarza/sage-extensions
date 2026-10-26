r"""V(10) in Spec Z retains its defining ideal and closed points."""

from sage_extensions.all import *  # noqa: F401,F403


def test_closed_set_v_ten_retains_the_defining_ideal() -> None:
    spectrum = ZZ.spectrum()
    closed = spectrum.closed_set(ZZ.ideal(10))

    assert closed.defining_ideal() == ZZ.ideal(10)
    assert spectrum(ZZ.ideal(2)) in closed
    assert spectrum(ZZ.ideal(5)) in closed
