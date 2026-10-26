r"""The injections of an orthogonal sum, the twist functor, and parabolic Gram matrices.

- The summand injections \(\iota_k\colon L_k\to L_0\oplus L_1\) preserve the form and have
  mutually orthogonal images: \(\iota_0(x)\cdot\iota_1(y)=0\).
- The twist \(L\mapsto L(n)\) multiplies the form by \(n\): a rank-\(r\) lattice has
  \(\det L(n) = n^r\det L\), so \(\det A_2(2) = 4\cdot3 = 12\), and a root of \(A_2\) has
  square \(-4\) in \(A_2(2)\).
- A unimodular lattice is its own dual, so \(U^\vee\) has determinant \(-1\).
- The Gram \(\begin{pmatrix}-2&2\\2&-2\end{pmatrix}\) of the affine diagram \(\tilde A_1\) is
  negative semidefinite with a one-dimensional radical, so it is parabolic; \(A_2\) is
  elliptic, not parabolic.
"""

from sage_extensions.all import *


def test_the_summand_injections_preserve_the_form_and_have_orthogonal_images() -> None:
    root_lattice = Lattices(ZZ)("A2")
    plane = Lattices(ZZ)("U")
    total = root_lattice + plane
    first_injection = total.injection(0)
    second_injection = total.injection(1)
    e, f = plane.module_generators()
    a, b = root_lattice.module_generators()

    assert second_injection(e) * second_injection(f) == 1
    assert second_injection(e) * second_injection(e) == 0
    assert first_injection(a) * first_injection(b) == 1
    assert first_injection(a) * first_injection(a) == -2
    for root in (a, b):
        for vector in (e, f):
            assert first_injection(root) * second_injection(vector) == 0


def test_the_second_factor_of_a2_plus_u_is_unimodular() -> None:
    factor = (Lattices(ZZ)("A2") + Lattices(ZZ)("U")).biproduct_factor(1)

    assert factor.determinant() == -1
    assert factor.is_unimodular()
    assert factor.signature_pair() == signature_pair(1, 1)


def test_the_twist_functor_by_two_scales_the_form() -> None:
    twist = Lattices(ZZ).twist_functor(2)
    root_lattice = Lattices(ZZ)("A2")
    twisted = twist(root_lattice)
    first, second = twisted.module_generators()

    assert twisted.determinant() == 12
    assert first * first == -4
    assert first * second == 2
    assert root_lattice.twist(2).determinant() == 12


def test_the_dual_of_a_unimodular_lattice_is_itself() -> None:
    plane = Lattices(ZZ)("U")

    assert plane.dual_lattice().determinant() == -1
    assert plane.dual_lattice().is_unimodular()


def test_the_affine_a1_gram_is_parabolic_and_a2_is_elliptic() -> None:
    affine = Lattices(ZZ)([[-2, 2], [2, -2]])
    root_lattice = Lattices(ZZ)("A2")

    assert affine.is_parabolic()
    assert not affine.is_elliptic()
    assert root_lattice.is_elliptic()
    assert not root_lattice.is_parabolic()
