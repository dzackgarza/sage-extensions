r"""Finite type A2 has only elliptic induced subdiagrams, organized by automorphism orbits."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_elliptic_subdiagram_poset_contains_every_induced_subdiagram() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])

    assert diagram.elliptic_subdiagram_poset().cardinality() == cardinal(4)
    assert diagram.parabolic_subdiagram_poset().cardinality() == cardinal(0)


def test_a2_subdiagram_orbits_identify_the_two_single_vertex_subdiagrams() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])
    all_orbits = diagram.subdiagram_orbits()
    elliptic_orbits = diagram.elliptic_subdiagram_orbits()

    assert all_orbits.cardinality() == cardinal(3)
    assert elliptic_orbits.cardinality() == cardinal(3)
    assert diagram.subdiagram_orbit_poset(all_orbits).cardinality() == cardinal(3)
    assert diagram.elliptic_subdiagram_orbit_poset().cardinality() == cardinal(3)


def test_a2_has_no_parabolic_or_maximal_parabolic_subdiagrams() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])

    assert diagram.parabolic_subdiagrams().cardinality() == cardinal(0)
    assert diagram.parabolic_subdiagram_orbits().cardinality() == cardinal(0)
    assert diagram.parabolic_subdiagram_orbit_poset().cardinality() == cardinal(0)
    assert diagram.maximal_parabolic_subdiagrams().cardinality() == cardinal(0)


def test_a2_itself_is_the_unique_maximal_elliptic_subdiagram() -> None:
    diagram = CoxeterDiagrams().from_cartan_type(["A", 2])
    maximal = diagram.maximal_elliptic_subdiagrams()

    assert maximal.cardinality() == cardinal(1)
    assert diagram in maximal
