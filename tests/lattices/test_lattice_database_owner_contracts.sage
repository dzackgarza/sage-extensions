"""Preamble owner contracts consumed by lattice-database certification.

These are mathematical tests of the preamble objects themselves.  Lattice-db
only serializes the returned values and never rechecks these formulas.
"""

from sage_extensions.all import *


def test_positive_a2_genus_and_orthogonal_group_are_owned_by_the_lattice() -> None:
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])

    assert lattice.conway_sloane_genus_symbol() == "II_{2,0} (2: 1^-2; 3: 1^-1 3^-1)"
    assert lattice.genus_class_number() == 1
    assert lattice.integral_overlattice_inclusions().cardinality() == 1
    group = lattice.orthogonal_group()
    assert group.order() == 12
    for automorphism in group.group_generators():
        for left in lattice.module_generators():
            for right in lattice.module_generators():
                assert lattice.b(left, right) == lattice.b(automorphism(left), automorphism(right))


def test_rational_definite_orthogonal_group_is_owned_by_the_lattice() -> None:
    lattice = Lattices(QQ)([[QQ(1) / 2]])
    group = lattice.orthogonal_group()
    assert group.cardinality() == 2
    assert Set(group.group_generators()).cardinality() == 1


def test_a2_orbit_and_discriminant_certification_data_are_owned_by_the_lattice() -> None:
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])
    one = {"constant": 0, "z": [0, 1, 0, 0], "w": [0, 0, 0, 0]}
    two = {"constant": 0, "z": [0, 2, 0, 0], "w": [0, 0, 0, 0]}
    assert lattice.primitive_orbit_series() == {
        "O": one,
        "SO": one,
        "Otilde": one,
        "SOtilde": two,
        "O+": one,
        "SO+": one,
        "Otilde+": two,
        "SOtilde+": two,
    }
    sequence = lattice.discriminant_sequence_data()
    assert sequence["discriminant_group_order"] == 2
    assert sequence["image_order"] == 2
    assert Set(sequence["coset_representatives"]).cardinality() == 1
    assert sequence["mm_trivial"] is True


def test_discriminant_sequence_retains_a_nontrivial_pointed_coset_quotient() -> None:
    lattice = Lattices(ZZ)([[2, 0], [0, 10]])
    sequence = lattice.discriminant_sequence_data()
    assert sequence["discriminant_factors"] == [2, 10]
    assert sequence["discriminant_group_order"] == 4
    assert sequence["image_order"] == 2
    assert Set(sequence["coset_representatives"]).cardinality() == 2
    assert sequence["mm_trivial"] is False
    assert sequence["quotient_multiplication"] == [[0, 1], [1, 0]]


def test_discriminant_orbit_series_under_the_eichler_hypothesis_is_owned_by_the_lattice() -> None:
    lattice = Lattices(ZZ)(
        [
            [0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, -2],
        ]
    )
    series = {"constant": 1, "z": [0, 1, 0, 1], "w": [0, 2, 0, 1]}
    assert lattice.discriminant_orbit_series() == dict.fromkeys(
        ("O", "SO", "Otilde", "SOtilde", "O+", "SO+", "Otilde+", "SOtilde+"),
        series,
    )


def test_balanced_even_unimodular_lattice_recognizes_its_hyperbolic_plane_power() -> None:
    plane = Lattices(ZZ)("U")
    assert plane.hyperbolic_plane_power_if_even_unimodular() == 1
    assert (plane + plane).hyperbolic_plane_power_if_even_unimodular() == 2
    assert Lattices(ZZ)("E8").hyperbolic_plane_power_if_even_unimodular() is None


def test_integral_hyperbolic_index_is_owned_by_the_lattice() -> None:
    plane = Lattices(ZZ)("U")
    e8 = Lattices(ZZ)("E8")

    assert (plane + plane + e8).integral_hyperbolic_index() == 2
    assert (plane.twist(2) + Lattices(ZZ)([[-2]])).integral_hyperbolic_index() == 0
    assert Lattices(ZZ)([[1, 0], [0, -1]]).integral_hyperbolic_index() == 0
    assert Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, -1]]).integral_hyperbolic_index() == 1


def test_spinor_genus_counts_and_class_numbers_are_owned_by_the_lattice() -> None:
    splag_96 = Lattices(ZZ)([[2, 1, 0], [1, 2, 0], [0, 0, 18]])
    splag_11 = Lattices(ZZ)([[-1, 0, 0], [0, 64, 0], [0, 0, 2]])

    for lattice in (splag_96, splag_11):
        assert lattice.genus_class_number() == 2
        assert lattice.spinor_genus_count() == 2
        assert tuple(lattice.spinor_genus_class_numbers()) == (1, 1)


def test_lattice_isotropy_is_owned_by_the_quadratic_space() -> None:
    assert Lattices(ZZ)("U").is_isotropic()
    assert not Lattices(ZZ)([[1]]).is_isotropic()
    assert Lattices(ZZ)([[0]]).is_isotropic()


def test_root_and_theta_catalogue_invariants_are_owned_by_the_lattice() -> None:
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])
    components = lattice.reflective_root_system_components()
    assert [(component.label(), component.root_scale()) for component in components] == [("G2", 1)]
    theta = lattice.theta_series(precision=5)
    assert tuple(int(theta[index]) for index in range(5)) == (1, 0, 6, 0, 0)
    rank_one = Lattices(ZZ)([[1]]).reflective_root_system_components()
    assert [(component.label(), component.root_scale()) for component in rank_one] == [("A1", QQ(1) / 2)]


def test_affine_quadric_zeta_factorization_is_owned_by_the_lattice() -> None:
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]])
    factorization = lattice.quadratic_hypersurface_zeta_factorization(cone=True)
    assert [(factor.shift, factor.character.coefficient) for factor in factorization.numerator] == [(1, 1), (1, -3)]
    assert [(factor.shift, factor.character.coefficient) for factor in factorization.denominator] == [(0, -3)]
