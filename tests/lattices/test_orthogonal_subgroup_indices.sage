r"""The stable group and the real spinor kernel of $L = U \oplus U \oplus \langle -6 \rangle$.

$L$ has signature $(2,3)$ and discriminant form $A_L = \mathbb{Z}/6$ with
$q(x) = -x^2/6 \bmod 2\mathbb{Z}$.  An automorphism of $A_L$ is $x \mapsto ux$ with
$u \in (\mathbb{Z}/6)^\times = \{1, 5\}$, and $q(5x) = -25x^2/6 = q(x) - 4x^2$, so
$O(q_L) = \{\pm 1\}$ has order two.  $-\mathrm{id}_L$ induces $-1 \ne 1$ on $A_L$, so
the image of $O(L) \to O(q_L)$ is all of $O(q_L)$ and
$[O(L) : \widetilde O(L)] = 2$ for the stable group $\widetilde O(L) = \ker(O(L) \to O(q_L))$.

$O^+(L)$ is the kernel of the real spinor norm with the multiplier $-\tfrac12$
(Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §1): a reflection $s_v$ has
$\mathrm{sn}_{\mathbb R}(s_v) = \operatorname{sign}(-\tfrac12 (v,v))$, so it lies in
$O^+(L)$ exactly when it fixes the orientation of the positive definite planes.  The
reflection in $e + f$, with $(e, f)$ the hyperbolic basis of the first $U$, has
$(e+f, e+f) = 2$ and real spinor norm $-1$.  The character
$O(L) \to \{\pm 1\}$ is therefore onto and $[O(L) : O^+(L)] = 2$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _lattice():
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-6]])


def test_the_stable_group_has_index_the_order_of_the_discriminant_image() -> None:
    r"""$[O(L) : \widetilde O(L)] = |\rho(O(L))| = |O(q_L)| = 2$, and its Schreier generators lie in it."""
    lattice = _lattice()
    stable = lattice.stable_orthogonal_group()
    negation = lattice.O()(lambda label: -lattice.module_generator(label))

    assert negation not in stable
    assert lattice.discriminant_group().orthogonal_group().cardinality() == 2
    assert lattice.discriminant_image().cardinality() == 2
    assert stable.coset_space().cardinality() == 2
    assert all(generator in stable for generator in stable.group_generators())


def test_the_real_spinor_kernel_has_index_two() -> None:
    r"""$[O(L) : O^+(L)] = 2$: the reflection in the norm-two vector $e+f$ is outside $O^+(L)$."""
    lattice = _lattice()
    plus = lattice.O_plus()
    e, f = tuple(lattice.module_generators())[:2]

    assert lattice.reflection(e + f) not in plus
    assert lattice.reflection(e - f) in plus
    assert plus.coset_space().cardinality() == 2
    assert all(generator in plus for generator in plus.group_generators())
