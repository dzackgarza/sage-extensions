r"""The keys of an indexed family are exactly its mathematical index set."""

from sage_extensions.all import *  # noqa: F401,F403


def test_indexed_family_keys_are_its_index_set() -> None:
    family = ADELogPairs(QQ)("E", 6).integral_invariants()

    assert family.keys() is family.index_set()
    assert tuple(family.keys()) == (
        "dimension",
        "volume",
        "normalized_volume",
        "n_integral_points",
        "n_interior_points",
        "n_boundary_points",
    )
