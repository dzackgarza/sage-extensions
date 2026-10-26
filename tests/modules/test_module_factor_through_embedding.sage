r"""Factoring a map of abelian groups through a monomorphism."""

from sage_extensions.all import *  # noqa: F401,F403


def test_multiplication_by_6_on_z_factors_through_multiplication_by_2_as_multiplication_by_3() -> None:
    r"""$6 = 2 \cdot 3$, and the identity does not factor through $2\colon \mathbb Z \hookrightarrow \mathbb Z$
    because $1 \notin 2\mathbb Z$.

    Source: by hand.
    """
    M = ZZ**1
    e = M.module_generator(0)
    doubling = M.Mono(M)({0: 2 * e})
    sixfold = M.End()({0: 6 * e})

    factor = sixfold.factor_through(doubling)
    assert factor(e) == 3 * e
    assert doubling * factor == sixfold
    assert not doubling.is_in_image(e)
    assert doubling.is_in_image(4 * e)
