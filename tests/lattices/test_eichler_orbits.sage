r"""Eichler's criterion as a decision about stable orbits of primitive vectors.

Eichler, *Quadratische Formen und orthogonale Gruppen*, Springer 1952,
section 10: on an even lattice splitting two hyperbolic planes, the stable
orthogonal group is transitive on primitive vectors of a given square and a
given divided discriminant class.  The invariants therefore decide an orbit
question about an infinite group with no enumeration.

``U + U + E8(-2)`` is the specimen that separates the invariants.  Its
discriminant group is ``(Z/2)^8`` and each ``E8(-2)`` basis vector has
divisibility two, so two different such vectors share a square and a
divisibility while their divided classes differ.  On a unimodular lattice
every divided class is trivial and the square alone decides.

The hypothesis is read off the presented decomposition, so the K3 lattice
appears here twice: once built as ``U^3 + E8^2``, where the three hyperbolic
planes are summands, and once as the catalogue's ``LK3``, which is presented
by a Gram matrix and therefore answers that it splits nothing.
"""

from sage_extensions.all import *


def _decomposed_k3():
    return NamedLattices.U ** 3 + NamedLattices.E8 ** 2


def _two_elementary_specimen():
    lattice = NamedLattices.U + NamedLattices.U + NamedLattices.E8_2
    return lattice


def test_the_criterion_reads_its_hypothesis_off_the_decomposition() -> None:
    decomposed = _decomposed_k3()
    assert decomposed.indecomposable_summands().cardinality() == 5
    assert decomposed.hyperbolic_plane_summand_count() == 3
    assert decomposed.splits_two_hyperbolic_planes()
    assert decomposed.eichler_criterion_applies()

    # E10 = U + E8 splits one hyperbolic plane, not two.
    assert NamedLattices.E10.hyperbolic_plane_summand_count() == 1
    assert not NamedLattices.E10.splits_two_hyperbolic_planes()
    assert not NamedLattices.E10.eichler_criterion_applies()

    # The catalogue's K3 lattice is isometric to the decomposed one but is
    # presented by a Gram matrix, so no decomposition is readable from it.
    assert NamedLattices.LK3.is_isometric(decomposed)
    assert not NamedLattices.LK3.is_decomposable()
    assert not NamedLattices.LK3.eichler_criterion_applies()


def test_raw_gram_factor_does_not_count_as_a_represented_u_summand() -> None:
    raw_u = Lattices(ZZ)([[2, 1], [1, 0]])
    lattice = raw_u + NamedLattices.U

    assert raw_u.is_isometric(NamedLattices.U)
    assert tuple(lattice.decomposition_names()) == (None, "U")
    assert lattice.hyperbolic_plane_summand_count() == 1
    assert not lattice.splits_two_hyperbolic_planes()


def test_on_a_unimodular_lattice_the_square_decides() -> None:
    lattice = _decomposed_k3()
    first_plane = lattice.module_generator(0) + lattice.module_generator(1)
    second_plane = lattice.module_generator(2) + lattice.module_generator(3)
    opposite = lattice.module_generator(0) - lattice.module_generator(1)

    assert lattice.discriminant_group().cardinality() == 1
    assert first_plane.q() == 2
    assert second_plane.q() == 2
    assert opposite.q() == -2
    assert first_plane.div() == 1
    assert lattice.are_in_one_stable_orbit(first_plane, second_plane)
    assert not lattice.are_in_one_stable_orbit(first_plane, opposite)


def test_the_divided_discriminant_class_separates_two_elementary_vectors() -> None:
    lattice = _two_elementary_specimen()
    assert lattice.eichler_criterion_applies()
    assert lattice.discriminant_group().cardinality() == 256

    first_root = lattice.module_generator(4)
    second_root = lattice.module_generator(5)
    assert first_root.q() == -4
    assert second_root.q() == -4
    assert first_root.div() == 2
    assert second_root.div() == 2
    assert (
        first_root.divided_discriminant_class()
        != second_root.divided_discriminant_class()
    )

    # Same square and divisibility, different divided class: different orbits.
    assert not lattice.are_in_one_stable_orbit(first_root, second_root)
    # Negation preserves all three invariants in a two-group.
    assert lattice.are_in_one_stable_orbit(first_root, -first_root)
    assert first_root != -first_root


def test_the_covering_list_holds_the_class_of_every_primitive_vector() -> None:
    lattice = _two_elementary_specimen()
    root = lattice.module_generator(4)
    covering = lattice.covering_discriminant_classes(root.q())
    divided = root.divided_discriminant_class()

    assert divided in covering
    assert divided.additive_order() == root.div()
    assert lattice.module_generator(5).divided_discriminant_class() in covering
    assert covering.cardinality() < lattice.discriminant_group().cardinality()

    isotropic = lattice.module_generator(0)
    assert isotropic.q() == 0
    assert lattice.discriminant_group().zero() in lattice.covering_discriminant_classes(isotropic.q())

    # An even lattice has no vector of odd square, and no class can cover one:
    # q_{A_L} takes the values q(v)/d^2 of an even lattice, so an odd square
    # would need a denominator the discriminant form does not produce.
    odd = lattice.covering_discriminant_classes(lattice.base_ring().one())
    assert odd.cardinality() == 0


def test_a_vector_with_divisibility_one_has_a_trivial_divided_class() -> None:
    lattice = _two_elementary_specimen()
    isotropic = lattice.module_generator(0)
    assert isotropic.div() == 1
    assert isotropic.divided_discriminant_class() == lattice.discriminant_group().zero()
    assert lattice.are_in_one_stable_orbit(isotropic, lattice.module_generator(2))
