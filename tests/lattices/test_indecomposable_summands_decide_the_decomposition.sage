r"""The family of indecomposable summands is a decomposition the lattice decides.

A definite lattice decomposes uniquely into indecomposables (Eichler), and
Kneser's construction finds that decomposition: a minimal vector is not a sum
of two nonzero orthogonal vectors, so the minimal vectors fall into the
summands along the connected components of their nonorthogonality graph
(Kneser, *Quadratische Formen*, section 27).  The lattice below is
$A_1^4$ in a basis in which every displayed generator pairs with its
neighbour, so no Gram entry separates a summand and the display on its own
exhibits nothing; the four summands are still the lattice's own.

A lattice presented by a Gram matrix that separates nothing has no decided
decomposition, and the family then reports none.  A family of one summand is
not a weaker answer: it states that the K3 lattice, which is
$U^3 \oplus E_8(-1)^2$, is indecomposable.
"""

from sage_extensions.all import *

import pytest


def _definite_sum_with_a_connected_display():
    r"""$A_1^4$ in the basis $e_1 + e_2$, $e_2 + e_3$, $e_3 + e_4$, $e_4$."""
    standard = Lattices(ZZ)("A1") ** 4
    basis = tuple(standard.module_generators())
    changed = tuple(basis[position] + basis[position + 1] for position in range(3)) + (basis[3],)
    return Lattices(ZZ)(tuple(tuple(standard.b(x, y) for y in changed) for x in changed))


def _scrambled_k3():
    r"""The K3 lattice in a basis in which every displayed generator pairs with a neighbour."""
    decomposed = NamedLattices.U ** 3 + NamedLattices.E8 ** 2
    basis = tuple(decomposed.module_generators())
    changed = tuple(basis[position] + basis[position + 1] for position in range(21)) + (basis[21],)
    return Lattices(ZZ)(tuple(tuple(decomposed.b(x, y) for y in changed) for x in changed))


def test_a_definite_sum_with_a_connected_display_is_decomposable() -> None:
    lattice = _definite_sum_with_a_connected_display()
    root_line = Lattices(ZZ)("A1")

    assert lattice.is_decomposable() is True
    summands = lattice.indecomposable_summands()
    assert summands.cardinality() == 4
    assert all(summand.is_indecomposable() is True for summand in summands)
    assert all(summand.is_isometric_to(root_line) for summand in summands)


def test_the_family_reports_no_summands_where_the_decomposition_is_undecided() -> None:
    scrambled = _scrambled_k3()
    decomposed = NamedLattices.U ** 3 + NamedLattices.E8 ** 2

    assert scrambled.is_isometric(decomposed)
    assert decomposed.indecomposable_summands().cardinality() == 5
    with pytest.raises(ValueError):
        scrambled.indecomposable_summands()
