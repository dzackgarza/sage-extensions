r"""Vector equivalence under the stabilizer of a primitive isotropic plane of $U \oplus U(2)$ (#324).

The consumer: on an indefinite lattice $L$ and a primitive sublattice $I$, a call
decides whether two vectors of $L$ are equivalent under $\mathrm{Stab}_{O(L)}(I)$
and returns a witness in that stabilizer when they are.

The specimen: $L = U \oplus U(2)$ with basis $(e_1, f_1)$ of $U$
($b(e_1, f_1) = 1$) and $(e_3, f_3)$ of $U(2)$ ($b(e_3, f_3) = 2$), and
$I = \langle e_1, e_3\rangle$, a primitive totally isotropic plane.  $I$ is
maximal isotropic: $I^\perp = I$, so its reduction $K_I = I^\perp/I$ is the zero
lattice and the parabolic is $P_I = \Gamma \ltimes K$ with $K$ the pointwise
kernel and $\Gamma$ the image in $GL(I)$.

What is asserted, and what is not:

* the setwise stabilizer transports $f_1$ to $f_1 + e_3$ and returns a witness
  that lies in the stabilizer and carries the first vector onto the second;
* it separates $f_1$ from $2 f_1$, which is not in its orbit because
  $b(-, e_1)$ takes the values $-1, 0$ on one and $-2, 0$ on the other and every
  element of the parabolic acts on $I$ by a unimodular map;
* the pointwise stabilizer transports $f_1$ to $f_1 + e_3$ as well, and decides
  that $f_1$ is *not* carried to $f_3$: it is exactly the pointwise kernel
  $K = \ker(P_I \to \mathrm{Aut}(I^\perp))$, whose complete integral parameter
  module is $K$ itself, so that `None` is a decision and not a failure to find a
  witness.

No number is asserted: the only claims are the three relations above.  Every
count in this module's calls is this call's output, not a lattice-database card
value.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""$L = U \oplus U(2)$, its primitive isotropic plane $\langle e_1, e_3\rangle$, and the basis."""

    lattices = Lattices(ZZ)
    ambient = lattices("U") + lattices("U").twist(2)
    e1, f1, e3, f3 = tuple(ambient.module_generators())
    plane = ambient.primitive_isotropic_subobject(e1, e3)
    return ambient, plane, (e1, f1, e3, f3)


def test_the_setwise_stabilizer_of_a_primitive_isotropic_plane_transports_a_vector():
    ambient, plane, (e1, f1, e3, f3) = _specimen()
    stabilizer = ambient.O().setwise_stabilizer(plane.inclusion())
    witness = stabilizer.vector_equivalence_witness(f1, f1 + e3)
    assert witness in stabilizer
    assert witness(f1) == f1 + e3


def test_the_setwise_stabilizer_separates_vectors_of_different_reduction_content():
    ambient, plane, (e1, f1, e3, f3) = _specimen()
    stabilizer = ambient.O().setwise_stabilizer(plane.inclusion())
    assert stabilizer.vector_equivalence_witness(f1, 2 * f1) is None


def test_the_pointwise_stabilizer_of_the_plane_decides_vectors_completely():
    ambient, plane, (e1, f1, e3, f3) = _specimen()
    stabilizer = ambient.O().pointwise_stabilizer(plane.inclusion())
    witness = stabilizer.vector_equivalence_witness(f1, f1 + e3)
    assert witness in stabilizer
    assert witness(f1) == f1 + e3
    assert stabilizer.vector_equivalence_witness(f1, f3) is None
