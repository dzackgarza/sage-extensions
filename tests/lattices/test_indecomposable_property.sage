r"""Orthogonal indecomposability is a property of the lattice, not its presentation.

For even rank-two lattices, a nontrivial orthogonal sum has two nonzero
rank-one factors, each with even norm. Its determinant therefore has absolute
value at least four. Thus A2, of determinant three, is indecomposable.
The hyperbolic plane U is indecomposable because an even unimodular rank-one
summand would have norm ±1, a contradiction.
"""

from sage_extensions.all import *


def _first_n(iterator, count):
    return tuple(next(iterator) for _ in range(count))


def test_indecomposable_property_category_supplies_known_objects() -> None:
    C = Lattices(ZZ).Indecomposable()
    known = C.known_objects()

    assert C.an_object() in C
    assert any(L.is_isometric_to(Lattices(ZZ)("A2")) for L in known)
    assert all(L.is_indecomposable() is True for L in known)
    assert all(L in C for L in known)
    assert Lattices(ZZ)("E8") in C


def test_irreducible_root_system_need_not_be_an_indecomposable_lattice() -> None:
    category = Lattices(ZZ)
    indecomposable = category.Indecomposable()
    # An irreducible root system need not yield an orthogonally
    # indecomposable integral lattice.
    b2 = category("B2")
    assert b2.is_decomposable() is True
    assert b2.is_indecomposable() is False
    assert b2 not in indecomposable


def test_twisted_and_untwisted_are_lattice_property_categories() -> None:
    category = Lattices(ZZ)
    plane = category("U")
    twice_plane = plane.twist(2)
    root_line = category("A1")

    assert plane.is_indecomposable() is True
    assert plane.is_untwisted() is True
    assert plane in category.Untwisted().Indecomposable()
    assert plane in category.Indecomposable().Untwisted()
    assert twice_plane.is_indecomposable() is True
    assert twice_plane.is_twisted() is True
    assert twice_plane in category.Twisted().Indecomposable()
    assert twice_plane in category.Indecomposable().Twisted()
    assert twice_plane not in category.Untwisted()
    assert root_line.is_twisted() is True
    assert category([[1]]).is_untwisted() is True
    assert category([[-1]]).is_untwisted() is True


def test_known_construction_seeds_come_from_untwisted_indecomposables() -> None:
    category = Lattices(ZZ)
    seeds_category = category.Untwisted().Indecomposable()
    seeds = seeds_category.known_objects()

    assert all(L.is_untwisted() is True and L.is_indecomposable() is True for L in seeds)
    assert all(L in seeds_category for L in seeds)
    assert any(L.gram_tensor() == category("U").gram_tensor() for L in seeds)
    assert any(L.gram_tensor() == category("A2").gram_tensor() for L in seeds)
    assert all(L.gram_tensor() != category("A1").gram_tensor() for L in seeds)

    twisted = category.Twisted().Indecomposable()
    twisted_known = twisted.known_objects()
    assert all(L.is_twisted() is True and L.is_indecomposable() is True for L in twisted_known)
    assert all(L in twisted for L in twisted_known)
    assert any(L.gram_tensor() == category("A1").gram_tensor() for L in twisted_known)


def test_odd_unimodular_family_is_indecomposable_only_in_rank_one() -> None:
    indecomposable = Lattices(ZZ).Indecomposable()
    known = indecomposable.known_objects(max_rank=3)

    for positive in range(4):
        for negative in range(4 - positive):
            rank = positive + negative
            if rank == 0:
                continue
            lattice = Lattices.IPQ(positive, negative)
            assert lattice.is_decomposable() is (rank >= 2)
            assert (lattice in indecomposable) is (rank == 1)
            if rank >= 2:
                assert all(item.gram_tensor() != lattice.gram_tensor() for item in known)


def test_indecomposability_does_not_depend_on_a_selected_sum_presentation() -> None:
    C = Lattices(ZZ)
    orthogonal_square = C([[-2, 0], [0, -2]])
    a2 = C([[2, -1], [-1, 2]])

    assert orthogonal_square.is_decomposable() is True
    assert orthogonal_square not in C.Indecomposable()
    assert a2.is_indecomposable() is True
    assert a2 in C.Indecomposable()


def test_unbounded_construction_enumeration_is_fair_and_keeps_gluing_maps() -> None:
    C = Lattices(ZZ)
    line = C([[2]])
    built = _first_n(C.construction_enumeration((line,)), 7)

    assert all(
        item.lattice.form_content() >= 2 * item.factors[0].lattice.form_content()
        for item in built if item.operation == "twist"
    )
    assert all(item.witness.index() > 1 for item in built if item.operation == "overlattice")
    assert any(item.operation == "twist" and item.lattice.determinant() == 4 for item in built)
    assert any(item.operation == "orthogonal_sum" and item.lattice.module_rank() == 2 for item in built)
    assert any(item.operation == "tensor_product" and item.lattice.determinant() == 4 for item in built)
    proper_line = C([[4]])
    seed, proper = _first_n(C.construction_enumeration((proper_line,)), 2)
    assert seed.lattice is proper_line
    assert proper.operation == "overlattice" and proper.witness.index() == 2
    assert tuple(L.gram_tensor() for L in _first_n(C.object_enumeration((line,)), 2)) == tuple(item.lattice.gram_tensor() for item in built[:2])


def test_infinite_seed_stream_is_visited_fairly() -> None:
    C = Lattices(ZZ)

    def seeds():
        scale = 1
        while True:
            yield C([[scale]])
            scale += 1

    first = _first_n(C.construction_enumeration(seeds()), 3)
    assert first[0].operation == "seed" and first[0].lattice.determinant() == 1
    assert any(item.operation == "seed" and item.lattice.determinant() == 2 for item in first)


def test_standard_specimens_use_the_lattice_funnel() -> None:
    C = Lattices(ZZ)
    specimens = []
    for lattice in C.standard_objects():
        if lattice.module_rank() > 10:
            break
        specimens.append(lattice)
    assert any(L.gram_tensor() == Lattices.IPQ(2, 1).gram_tensor() for L in specimens)
    assert any(L.gram_tensor() == Lattices.IIPQ(1, 9).gram_tensor() for L in specimens)
    for kind, rank in (("A", 2), ("B", 2), ("C", 2), ("D", 4), ("E", 8), ("F", 4), ("G", 2)):
        expected = Lattices.root_lattice(kind, rank)
        assert any(L.gram_tensor() == expected.gram_tensor() for L in specimens)
