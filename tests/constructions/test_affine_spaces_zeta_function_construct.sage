r"""The zeta function of A^2 over F_5 is 1/(1 - 25 T)."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_plane_zeta_function_over_five() -> None:
    plane = AffineSpaces(GF(5))(2)
    zeta = plane.zeta_function()
    rational_functions = zeta.parent()
    T = rational_functions.algebra_generator("T")

    assert zeta * (rational_functions.one() - 25 * T) == rational_functions.one()
