r"""Normal affine spectra detect the normality of their coordinate rings."""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


NORMAL = {"ZZ", "QQ", "GF(5)", "ZZ[i]", "ZZ[sqrt-5]", "ZZ[x]", "QQ[x,y]", "QQ[x]", "ZZ_3", "QQ[[t]]"}
NOT_NORMAL = {"QQ[x,y]/(y^2-x^3)", "ZZ/12", "QQ[e]/(e^2)", "QQ[x,y]/(xy)"}


@pytest.mark.parametrize("name", sorted(NORMAL | NOT_NORMAL))
def test_normality_of_spec(build, name) -> None:
    ring = build(name)

    assert (ring.affine_spectrum() in NormalSchemes(ring)) == (name in NORMAL)
    assert (ring.affine_spectrum() in NormalSchemes(ZZ)) == (name in NORMAL)
