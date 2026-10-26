r"""The zeta function of P^1 over F_5 is 1/((1-T)(1-5T))."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_line_zeta_function_over_five() -> None:
    line = ProjectiveSpaces(GF(5))(1)
    zeta = line.zeta_function()
    rational_functions = zeta.parent()
    T = rational_functions.algebra_generator("T")

    denominator = (rational_functions.one() - T) * (rational_functions.one() - 5 * T)
    assert zeta * denominator == rational_functions.one()
