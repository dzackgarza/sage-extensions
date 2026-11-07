r"""Stabilizers in ``O(L)`` of the family of simple roots, up to reindexing.

For a simply-laced root lattice ``L`` and its simple roots ``v: Delta -> L``
the stabilizer ``O(L)_[v] = {g : g o v = v o sigma for a bijection sigma of Delta}``
consists of the isometries permuting the simple roots, which are the Dynkin
diagram automorphisms; ``O(L)`` is their semidirect product with the Weyl
group, so the stabilizer has order ``|O(L)| / |W(L)|``.  The two orders are
the values the repository already records in its Coxeter session: ``A2``
gives ``12/6``, ``A3`` gives ``48/24``, ``D4`` gives ``1152/192`` which is
triality, and ``E8`` gives ``696729600/696729600``, the trivial group
(Humphreys, *Reflection Groups and Coxeter Groups*, 2.10 and the table of 2.11).

``A1 + A1 + A1`` separates the pairings from a bare count of vectors: three
mutually orthogonal roots admit every permutation, so their stabilizer has
order six where the ``A3`` chain on three vectors admits only the reversal.
"""

import pytest

from sage_extensions.all import *

# Cartan type: (order of the diagram automorphism group, |O(L)|, |W(L)|)
ROOT_BASES = {
    "A2": (2, 12, 6),
    "A3": (2, 48, 24),
    "D4": (6, 1152, 192),
    "E8": (1, 696729600, 696729600),
}


def _simple_roots(lattice):
    return Sets().Mor(lattice.module_generating_set(), lattice)(lattice.module_generator)


@pytest.mark.parametrize("name", ROOT_BASES)
def test_the_stabilizer_of_the_simple_roots_is_the_diagram_automorphism_group(name) -> None:
    diagram_order, isometry_order, weyl_order = ROOT_BASES[name]
    root_lattice = Lattices(ZZ)(name)
    stabilizer = root_lattice.O().stabilizer(_simple_roots(root_lattice))

    assert stabilizer.cardinality() == diagram_order
    assert diagram_order * weyl_order == isometry_order


def test_orthogonal_roots_admit_every_permutation_but_a_chain_does_not() -> None:
    chain = Lattices(ZZ)("A3")
    orthogonal = NamedLattices.A1 ** 3
    assert chain.module_rank() == orthogonal.module_rank() == 3

    assert chain.O().stabilizer(_simple_roots(chain)).cardinality() == 2
    assert orthogonal.O().stabilizer(_simple_roots(orthogonal)).cardinality() == 6


def test_the_swap_of_the_A2_simple_roots_is_an_involution_of_O_A2() -> None:
    root_lattice = Lattices(ZZ)("A2")
    positions = root_lattice.module_generating_set()
    first, second = positions[0], positions[1]
    roots = _simple_roots(root_lattice)
    action = root_lattice.O().index_action(roots)
    swap = next(g for g in root_lattice.O().stabilizer(roots) if action.act(g, first) == second)

    assert swap(root_lattice.module_generator(first)) == root_lattice.module_generator(second)
    assert swap * swap == root_lattice.Aut().one()
    assert swap != root_lattice.Aut().one()


def test_colouring_the_two_A2_roots_differently_kills_the_swap() -> None:
    r"""A colour-preserving reindexing of two roots of different colours is the identity.

    The stabilizer of the coloured family ``((a1, 0), (a2, 1))`` consists of
    the isometries fixing each simple root, which fix the lattice they span.
    """
    lattice = Lattices(ZZ)("A2")
    positions = lattice.module_generating_set()
    colours = Sets.Δ[1]
    points = Sets().product((lattice, colours))
    coloured = Sets().Mor(positions, points)(
        lambda position: points((lattice.module_generator(position), colours[int(positions.ranking_map()(position))])),
    )

    assert lattice.O().stabilizer(coloured).cardinality() == 1


def test_a_redundant_family_in_an_indefinite_lattice_has_the_swap_of_its_two_positive_vectors() -> None:
    r"""In ``<1> + <1> + <-1>`` the family ``(e_0, e_1, e_2, e_0 + e_1)`` is stabilized by ``e_0 <-> e_1``.

    The swap permutes the family (it fixes ``e_0 + e_1``); the four vectors
    span the lattice without being linearly independent.  The reversed family is carried to it by an element of
    the stabilizer of the family, since it is the same family reindexed.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, -1]])
    e = lattice.module_generators()
    vectors = (e[0], e[1], e[2], e[0] + e[1])
    family = Sets().Mor(Sets.Δ[3], lattice)(lambda position: vectors[int(position)])
    reversed_family = Sets().Mor(Sets.Δ[3], lattice)(lambda position: vectors[3 - int(position)])
    stabilizer = lattice.O().stabilizer(family)
    swap = lattice.Aut()({label: e[1 - int(label)] if int(label) < 2 else e[2] for label in lattice.module_generating_set()})

    assert swap in stabilizer
    assert lattice.O().transporter(family, reversed_family) in stabilizer


def test_a_redundant_index_three_family_has_its_integral_hyperbolic_exchange() -> None:
    r"""The columns (2,1), (1,2) span an index-three subgroup of ZZ^2.

    Their sum and a repeated vector preserve this span. Over QQ the
    family spans the whole space. Exchanging e and f is the unique
    integral isometry carrying it to the exchanged family.
    """
    lattice = Lattices(ZZ)([[0, 1], [1, 0]])
    e, f = tuple(lattice.module_generators())
    indices = Sets.Δ[3]
    vectors = (2 * e + f, e + 2 * f, 3 * e + 3 * f, e + 2 * f)
    targets = (e + 2 * f, 2 * e + f, 3 * e + 3 * f, 2 * e + f)
    family = Sets().Mor(indices, lattice)(lambda index: vectors[int(index)])
    target = Sets().Mor(indices, lattice)(lambda index: targets[int(index)])

    witness = lattice.O().transporter(family, target)

    assert witness(e) == f and witness(f) == e
    assert all(witness(value) == image for value, image in zip(vectors, targets, strict=True))
    assert all((~witness)(witness(value)) == value for value in (e, f))


def test_the_reindexed_index_two_hyperbolic_family_has_the_identity_transporter() -> None:
    r"""The rational exchange of 2e and f is not integral, but fixes 2e+f.

    Among O(U)={+-1,+-exchange}, only the identity preserves the family
    {2e,f,2e+f}. Reindexing the family therefore has that transporter.
    """
    lattice = Lattices(ZZ)([[0, 1], [1, 0]])
    e, f = tuple(lattice.module_generators())
    vectors = (2 * e, f, 2 * e + f)
    targets = (f, 2 * e, 2 * e + f)
    family = Sets().Mor(Sets.Δ[2], lattice)(lambda index: vectors[int(index)])
    target = Sets().Mor(Sets.Δ[2], lattice)(lambda index: targets[int(index)])

    witness = lattice.O().transporter(family, target)

    assert witness(e) == e
    assert witness(f) == f
