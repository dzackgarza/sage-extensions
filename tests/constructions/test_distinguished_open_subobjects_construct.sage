r"""D(5) in Spec Z retains its defining function and localization."""

from sage_extensions.all import *  # noqa: F401,F403


def test_distinguished_open_d_five_has_coordinate_ring_z_with_five_inverted() -> None:
    spectrum = ZZ.spectrum()
    open_set = spectrum.distinguished_open(ZZ(5))
    coordinate_ring = open_set.coordinate_ring()

    assert open_set.function() == ZZ(5)
    assert coordinate_ring(ZZ(5)).is_unit()
    assert not coordinate_ring(ZZ(3)).is_unit()
