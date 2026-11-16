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


def _presented_in_the_basis(standard, changed):
    r"""The form of ``standard`` written in the basis ``changed``, as a fresh presentation.

    A Gram matrix in a new basis is the pullback of the retained form along the
    change of basis, so the transport is the tensor owner's and no pairing is
    written here.
    """
    ring = standard.base_ring()
    labels = tuple(standard.module_generating_set())
    change = Modules(ring).Mor(standard, standard)(
        {
            label: element
            for label, element in zip(labels, changed, strict=True)
        }
    )
    return Lattices(ring)(standard.gram_tensor().pullback(change, change))


def _definite_sum_with_a_connected_display():
    r"""$A_1^4$ in the basis $e_1 + e_2$, $e_2 + e_3$, $e_3 + e_4$, $e_4$."""
    standard = Lattices(ZZ)("A1") ** 4
    basis = tuple(standard.module_generators())
    changed = tuple(basis[position] + basis[position + 1] for position in range(3)) + (basis[3],)
    return _presented_in_the_basis(standard, changed)


def _scrambled_k3():
    r"""The K3 lattice in a basis in which every displayed generator pairs with a neighbour."""
    decomposed = NamedLattices.U ** 3 + NamedLattices.E8 ** 2
    basis = tuple(decomposed.module_generators())
    changed = tuple(basis[position] + basis[position + 1] for position in range(21)) + (basis[21],)
    return _presented_in_the_basis(decomposed, changed)


def test_a_definite_sum_with_a_connected_display_is_decomposable() -> None:
    r"""The four summands embed in the lattice, pair to zero, and fill it.

    Each summand is a sublattice of the lattice with an inclusion into it, so
    four unrelated or repeated copies of $A_1$ would not pass: the inclusion's
    codomain is the lattice itself, the pairing of two different summands --
    the pullback of the form along their two inclusions -- is the zero tensor,
    and the ranks sum to the rank of the nondegenerate lattice, so the sum of
    the summands is direct and full.
    """
    lattice = _definite_sum_with_a_connected_display()
    root_line = Lattices(ZZ)("A1")
    rank = lattice.module_rank()
    gram = lattice.gram_tensor()
    ring = lattice.base_ring()

    assert lattice.is_decomposable() is True
    summands = lattice.indecomposable_summands()
    assert summands.cardinality() == 4
    assert all(summand.is_indecomposable() is True for summand in summands)
    assert all(summand.is_isometric_to(root_line) for summand in summands)
    assert all(summand.inclusion().codomain() is lattice for summand in summands)
    assert sum(int(summand.module_rank()) for summand in summands) == int(rank)
    for left in range(summands.cardinality()):
        for right in range(left + 1, summands.cardinality()):
            pairing = gram.pullback(
                summands[left].inclusion(), summands[right].inclusion()
            )
            rows, columns = (int(extent) for extent in pairing.tensor_shape())
            assert all(
                pairing[i, j] == ring.zero()
                for i in range(rows)
                for j in range(columns)
            )


def test_the_family_reports_no_summands_where_the_decomposition_is_undecided() -> None:
    scrambled = _scrambled_k3()
    decomposed = NamedLattices.U ** 3 + NamedLattices.E8 ** 2

    assert scrambled.is_isometric(decomposed)
    assert decomposed.indecomposable_summands().cardinality() == 5
    with pytest.raises(ValueError):
        scrambled.indecomposable_summands()


def test_the_definite_decomposition_is_the_owner_operation_on_the_lattice() -> None:
    r"""The definite decomposition is `definite_indecomposable_summands`' answer.

    Kneser's decomposition reads the reduction of the form and the
    minimal-vector enumeration, so it is stated for a definite lattice and
    returns that lattice's own summands: a family of sublattices, each carrying
    the form as the pullback along its own inclusion.
    """
    lattice = _definite_sum_with_a_connected_display()
    gram = lattice.gram_tensor()
    summands = definite_indecomposable_summands(lattice)

    assert summands.cardinality() == 4
    assert all(summand.inclusion().codomain() is lattice for summand in summands)
    assert all(
        summand.gram_tensor() == gram.pullback(summand.inclusion(), summand.inclusion())
        for summand in summands
    )
    assert sum(int(summand.module_rank()) for summand in summands) == int(lattice.module_rank())
