r"""Smooth affine spectra distinguish smooth from singular base algebras."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


@pytest.mark.parametrize(
    "name, base, smooth",
    [
        ("QQ(i)", "QQ", True),
        ("GF(4)", "GF(2)", True),
        ("QQ[x,y]", "QQ", True),
        ("QQ[x,y]/(y^2-x^3)", "QQ", False),
        ("QQ[e]/(e^2)", "QQ", False),
        ("ZZ[i]", "ZZ", False),
        ("ZZ[x]", "ZZ", True),
    ],
)
def test_smoothness_of_spec_over_a_base(build, name, base, smooth) -> None:
    ring = build(name)
    base_ring = GF(2) if base == "GF(2)" else build(base)

    assert (ring.as_algebra_over(base_ring).affine_spectrum() in SmoothSchemes(base_ring)) == smooth
