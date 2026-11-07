r"""The discriminant-action sequence of an indefinite lattice, through the public call.

``L.discriminant_sequence_data()`` reports the action of $O(L)$ on the discriminant group
$A_L$: the invariants, the image order, and the kernel's order.  When $O(L)$ is infinite the
kernel of $O(L)\to O(A_L)$ is infinite too -- a cardinal, not an integer.  Computing it as
``int(|O(L)|) // |image|`` raised ``TypeError: cannot convert infinite cardinal ℵ_0 to
integer`` (``cardinals.py:789``) on every lattice containing $U\oplus U$ (issue #309).

Infinitude is a property of the lattice, not of its indefiniteness: $U\oplus U$ has infinite
$O(L)$, while the hyperbolic plane $U$ is indefinite with $|O(U)| = 4$ and keeps the integer
branch.  The kernel's cardinality is not ambiguous: the image lies in $O(A_L)$, which is
finite because $A_L$ is, so $|O(L)| = |\ker|\cdot|\mathrm{image}|$ with finite image and
therefore $|\ker| = |O(L)|$ whenever $O(L)$ is infinite.  A finite $O(L)$ keeps the integer
quotient, which is what the third test pins at the same boundary.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _hyperbolic_plane_sum():
    r"""$U \oplus U$: unimodular, and its $O(L)$ is infinite -- which is the case under test."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U")


def test_the_unimodular_indefinite_plane_has_trivial_discriminant_data() -> None:
    r"""$A_{U\oplus U}$ is trivial, so its action data is the trivial group's."""
    sequence = _hyperbolic_plane_sum().discriminant_sequence_data()

    assert sequence["discriminant_factors"] == []
    assert sequence["discriminant_group_order"] == 1
    assert sequence["image_order"] == 1
    assert sequence["mm_trivial"] is True
    assert sequence["image_normal"] is True


def test_the_kernel_of_the_discriminant_representation_is_infinite() -> None:
    r"""$|\ker(O(L)\to O(A_L))| = |O(L)| = \aleph_0$ for $L = U\oplus U$.

    The image has order one here, so the equality is direct; the value is a cardinal, which
    is what ``is_finite()`` reports and what an integer cannot answer.
    """
    lattice = _hyperbolic_plane_sum()
    sequence = lattice.discriminant_sequence_data()
    kernel = sequence["kernel_order"]

    assert kernel == lattice.orthogonal_group().cardinality()
    assert kernel.is_finite() is False


def test_a_finite_lattice_keeps_an_integer_kernel_order() -> None:
    r"""\(\langle 2\rangle\) has $|O(L)| = 2$ and trivial discriminant image, so the kernel is 2.

    The returned value stays an ordinary integer at this boundary: it converts exactly, and
    the quotient identity $|\ker|\cdot|\mathrm{image}| = |O(L)|$ holds in integers.
    """
    lattice = Lattices(ZZ)([[2]])
    sequence = lattice.discriminant_sequence_data()
    kernel = sequence["kernel_order"]

    assert sequence["discriminant_factors"] == [2]
    assert sequence["image_order"] == 1
    assert kernel * sequence["image_order"] == lattice.orthogonal_group().cardinality()
    assert int(kernel) == 2


def test_the_hyperbolic_plane_is_indefinite_with_a_finite_kernel() -> None:
    r"""$U$ is indefinite and $|O(U)| = 4$, so its kernel is the integer $4$.

    Infinitude is a property of the lattice, not a consequence of being indefinite: this is
    the case that a sentence about "indefinite lattices" would get wrong, and it keeps the
    integer branch at the same boundary.
    """
    lattice = Lattices(ZZ)("U")
    signature = lattice.signature_pair()
    assert signature.first() == cardinal(1)
    assert signature.second() == cardinal(1)

    sequence = lattice.discriminant_sequence_data()
    kernel = sequence["kernel_order"]
    assert sequence["discriminant_factors"] == []
    assert sequence["image_order"] == 1
    assert kernel * sequence["image_order"] == lattice.orthogonal_group().cardinality()
    assert int(kernel) == 4
