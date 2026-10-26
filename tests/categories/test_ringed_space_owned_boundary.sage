r"""Global sections of the structure sheaf of an affine and a projective scheme."""

from sage_extensions.all import *  # noqa: F401,F403


def test_global_functions_on_spec_Z_are_Z_and_on_P1_are_the_constants() -> None:
    r"""``Gamma(Spec Z, O) = Z``; ``Gamma(P^1_Q, O) = Q`` although ``P^1`` is not affine.

    A global function on ``P^1`` is regular on both charts ``Spec Q[t]`` and
    ``Spec Q[1/t]``, so it lies in ``Q[t] cap Q[1/t] = Q``.
    """
    spectrum = ZZ.affine_spectrum()
    line = ProjectiveSpaces(QQ)(1)

    assert spectrum.structure_sheaf().global_sections().is_isomorphic(ZZ)
    assert spectrum.is_affine()
    assert line.structure_sheaf().global_sections().is_isomorphic(QQ)
    assert not line.is_affine()
    assert line.dimension() == 1
