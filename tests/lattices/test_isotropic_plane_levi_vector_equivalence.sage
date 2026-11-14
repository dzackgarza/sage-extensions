r"""Vector equivalence under the setwise stabilizer of an isotropic plane, decided on the Levi part (#327).

The consumer: `L.Aut().stabilizer(I, action="setwise").vector_equivalence_witness(u, v)`
decides whether two vectors of an indefinite lattice $L$ are equivalent under
$\mathrm{Stab}_{O(L)}(I)$ for a primitive isotropic plane $I$ with $I^\perp/I$
definite, and returns a witness in that stabilizer when they are.

The specimen: $L = U \oplus U \oplus K$ with $K$ of Gram matrix
$\begin{pmatrix}-2 & 1\\ 1 & -2\end{pmatrix}\oplus(-2)$, negative definite of
rank three, in the bases
$(e_1, f_1)$ and $(e_2, f_2)$ of the two copies of $U$ and $(r, s)$ of $K$, and
$I = \langle e_1, e_2\rangle$, a primitive totally isotropic plane.  Then
$I^\perp = I \oplus K$, so $K_I = I^\perp/I$ is isometric to $K$ and negative
definite, its orthogonal group $O(K_I)$ is finite, and the parabolic is
$P_I = K \ltimes M_I$ with $K = \ker(P_I \to O(I^\perp))$ the pointwise kernel and
$M_I \le GL(I) \times O(I^\perp/I)$ the Levi factor.

What is asserted, and what is not:

* $e_1 + r$ and $e_2 + r$ have the same reduction $[r]$ modulo $I$, and no
  element of the pointwise kernel moves either of them: the kernel fixes
  $I^\perp$ pointwise.  Only a Levi element carries one onto the other — the
  swap $e_1 \leftrightarrow e_2$, $f_1 \leftrightarrow f_2$ of the two copies of
  $U$, which fixes $K$ — so the witness this call returns is a Levi element;
* $r$ and $-r$ likewise differ by the Levi factor's action on $K_I$;
* $r$ and $s$ have the same square and are not equivalent: $K_I$ is isometric
  to $K$, whose two vectors here are $r$, a root of the $A_2$ block, and $s$,
  the $(-2)$ summand's generator, and the reflections of the parabolic respect
  the two blocks, so the two lie in different orbits of the image of $P_I$ in
  $O(K_I)$.

No number is asserted: every count in this module's calls is that call's output,
and none of them is a lattice-database card value.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""$L = U \oplus U \oplus K$ with $K$ negative definite, its plane $I = \langle e_1, e_2\rangle$, and the basis."""

    lattices = Lattices(ZZ)
    ambient = lattices("U") + lattices("U") + lattices([[-2, 1], [1, -2]]) + lattices([[-2]])
    e1, f1, e2, f2, r, _second_root, s = tuple(ambient.module_generators())
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    return ambient, plane, (e1, f1, e2, f2, r, s)


def test_the_setwise_stabilizer_transports_a_vector_by_a_levi_element() -> None:
    r"""$e_1 + r$ is carried to $e_2 + r$ by the swap of the two copies of $U$.

    The two vectors have the same reduction modulo $I$ and the pointwise kernel
    fixes $I^\perp$ pointwise, so no element of the kernel carries one onto the
    other: the witness lies in the Levi factor.
    """

    ambient, plane, (e1, f1, e2, f2, r, s) = _specimen()
    stabilizer = ambient.Aut().stabilizer(plane, action="setwise")
    witness = stabilizer.vector_equivalence_witness(e1 + r, e2 + r)
    assert witness in stabilizer
    assert witness(e1 + r) == e2 + r
    assert witness(r) == r


def test_the_setwise_stabilizer_transports_a_vector_by_the_levi_factor_on_the_reduction() -> None:
    r"""$r$ is carried to $-r$ by the element of the Levi factor acting as $-1$ on $K_I$."""

    ambient, plane, (e1, f1, e2, f2, r, s) = _specimen()
    stabilizer = ambient.Aut().stabilizer(plane, action="setwise")
    witness = stabilizer.vector_equivalence_witness(r, -r)
    assert witness in stabilizer
    assert witness(r) == -r


def test_the_setwise_stabilizer_separates_vectors_in_different_reduction_orbits() -> None:
    r"""$r$ and $s$ have the same square and lie in different orbits of the image of $P_I$ in $O(K_I)$."""

    ambient, plane, (e1, f1, e2, f2, r, s) = _specimen()
    stabilizer = ambient.Aut().stabilizer(plane, action="setwise")
    assert stabilizer.vector_equivalence_witness(r, s) is None
