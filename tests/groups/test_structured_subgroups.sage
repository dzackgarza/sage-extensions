r"""Structured subgroups of $O(A_1) = \{\pm 1\}$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_stabilizers_kernels_and_centralizers_in_the_orthogonal_group_of_a1() -> None:
    r"""For $L = A_1 = \mathbf{Z}v$: $O(L) = \{\pm1\}$ has order 2.

    $-1$ moves $v$ and preserves $\mathbf{Z}v$, so the stabilizer of $v$ and the
    pointwise stabilizer of $\mathbf{Z}v$ are trivial while the setwise
    stabilizer is all of $O(L)$.  $A_L \cong \mathbf{Z}/2$ has trivial
    orthogonal group, so $O(L) \to O(A_L)$ has kernel $O(L)$.
    """
    lattice = Lattices(ZZ)("A1")
    group = lattice.O()
    vector = lattice.module_generator(0)
    line = vector.sublattice()
    minus_one = next(g for g in group if g != group.one())

    assert group.cardinality() == 2
    assert minus_one(vector) == -vector
    assert group.stabilizer(vector).cardinality() == 1
    assert group.stabilizer(line, action="setwise").cardinality() == 2
    assert group.stabilizer(line, action="pointwise").cardinality() == 1
    assert group.kernel(group.discriminant_representation()).cardinality() == 2
    assert group.centralizer(minus_one).cardinality() == 2
    assert group.subgroup([minus_one]).cardinality() == 2
    assert group.subgroup([]).cardinality() == 1
