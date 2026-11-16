r"""A subobject is primitive exactly when its inclusion has torsion-free cokernel.

For $P \le L$ this is the statement that $P$ is saturated in $L$: $L/P$ is
torsion-free, so $L/P$ is free over a principal ideal domain.  The decision is
one on the inclusion, and its coordinate matrix is taken in the frame of that
inclusion's own codomain -- so the same vectors can be primitive in a sublattice
and not in the lattice containing it.  The last test below is exactly that case.

$U \oplus U$ has basis $e_1, f_1, e_2, f_2$ with $b(e_i, f_i) = 1$ and
$q(e_i) = q(f_i) = 0$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_span_is_primitive_exactly_when_its_quotient_is_torsion_free() -> None:
    r"""$f_2$ is outside $\langle e_1, 2f_2\rangle$ while $2f_2$ is inside it."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = lattice.module_generators()
    primitive = lattice.subobject_on((e1, f2))
    doubled = lattice.subobject_on((e1, 2 * f2))
    doubled_line = lattice.subobject_on((2 * e1,))

    assert primitive.is_primitive() is True
    assert primitive.inclusion().cokernel().is_torsion_free() is True
    assert doubled.is_primitive() is False
    assert doubled.inclusion().cokernel().is_torsion_free() is False
    assert doubled_line.is_primitive() is False
    assert lattice.subobject_on((f1 - e1,)).is_primitive() is True
    assert lattice.subobject_on(()).is_primitive() is True


def test_a_primitivity_decision_is_read_in_the_inclusions_own_codomain() -> None:
    r"""$2U$'s own basis vector spans a primitive line in $2U$ and not in $U \oplus U$.

    $2U = \langle 2e_1, 2f_1 \rangle$ is a sublattice of $U \oplus U$ with a
    non-standard basis: every one of its basis vectors is twice a vector of $U
    \oplus U$.  A line spanned by one of them is spanned by a basis vector of
    $2U$, hence primitive there, while the same line misses a factor two in $U
    \oplus U$, and $2U$ itself is not saturated in $U \oplus U$.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = lattice.module_generators()
    doubled = lattice.subobject_on((2 * e1, 2 * f1))
    basis = doubled.module_generators()
    lifted = basis[0]
    above = tuple(doubled.inclusion()(generator) for generator in basis)

    assert doubled.subobject_on((lifted,)).is_primitive() is True
    assert lattice.subobject_on((doubled.inclusion()(lifted),)).is_primitive() is False
    assert lattice.subobject_on(above).is_primitive() is False
