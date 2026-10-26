r"""The root lattice $A_2$ from its name."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_is_even_nondegenerate_of_determinant_three() -> None:
    r"""$A_2$ has Gram matrix $\begin{psmallmatrix}-2&1\\1&-2\end{psmallmatrix}$: even, determinant $3$, $|b(e_1, e_2)| = 1$.

    Source: Conway–Sloane, *Sphere Packings, Lattices and Groups*, Ch. 4 §6.1
    (with the negative-definite sign convention of this repository).
    """
    lattice = Lattices(ZZ)("A2")
    first, second = lattice.module_generator(0), lattice.module_generator(1)

    assert lattice.module_rank() == 2
    assert lattice.is_even()
    assert lattice.is_nondegenerate()
    assert lattice.determinant() == 3
    assert abs(lattice.b(first, second)) == 1
