r"""The hyperbolic plane, computed from its name."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_hyperbolic_plane_has_determinant_minus_one_and_signature_one_one() -> None:
    r"""$U$ is the even unimodular lattice of rank $2$ and signature $(1, 1)$, with isotropic basis $e, f$ and $b(e, f) = 1$.

    Source: Serre, *A Course in Arithmetic*, V.1.3.
    """
    U = Lattices(ZZ)("U")
    e, f = U.module_generator(0), U.module_generator(1)

    assert U.module_rank() == 2
    assert U.determinant() == -1
    assert U.signature_pair() == signature_pair(1, 1)
    assert U.b(e, e) == 0
    assert U.b(f, f) == 0
    assert U.b(e, f) == 1
