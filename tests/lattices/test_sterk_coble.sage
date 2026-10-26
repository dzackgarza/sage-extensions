from sage_extensions.all import *

_STERK_NORM_COUNTS = {
    "Sterk_1": {-4: 12, -2: 0},
    "Sterk_2": {-4: 9, -2: 1},
    "Sterk_3": {-4: 10, -2: 2},
    "Sterk_4": {-4: 9, -2: 2},
    "Sterk_5": {-4: 10, -2: 4},
}


def test_sterk_configurations_have_the_archived_root_counts_and_norms() -> None:
    configurations = Sterk.sterk_roots()
    assert {name: roots.cardinality() for name, roots in configurations.items()} == {
        "Sterk_1": 12,
        "Sterk_2": 10,
        "Sterk_3": 12,
        "Sterk_4": 11,
        "Sterk_5": 14,
    }
    assert all(root.q() in (-2, -4) for roots in configurations.values() for root in roots)
    assert {name: {norm: sum(root.q() == norm for root in roots) for norm in (-4, -2)} for name, roots in configurations.items()} == _STERK_NORM_COUNTS


def test_sterk_alternative_realizations_reproduce_the_archived_root_data() -> None:
    lattice, sterk_5 = Sterk.sterk5_in_U_E8_2()
    alternatives = Sterk.sterks_in_TEn()

    assert lattice.module_rank() == 10
    assert sterk_5.cardinality() == 14
    assert sum(root.q() == -4 for root in sterk_5) == _STERK_NORM_COUNTS["Sterk_5"][-4]
    assert sum(root.q() == -2 for root in sterk_5) == _STERK_NORM_COUNTS["Sterk_5"][-2]

    assert {name: roots.cardinality() for name, roots in alternatives.items()} == {
        "Sterk_1": 12,
        "Sterk_2": 10,
        "Sterk_3": 12,
    }
    assert all(root.q() in (-2, -4) for roots in alternatives.values() for root in roots)
