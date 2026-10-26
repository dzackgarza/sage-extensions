from sage_extensions.all import *


def k3():
    return NamedLattices.LK3


def test_the_catalogue_entry_is_three_hyperbolic_planes_and_two_e8() -> None:
    r"""$H^2(X, \mathbb Z) \cong U^{\oplus 3} \oplus E_8^{\oplus 2}$ for a K3 surface $X$ (Barth--Hulek--Peters--Van de Ven, VIII.3)."""
    assert k3().is_isometric(Lattices(ZZ)("U") ^ 3 + Lattices(ZZ)("E8") ^ 2)


def test_the_categories_of_the_k3_lattice() -> None:
    lattice = k3()
    assert lattice in Lattices(ZZ)
    assert lattice in EvenLattices(ZZ)
    assert lattice in NondegenerateLattices(ZZ)


def test_the_invariants_of_the_k3_lattice() -> None:
    lattice = k3()
    assert lattice.module_rank() == 22
    assert lattice.signature_pair() == signature_pair(3, 19)
    assert lattice.is_even()
    assert lattice.is_unimodular()
    assert lattice.determinant() == -1
    assert lattice.discriminant_group().cardinality() == 1
    assert lattice.summands().cardinality() == 5


def test_the_displayed_hyperbolic_plane_splits_off_the_k3_lattice() -> None:
    r"""The displayed first U block is primitive and orthogonal to the remaining rank-20 block."""
    lattice = k3()
    generators = tuple(lattice.module_generators())
    hyperbolic = lattice.subobject_on(generators[:2])
    complement = lattice.subobject_on(generators[2:])

    assert hyperbolic.is_primitive()
    assert hyperbolic.gram_matrix() == Lattices.U.gram_matrix()
    assert complement.module_rank() == 20
    assert complement.signature_pair() == signature_pair(2, 18)
    assert complement.is_unimodular()
    for left in hyperbolic.embedded_module_generators():
        for right in complement.embedded_module_generators():
            assert lattice.b(left, right) == 0


def test_the_k3_lattice_has_one_endomorphism_category() -> None:
    lattice = k3()
    endomorphisms = lattice.Mor(lattice)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert lattice.Mor(lattice) is endomorphisms
    assert identity * identity == identity
