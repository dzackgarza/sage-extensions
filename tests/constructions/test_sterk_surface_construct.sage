r"""The Sterk catalogue retains its finite root configurations, cusp vectors, and diagrams."""

from sage_extensions.all import *  # noqa: F401,F403


def test_sterk_archived_root_systems_have_expected_sizes_and_root_squares() -> None:
    roots_1820 = Sterk.roots_18_2_0()
    roots_1800 = Sterk.roots_18_0_0()

    assert len(roots_1820) == 22
    assert len(roots_1800) == 19
    assert all(root.q() in (-2, -4) for root in roots_1820.values())
    assert all(root.q() in (-2, -4) for root in roots_1800.values())


def test_sterk_named_root_configurations_and_selected_isotropic_vectors() -> None:
    configurations = Sterk.sterk_roots()
    isotropic = Sterk.selected_isotropic_vectors()

    assert tuple(configurations) == (
        "Sterk_1",
        "Sterk_2",
        "Sterk_3",
        "Sterk_4",
        "Sterk_5",
    )
    assert tuple(int(configurations[name].cardinality()) for name in configurations) == (
        12,
        10,
        12,
        11,
        14,
    )
    assert len(isotropic) == 5
    assert all(vector.q() == 0 for vector in isotropic.values())


def test_sterk_alternative_models_and_diagrams_match_the_named_configurations() -> None:
    lattice, roots = Sterk.sterk5_in_U_E8_2()
    in_ten = Sterk.sterks_in_TEn()
    diagrams = Sterk.diagrams()
    layouts = Sterk.diagram_layouts()
    isotropic = Sterk.isotropic_vectors()

    assert lattice is NamedLattices.U_E8_2
    assert len(roots) == 14
    assert all(root.q() in (-2, -4) for root in roots)
    assert tuple(map(len, in_ten.values())) == (12, 10, 12)
    assert set(diagrams) == set(layouts) == set(Sterk.sterk_roots())
    assert all(
        diagrams[name].cardinality() == Sterk.sterk_roots()[name].cardinality()
        for name in diagrams
    )
    for name, diagram in diagrams.items():
        count = int(diagram.cardinality())
        assert tuple(diagram.index_set()) == tuple(range(count))
        assert tuple(diagram.vertex_names()) == tuple(f"r{index}" for index in range(count))
        assert set(diagram.preferred_positions()) == set(range(count))
        assert tuple(diagram.root(index) for index in range(count)) == Sterk.sterk_roots()[name]
        diagram.validate_positions()
    assert set(isotropic) == {"s4_12"}
    assert isotropic["s4_12"].q() == 0
