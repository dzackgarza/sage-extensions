r"""Isometry of integral lattices decided by ``Isom(L, M).is_empty()`` and ``isometry_classes``.

Expected values are cited from Conway--Sloane, *Sphere Packings, Lattices and
Groups*, Ch. 15 (extraction
``references/literature/lattice-research/conway1999sphere.md``).  Written
unexecuted under DEV-58; executed at T.
"""

from sage_extensions.all import *
from sage_extensions.categories.sets.finite_families import finite_family


def test_dickson_ross_ternary_forms_are_isometric() -> None:
    # CS99 Ch. 15 §11 (l.12903-12929): one genus, one spinor genus, and the
    # unimodular matrix M of (50) transforms the first form into the second.
    first = Lattices(ZZ)([[3, 1, 0], [1, 23, 0], [0, 0, -1]])
    second = Lattices(ZZ)([[7, 3, 0], [3, 11, 0], [0, 0, -1]])
    assert first.Isom(second).is_empty() is False
    assert first.is_isometric(second) is True
    isometry = first.Isom(second).an_element()
    assert isometry.domain() is first and isometry.codomain() is second


def test_a_genus_of_two_spinor_genera_has_two_classes() -> None:
    # CS99 Ch. 15 §11 (l.12933): the genus of diag(-1, 64, 2) contains two
    # spinor genera and hence two classes, f and f * Delta(3).  Its class
    # number is therefore 2 [CS99, Ch. 15, Thm 14].
    lattice = Lattices(ZZ)([[-1, 0, 0], [0, 64, 0], [0, 0, 2]])
    representatives = lattice.genus().representatives()
    assert representatives.cardinality() == 2
    first, second = representatives[0], representatives[1]
    assert first.Isom(second).is_empty() is True
    # Isom(L, M) has distinct endpoints and no placement among the sets, so its
    # cardinality is the core Mor's operation, read from the isometry decision.
    assert first.Isom(second).cardinality() == 0
    classes = Lattices(ZZ).isometry_classes(finite_family((first, second, lattice)))
    assert classes.cardinality() == 2


def test_isometric_binary_definite_presentations() -> None:
    # A_2 has Gram [[2,-1],[-1,2]]; negating one basis vector gives [[2,1],[1,2]].
    first = Lattices(ZZ)([[2, -1], [-1, 2]])
    second = Lattices(ZZ)([[2, 1], [1, 2]])
    assert first.Isom(second).is_empty() is False
    assert first.Isom(second).an_element().domain() is first
